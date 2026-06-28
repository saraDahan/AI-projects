# answer_service.py — thin wrapper around the existing synthesizer.
#
# The Workflow calls generate() instead of calling synthesizer.synthesize()
# directly, so answer-generation logic stays in one place.

from llama_index.core.schema import NodeWithScore
from chat_service import synthesizer


def generate(question: str, nodes: list[NodeWithScore]) -> str:
    """Send the question + retrieved nodes to the LLM and return the answer.

    Args:
        question: The original user question.
        nodes:    The filtered nodes to use as context.

    Returns:
        Plain-text answer from the LLM.
    """
    response = synthesizer.synthesize(query=question, nodes=nodes)
    return str(response)
