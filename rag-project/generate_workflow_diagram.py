# generate_workflow_diagram.py
#
# Creates a standalone HTML file that visualises the RAGWorkflow.
# Run with:  uv run generate_workflow_diagram.py
#
# Does NOT import or modify any workflow logic.

OUTPUT_FILE = "rag_workflow.html"

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>RAG Workflow Diagram</title>
  <style>
    body {
      font-family: 'Segoe UI', sans-serif;
      background: #f4f6f9;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 40px 20px;
    }
    h1 { color: #2c3e50; margin-bottom: 8px; }
    p  { color: #7f8c8d; margin-bottom: 40px; }

    .flow {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0;
    }

    /* ── Node styles ── */
    .node {
      padding: 10px 28px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 14px;
      text-align: center;
      min-width: 200px;
    }
    .event  { background: #d6eaf8; border: 2px solid #2980b9; color: #1a5276; }
    .step   { background: #d5f5e3; border: 2px solid #27ae60; color: #1e8449; }
    .stop   { background: #fadbd8; border: 2px solid #e74c3c; color: #922b21; }
    .start  { background: #fdebd0; border: 2px solid #e67e22; color: #784212; }

    /* ── Arrows ── */
    .arrow {
      width: 2px;
      height: 28px;
      background: #95a5a6;
      position: relative;
    }
    .arrow::after {
      content: '▼';
      position: absolute;
      bottom: -14px;
      left: 50%;
      transform: translateX(-50%);
      color: #95a5a6;
      font-size: 12px;
    }

    /* ── Branch ── */
    .branch-container {
      display: flex;
      flex-direction: column;
      align-items: center;
      width: 100%;
    }
    .branch-label {
      font-size: 12px;
      color: #7f8c8d;
      font-style: italic;
      margin: 4px 0 2px;
    }
    .branch-row {
      display: flex;
      gap: 60px;
      align-items: flex-start;
      justify-content: center;
    }
    .branch-arm {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 0;
    }
    .branch-title {
      font-size: 11px;
      font-weight: 700;
      margin-bottom: 6px;
      padding: 3px 10px;
      border-radius: 4px;
    }
    .high { background: #d5f5e3; color: #1e8449; }
    .low  { background: #fdebd0; color: #784212; }

    /* ── Horizontal connector ── */
    .h-line {
      height: 2px;
      background: #95a5a6;
      width: 260px;
      margin: 0 auto;
    }
    .connector-row {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
    }
    .v-left, .v-right {
      width: 2px;
      height: 20px;
      background: #95a5a6;
    }
    .spacer { flex: 1; }
  </style>
</head>
<body>
  <h1>🔄 RAG Workflow Diagram</h1>
  <p>Event-Driven Pipeline — LlamaIndex Workflow</p>

  <div class="flow">

    <!-- START -->
    <div class="node start">StartEvent<br/><small>question</small></div>
    <div class="arrow"></div>
    <div style="height:14px"></div>

    <!-- Step 1 -->
    <div class="node step">validate_question</div>
    <div class="arrow"></div>
    <div style="height:14px"></div>

    <div class="node event">QuestionValidatedEvent<br/><small>question</small></div>
    <div class="arrow"></div>
    <div style="height:14px"></div>

    <!-- Step 2 -->
    <div class="node step">retrieve_documents</div>
    <div class="arrow"></div>
    <div style="height:14px"></div>

    <div class="node event">RetrievedEvent<br/><small>question, retrieved_nodes</small></div>
    <div class="arrow"></div>
    <div style="height:14px"></div>

    <!-- Step 3 -->
    <div class="node step">check_confidence</div>

    <!-- Branch split -->
    <div style="height:20px; width:2px; background:#95a5a6; margin:0 auto;"></div>
    <div class="h-line"></div>

    <div class="branch-row">

      <!-- HIGH confidence arm -->
      <div class="branch-arm">
        <div class="v-left"></div>
        <div class="node event" style="min-width:160px">HighConfidenceEvent<br/><small>question, nodes, score</small></div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node step" style="min-width:160px">generate_answer</div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node stop" style="min-width:160px">StopEvent<br/><small>result = answer</small></div>
      </div>

      <!-- LOW confidence arm -->
      <div class="branch-arm">
        <div class="v-right"></div>
        <div class="node event" style="min-width:160px; background:#fdebd0; border-color:#e67e22; color:#784212">
          LowConfidenceEvent<br/><small>nodes, score</small>
        </div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node step" style="min-width:160px">retry_retrieve</div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node event" style="min-width:160px">HighConfidenceEvent<br/><small>(best effort)</small></div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node step" style="min-width:160px">generate_answer</div>
        <div class="arrow"></div>
        <div style="height:14px"></div>
        <div class="node stop" style="min-width:160px">StopEvent<br/><small>result = answer</small></div>
      </div>

    </div>
  </div>

</body>
</html>
"""


def main() -> None:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(HTML)
    print(f"Workflow diagram created: {OUTPUT_FILE}")
    print(f"Open it in your browser.")


if __name__ == "__main__":
    main()
