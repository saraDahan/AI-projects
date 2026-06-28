# app.py — Gradio UI entry point.
#
# Responsibilities of this file:
#   • Build and configure the Gradio Blocks layout.
#   • Wire user events to handler functions.
#   • Launch the server.
#
# This file contains NO business logic.  The only backend call is:
#
#     response = chat_service.get_response(message)

import gradio as gr

import chat_service
from config import (
    APP_DESCRIPTION,
    APP_TITLE,
    MAX_CONTENT_WIDTH,
    TEXTBOX_LABEL,
    TEXTBOX_PLACEHOLDER,
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------

# Centers the interface, caps the content width, and adds responsive polish.
# Dark-mode colours are handled automatically by gr.themes.Soft(); these rules
# only add layout constraints that Gradio doesn't expose through its API.
_CSS = f"""
/* ── Outer wrapper ─────────────────────────────────────────── */
.gradio-container {{
    max-width: {MAX_CONTENT_WIDTH}px !important;
    margin-left:  auto  !important;
    margin-right: auto  !important;
    padding: 1rem !important;
}}

/* ── Chatbot fills ~55% of the viewport height ──────────────── */
#chatbot-window {{
    height: 55vh !important;
    min-height: 200px !important;
}}

/* ── Send button consistent height with the textbox ────────── */
#send-btn {{
    min-height: 46px;
    align-self: flex-end;
}}

/* ── Responsive: full-width buttons on small screens ────────── */
@media (max-width: 600px) {{
    #send-btn, #clear-btn {{
        width: 100% !important;
    }}
}}
"""

# ---------------------------------------------------------------------------
# Event handlers (pure functions — no UI objects referenced inside)
# ---------------------------------------------------------------------------

async def handle_send(
    user_message: str,
    history: list[dict],
) -> tuple[list[dict], list[dict], str]:
    """Process a user message and return updated state, chatbot, and cleared input.

    Calls ``chat_service.get_response`` to obtain the assistant reply, then
    appends both turns to the conversation history.

    Args:
        user_message: Raw text entered by the user.
        history:      Current conversation as a list of
                      ``{"role": str, "content": str}`` dicts.

    Returns:
        A 3-tuple of:
            - updated history (for ``gr.State``)
            - updated history (for ``gr.Chatbot``)
            - empty string (clears the input ``gr.Textbox``)
    """
    if not user_message.strip():
        return history, history, ""

    response: str =await chat_service.get_response(user_message)

    updated: list[dict] = history + [
        {"role": "user",      "content": user_message},
        {"role": "assistant", "content": response},
    ]
    return updated, updated, ""


def handle_clear() -> tuple[list, list, str]:
    """Reset the conversation to an empty state.

    Returns:
        A 3-tuple of empty history (state), empty history (chatbot), and
        empty string (clears the input textbox).
    """
    return [], [], ""


# ---------------------------------------------------------------------------
# UI layout
# ---------------------------------------------------------------------------

with gr.Blocks(title=APP_TITLE) as demo:

    # ── Header ──────────────────────────────────────────────────────────────
    gr.Markdown(f"# {APP_TITLE}")
    gr.Markdown(APP_DESCRIPTION)

    # ── Conversation state (not rendered) ───────────────────────────────────
    chat_history = gr.State(value=[])

    # ── Chat window ─────────────────────────────────────────────────────────
    chatbot = gr.Chatbot(
        value=[],
        show_label=False,
        elem_id="chatbot-window",
        # Height is set via CSS (55vh) so it adapts to any screen size
    )

    # ── Input row ───────────────────────────────────────────────────────────
    with gr.Row(equal_height=True):
        msg_box = gr.Textbox(
            placeholder=TEXTBOX_PLACEHOLDER,
            label=TEXTBOX_LABEL,
            show_label=False,
            scale=9,
            autofocus=True,
            lines=1,
            max_lines=5,
            submit_btn=False,     # we wire our own button below
        )
        send_btn = gr.Button(
            value="Send ➤",
            variant="primary",
            scale=1,
            elem_id="send-btn",
        )

    # ── Clear button ────────────────────────────────────────────────────────
    clear_btn = gr.Button(
        value="🗑️ Clear Chat",
        variant="secondary",
        elem_id="clear-btn",
    )

    # ── Event wiring ────────────────────────────────────────────────────────

    _inputs  = [msg_box, chat_history]
    _outputs = [chat_history, chatbot, msg_box]

    # Enter key inside the textbox
    msg_box.submit(fn=handle_send, inputs=_inputs, outputs=_outputs)

    # Click the Send button
    send_btn.click(fn=handle_send, inputs=_inputs, outputs=_outputs)

    # Click the Clear button
    clear_btn.click(fn=handle_clear, inputs=None, outputs=_outputs)


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Soft(),
        css=_CSS,
    )
