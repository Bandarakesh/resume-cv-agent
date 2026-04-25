import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
# from langchain.messages import HumanMessage
from multi_agents import agent_parser,agent_resume_in_json,agent_resume,agent_cv,tool_node,should_continue
from langgraph.graph import StateGraph,START, END
from IPython.display import Image, display
from stategraph import state
import traceback
from fastapi import UploadFile, File, Form
import PyPDF2
import docx
import io
# load_dotenv()


LANGCHAIN_TRACING_V2 = "true"
LANGCHAIN_ENDPOINT = "https://api.smith.langchain.com"
LANGCHAIN_PROJECT= "resume-multi-agent"


app = FastAPI(
    title="AI Agent API",
    description="Production API for Web Automation and Job Application Agents",
    version="1.0.0"
)

# #model intializing
# model=init_chat_model("gpt-4o-mini", temperature=0)
# #tools

# tools=[web_scrapper_tool,resume_text_to_yaml_tool]
# tools_by_name={tool.name:tool for tool in tools}
# model_with_tools=model.bind_tools(tools)

# --- 2. CORS Configuration ---
# This allows your Chrome Extension or a React/Vue frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def extract_text(file_bytes, filename):
    if filename.endswith(".pdf"):
        pdf = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        return "\n".join([p.extract_text() or "" for p in pdf.pages])

    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])

    else:
        return ""
# --- 3. Define Request/Response Schemas ---
class AgentRequest(BaseModel):
    input_text: str
    thread_id: Optional[str] = "default-thread"  # Useful for LangGraph checkpoints
    config: Optional[Dict[str, Any]] = {}

class AgentResponse(BaseModel):
    status: str
    output: Any
    

# --- 4. Initialize  Agent ---

def get_agent():
    
    agent_builder = StateGraph(state)

    # 1. Define all Nodes
    agent_builder.add_node("agent_parser", agent_parser)
    agent_builder.add_node("tool_node", tool_node)
    agent_builder.add_node("agent_resume_in_json", agent_resume_in_json)
    agent_builder.add_node("agent_resume", agent_resume)
    agent_builder.add_node("agent_cv", agent_cv)

    # 2. Define the Entry Point
    agent_builder.add_edge(START, "agent_parser")

    # 3. Parser Logic (Sends data TO the YAML converter)
    agent_builder.add_conditional_edges("agent_parser", should_continue, {
        "tool_node": "tool_node",
        "agent_resume_in_json": "agent_resume_in_json", # Go here next!
        "agent_parser": "agent_parser"
    })
    agent_builder.add_edge("tool_node", "agent_parser")

    agent_builder.add_edge("agent_resume_in_json","agent_resume")

    # 5. Final Handoffs
    agent_builder.add_edge("agent_resume", "agent_cv")
    agent_builder.add_edge("agent_cv", END) # You must tell it where to stop!

    return agent_builder.compile()

agent = get_agent()
# Show the agent
print("this is the multi-agent-graph")
display(Image(agent.get_graph(xray=True).draw_mermaid_png()))
# Save the graph to a file
graph_image = agent.get_graph(xray=True).draw_mermaid_png()

with open("agent_graph.png", "wb") as f:
    f.write(graph_image)

print("Graph saved to agent_graph.png. Open this file to view it.")

# --- 5. Endpoints ---

@app.get("/health")
def health_check():
    """Endpoint for GCP Cloud Run to check if the service is alive."""
    return {"status": "healthy", "service": "ai-agent-api"}

@app.post("/invoke", response_model=AgentResponse)
async def invoke(
    file: UploadFile = File(...),
    job_url: str = Form(...),
    user_prompt:str=Form(None)
):
    try:
        contents = await file.read()

        # ✅ Step 1: extract text
        resume_text = extract_text(contents, file.filename)
        print("Parsed Uploded file: "+"\n", resume_text)

        # ✅ Step 2: pass to graph
        result = await agent.ainvoke({
            "base_url": job_url,
            "resume_text": resume_text,
            "messages": [],
            "llm_calls": 0,
            "gen_resume_count": 0 if not user_prompt else 1
        })

        return {
            "status": "success",
            "output": {
                "jd": result.get("jd",""),
                "tailored_resume": result.get("tailored_resume",""),
                "CV": result.get("CV","")
            }
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- 6. Entry point ---
if __name__ == "__main__":
    import uvicorn
    # This part is used for local testing: python app.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
    # -----------------------------
# if __name__ == "__main__":
#     app.run(port=5000, debug=True)