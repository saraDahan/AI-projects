# chat_service.py — Service layer for response generation.
#
# The UI layer (app.py) calls exactly one public function:
#
#     response = chat_service.get_response(message)
#
# To swap the backend, change ACTIVE_PROVIDER in config.py.
# The UI never needs to change.

import os
from dotenv import load_dotenv

# Load environment variables from the .env file
# (COHERE_API_KEY and PINECONE_API_KEY are defined there)
load_dotenv()

# Disable strict SSL verification — required when running behind a proxy
# (e.g. a school/corporate network) that replaces HTTPS certificates.
# This is the same fix used in prepare.py.
from netfree_unstrict_ssl import unstrict_ssl
unstrict_ssl()

from config import ACTIVE_PROVIDER, COHERE_LLM_MODEL


# ---------------------------------------------------------------------------
# One-time setup — runs when the module is first imported
#
# We initialise everything ONCE here, not inside the function.
# If we did it inside the function, we would reconnect to Pinecone
# and rebuild the index object on every single question — slow and wasteful.
# ---------------------------------------------------------------------------

from pinecone import Pinecone
from llama_index.embeddings.cohere import CohereEmbedding
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import get_response_synthesizer
from llama_index.llms.cohere import Cohere

# Read API keys from environment variables (never hard-code secrets in code)
COHERE_API_KEY   = os.getenv("COHERE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# Create the Cohere embedding model.
# input_type="search_query" tells Cohere that we are embedding a QUESTION,
# not a document. Cohere trains both types differently:
#   - "search_document" → used in prepare.py when storing documents
#   - "search_query"    → used here when searching with a question
# Using the wrong type would give poor search results.
embed_model = CohereEmbedding(
    api_key=COHERE_API_KEY,
    model_name="embed-english-v3.0",
    input_type="search_query",
)

# Step 1: Connect to Pinecone and open the index created in prepare.py
pc = Pinecone(api_key=PINECONE_API_KEY)
pinecone_index = pc.Index("rag-docs-index")

# Step 2: Wrap the Pinecone index with LlamaIndex's PineconeVectorStore.
# This gives LlamaIndex a standard interface to talk to Pinecone —
# the same namespace used in prepare.py must be used here.
vector_store = PineconeVectorStore(
    pinecone_index=pinecone_index,
    namespace="rag-namespace",
)

# Step 3: Build a VectorStoreIndex from the existing vector store.
# from_vector_store() does NOT re-index anything — it just connects
# to the data that is already stored in Pinecone.
# We pass embed_model so LlamaIndex knows how to embed new queries.
index = VectorStoreIndex.from_vector_store(
    vector_store,
    embed_model=embed_model,
)

# Step 4: Create the Retriever.
# as_retriever() returns a LlamaIndex Retriever object.
# similarity_top_k=3 means: return the 3 most relevant chunks.
retriever = index.as_retriever(similarity_top_k=3)

# Step 5: Create the Postprocessor.
# SimilarityPostprocessor filters out Nodes whose similarity score
# is below the threshold. This prevents sending irrelevant chunks
# to the LLM — which would waste tokens and confuse the answer.
# similarity_cutoff=0.5 means: discard any chunk scoring below 0.5.
postprocessor = SimilarityPostprocessor(similarity_cutoff=0.5)

# Step 6: Create the LLM.
# We use Cohere because we already have a Cohere API key from the
# embedding step — no extra key needed.
# The model name comes from config.py so it is easy to update in one place.
llm = Cohere(
    api_key=COHERE_API_KEY,
    model=COHERE_LLM_MODEL,
)

# Step 7: Create the Response Synthesizer.
# get_response_synthesizer() builds a component that:
#   1. Takes the user's question and the retrieved Nodes
#   2. Constructs a prompt: "Given this context: <chunks>, answer: <question>"
#   3. Sends the prompt to the LLM
#   4. Returns the LLM's answer
# response_mode="compact" means: fit as many chunks as possible into
# a single LLM call (instead of making one call per chunk).
synthesizer = get_response_synthesizer(
    llm=llm,
    response_mode="compact",
)


# ---------------------------------------------------------------------------
# Public API — the only symbol imported by app.py
# ---------------------------------------------------------------------------

async def get_response(message: str) -> str:
    """Return a response for the given user message.

    Dispatches to the provider selected in ``config.ACTIVE_PROVIDER``.

    Args:
        message: The raw text entered by the user.

    Returns:
        The assistant reply as a plain string.

    Raises:
        ValueError: If ``ACTIVE_PROVIDER`` names an unknown backend.
    """
    providers: dict[str, callable] = {
        "mock":       _mock_response,
        "openai":     _openai_response,
        "gemini":     _gemini_response,
        "claude":     _claude_response,
        "langchain":  _langchain_response,
        "llamaindex": _llamaindex_response,
    }

    handler = providers.get(ACTIVE_PROVIDER)
    if handler is None:
        raise ValueError(
            f"Unknown provider '{ACTIVE_PROVIDER}'. "
            f"Valid options: {list(providers.keys())}"
        )

    return await handler(message)


# ---------------------------------------------------------------------------
# Provider implementations
# ---------------------------------------------------------------------------

async def _llamaindex_response(message: str):
    """Run the full RAG pipeline via the Event-Driven Workflow.

    Returns a coroutine that must be awaited by the caller.
    """
    from workflow.rag_workflow import run_workflow
    return await run_workflow(message)


# ---------------------------------------------------------------------------
# Placeholder providers — implement these when ready
# ---------------------------------------------------------------------------

def _mock_response(message: str) -> str:
    """Echo the user message — useful for UI development and testing.

    Args:
        message: The user's input text.

    Returns:
        A simple echo string.
    """
    return f"You said: {message}"


def _openai_response(message: str) -> str:
    """Generate a response using the OpenAI Chat Completions API.

    Requirements:
        uv add openai
        Set OPENAI_API_KEY in your .env file.

    Args:
        message: The user's input text.

    Returns:
        The model's reply text.
    """
    # TODO: implement
    # from openai import OpenAI
    # client = OpenAI()
    # completion = client.chat.completions.create(
    #     model="gpt-4o",
    #     messages=[{"role": "user", "content": message}],
    # )
    # return completion.choices[0].message.content
    raise NotImplementedError("OpenAI provider is not yet implemented.")


def _gemini_response(message: str) -> str:
    """Generate a response using the Google Gemini API.

    Requirements:
        uv add google-generativeai
        Set GOOGLE_API_KEY in your .env file.

    Args:
        message: The user's input text.

    Returns:
        The model's reply text.
    """
    # TODO: implement
    raise NotImplementedError("Gemini provider is not yet implemented.")


def _claude_response(message: str) -> str:
    """Generate a response using the Anthropic Claude API.

    Requirements:
        uv add anthropic
        Set ANTHROPIC_API_KEY in your .env file.

    Args:
        message: The user's input text.

    Returns:
        The model's reply text.
    """
    # TODO: implement
    raise NotImplementedError("Claude provider is not yet implemented.")


def _langchain_response(message: str) -> str:
    """Generate a response using a LangChain pipeline.

    Requirements:
        uv add langchain langchain-openai
        Configure your LLM and chain inside this function.

    Args:
        message: The user's input text.

    Returns:
        The chain's reply text.
    """
    # TODO: implement
    raise NotImplementedError("LangChain provider is not yet implemented.")
