# rag_workflow.py — Event-Driven RAG Workflow (orchestration only).
#
# Flow:
#   StartEvent → validate → retrieve → check_confidence
#                                           ├─(high)→ generate_answer → StopEvent
#                                           └─(low) → retry_retrieve  → generate_answer → StopEvent
#
# This file contains NO retrieval or LLM logic —
# it only decides what happens next based on events.

import asyncio

from llama_index.core.workflow import (
    Workflow, StartEvent, StopEvent, step, Context
)
from llama_index.core.schema import NodeWithScore

from workflow.events import (
    QuestionValidatedEvent,
    RetrievedEvent,
    HighConfidenceEvent,
    LowConfidenceEvent,
)
from services.retriever_service import get_nodes
from services.answer_service import generate

# Confidence threshold: average similarity score must be above this value
CONFIDENCE_THRESHOLD = 0.5
# Maximum number of retries to avoid infinite loops
MAX_RETRIES = 1


class RAGWorkflow(Workflow):
    """Orchestrates the RAG pipeline as an event-driven workflow."""

    # ------------------------------------------------------------------
    @step
    async def validate_question(self, ctx: Context, ev: StartEvent) -> QuestionValidatedEvent:
        """Step 1 — Validate the user's question (no LLM used here)."""
        question: str = getattr(ev, "question", "").strip()
        print(f"\n[Step 1 - validate_question] question='{question}'")

        if not question:
            raise ValueError("Question cannot be empty.")

        await ctx.store.set("question", question)
        await ctx.store.set("retry_count", 0)

        print(f"[Step 1 - validate_question] ✅ valid → QuestionValidatedEvent")
        return QuestionValidatedEvent(question=question)

    # ------------------------------------------------------------------
    @step
    async def retrieve_documents(self, ctx: Context, ev: QuestionValidatedEvent) -> RetrievedEvent:
        """Step 2 — Run semantic search against Pinecone."""
        print(f"\n[Step 2 - retrieve_documents] searching for: '{ev.question}'")

        nodes: list[NodeWithScore] = get_nodes(ev.question, top_k=3)
        await ctx.store.set("retrieved_nodes", nodes)

        print(f"[Step 2 - retrieve_documents] ✅ found {len(nodes)} nodes → RetrievedEvent")
        return RetrievedEvent(question=ev.question, retrieved_nodes=nodes)

    # ------------------------------------------------------------------
    @step
    async def check_confidence(
        self, ctx: Context, ev: RetrievedEvent
    ) -> HighConfidenceEvent | LowConfidenceEvent:
        """Step 3 — Check the quality of retrieved results."""
        nodes = ev.retrieved_nodes

        if not nodes:
            score = 0.0
        else:
            score = sum(n.score for n in nodes if n.score is not None) / len(nodes)

        await ctx.store.set("confidence_score", score)
        print(f"\n[Step 3 - check_confidence] avg score={score:.3f} (threshold={CONFIDENCE_THRESHOLD})")

        if score >= CONFIDENCE_THRESHOLD:
            print(f"[Step 3 - check_confidence] ✅ high confidence → HighConfidenceEvent")
            return HighConfidenceEvent(
                question=ev.question,
                retrieved_nodes=nodes,
                confidence_score=score,
            )
        else:
            print(f"[Step 3 - check_confidence] ⚠️  low confidence → LowConfidenceEvent")
            return LowConfidenceEvent(
                retrieved_nodes=nodes,
                confidence_score=score,
            )

    # ------------------------------------------------------------------
    @step
    async def retry_retrieve(self, ctx: Context, ev: LowConfidenceEvent) -> HighConfidenceEvent | StopEvent:
        """Step 4a — Retry retrieval with a broader search (low confidence path)."""
        retry_count: int = await ctx.store.get("retry_count", default=0)
        print(f"\n[Step 4a - retry_retrieve] retry_count={retry_count}")

        if retry_count >= MAX_RETRIES:
            print(f"[Step 4a - retry_retrieve] ❌ max retries reached → StopEvent")
            return StopEvent(
                result="I could not find confident results for your question. "
                       "Please try rephrasing."
            )

        await ctx.store.set("retry_count", retry_count + 1)
        question: str = await ctx.store.get("question")

        # Broaden the search by requesting more results
        nodes: list[NodeWithScore] = get_nodes(question, top_k=6)
        await ctx.store.set("retrieved_nodes", nodes)

        score = (
            sum(n.score for n in nodes if n.score is not None) / len(nodes)
            if nodes else 0.0
        )
        await ctx.store.set("confidence_score", score)

        print(f"[Step 4a - retry_retrieve] ✅ retry done, new score={score:.3f} → HighConfidenceEvent")
        return HighConfidenceEvent(
            question=question,
            retrieved_nodes=nodes,
            confidence_score=score,
        )

    # ------------------------------------------------------------------
    @step
    async def generate_answer(self, ctx: Context, ev: HighConfidenceEvent) -> StopEvent:
        """Step 4b — Generate a final answer using the LLM."""
        print(f"\n[Step 4b - generate_answer] sending {len(ev.retrieved_nodes)} nodes to LLM...")

        answer: str = generate(ev.question, ev.retrieved_nodes)
        await ctx.store.set("final_answer", answer)

        print(f"[Step 4b - generate_answer] ✅ answer generated → StopEvent")
        return StopEvent(result=answer)


# Workflow entry point used by the Gradio chat interface.

async def run_workflow(question: str) -> str:
    workflow = RAGWorkflow(timeout=60)

    result = await workflow.run(question=question)

    return result