# events.py — custom events that carry data between Workflow steps.
#
# Rule: each event holds only the data the NEXT step needs.
# Nothing more.

from llama_index.core.workflow import Event
from llama_index.core.schema import NodeWithScore


class QuestionValidatedEvent(Event):
    """Emitted by ValidateQuestionStep when the question passes validation."""
    question: str                        # the cleaned user question


class RetrievedEvent(Event):
    """Emitted by RetrieveStep after fetching nodes from Pinecone."""
    question: str                        # kept so later steps can use it
    retrieved_nodes: list[NodeWithScore] # raw results from the retriever


class HighConfidenceEvent(Event):
    """Emitted by ConfidenceCheckStep when results are good enough."""
    question: str
    retrieved_nodes: list[NodeWithScore]
    confidence_score: float              # average similarity score


class LowConfidenceEvent(Event):
    """Emitted by ConfidenceCheckStep when results are too weak."""
    retrieved_nodes: list[NodeWithScore]
    confidence_score: float
