# retriever_service.py — thin wrapper around the existing retriever.
#
# The Workflow calls get_nodes() instead of calling retriever.retrieve()
# directly, so retrieval logic stays in one place.

from llama_index.core.schema import NodeWithScore
from chat_service import retriever


def get_nodes(question: str, top_k: int = 3) -> list[NodeWithScore]:
    """Run semantic search and return the top matching nodes.

    Args:
        question: The user's question.
        top_k:    How many results to return (overrides the default).

    Returns:
        List of NodeWithScore objects (each has .node.text and .score).
    """
    # Temporarily adjust top_k if a retry requests more results
    retriever.similarity_top_k = top_k
    return retriever.retrieve(question)
