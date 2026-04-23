from langchain.messages import AnyMessage, SystemMessage,HumanMessage, AIMessage, ToolMessage
import pdfplumber
import json
from config import tools_by_name,model_with_tools,structured_model,model,model_jd,model_gpt_5nano
from typing import Literal
from langgraph.graph import START,END
from stategraph import state
import re


from config import model_with_tools


#llm call for agent parser 1

def agent_parser(state:dict):
  """llm parses the webpagae """
  print("executing agent parser")
  url=state["base_url"]
  jd_json_string=""
  response=model_with_tools.invoke([
        SystemMessage(content=f"""
        Extract the full job description from this URL: {url}. using tools
        You are an expert recruiter. You have been provided with a web_scraper tool. 
        When a URL is provided, you MUST use the tool to fetch the content. Do not tell the user you cannot access URLs; use your tool instead

        If extraction is incomplete, retry using the tool.
        After successfull extraction of JD after using the tool, examine the JD use your knowlegde if its a valid JD or not, if its invalid try it one more time,
        if the tool keep on returning invalid JD, reply only : "bad tool extraction"
        Do not include any explanation, text, or formatting. 
        If you have successfully extracted the JD please include "successful" in the beginning
        and then add the extracted jd
        """)]+ state.get("messages",[]),
        config={"run_name": "agent_parser_pipeline"}
        )
  # messages={[response],
            # "llm_calls": state.get("llm_calls", 0) + 1}
  print("this output is from the agent parser( tool calling ): "+"\n")
  print(response.content)
  if response.tool_calls:
    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
  if "can't access" in response.content or "external URLs" in response.content:
        # Add a correction message to the state to nudge it
        return {
            "messages": [
                response, 
                HumanMessage(content="You actually DO have a web_scraper tool. Please use it for the URL provided.")
            ]
        }
  
#so here it is skipping the if, coz above llm will call tool call
  if "successful" in response.content.lower():
    raw_jd=response.content.lower().replace("successful","",1).strip()
    response_jd=model_jd.invoke([
        SystemMessage(content=
            "Extract structured job description data.\n"
            "Ignore navigation links, images, legal text, and irrelevant sections.\n"
            "Focus only on:\n"
            "- Job title\n"
            "- Company name\n"
            "- Responsibilities\n"
            "- Requirements\n"
            "- Preferred qualifications\n"
            "- Eligibility\n"
            "- About company\n"
            "Return clean structured data."
        ),
        HumanMessage(content=raw_jd)
    ])
    # 1. Strip the "successful" prefix to isolate the JSON string
    jd_json_string = response_jd.model_dump()
    
  return {"messages":[response],
          "llm_calls":state.get("llm_calls", 0) + 1,
          "jd":jd_json_string}



#llm node call for agent to convert base resume to yaml agent 2 
def agent_resume_in_json(state:state):
   resume_text=state["resume_text"]
   response=structured_model.invoke([SystemMessage(content=
                                                   "Extract structured resume data into the provided schema.\n"
        "Follow these rules:\n"
        "- Fill all fields if information is available\n"
        "- Use lists for multiple items\n"
        "- Normalize skill categories (e.g., programming_languages, ai_ml, mlops, cloud)\n"
        "- For projects: use project title as key and include duration + bullet details\n"
        "- Split certifications into name and issuer\n"
        "- Keep text concise and clean (no extra symbols or formatting)\n"
        "DO NOT ADD ANY EXPLANATIONS OR ANYTHING"
        "- Do not hallucinate missing data"),HumanMessage(content=f"Here is the raw resume text: {resume_text} ")])
   print(response)
   content=response
   print("here is the content resume in json: "+"\n",content)
   return {"base_resume":content}



#llm call node for agent resume which writes the resume 3
def agent_resume(state:dict):
  """llm tailors the resume"""
  # print("this is the base resume at the agent resume: "+"\n")
  # print(state["base_resume"])
  response=model_gpt_5nano.invoke([
      SystemMessage(content=
      """You are a Career Strategist. Your task is to HIGHLIGHT relevant skills from a Base Resume to match a Job Description (JD).

STRICT TRUTH CONSTRAINTS:
1. NO HALLUCINATION: Do not invent any degrees, dates, company names, or roles.
2. NO IDENTITY OVERWRITING: If the user is an AI Engineer, they stay an AI Engineer. Do not change their job titles or education.
3. DATA INTEGRITY: Use ONLY the facts provided in the Base Resume. If a skill required by the JD is NOT in the resume, DO NOT add it. Instead, focus on 'Transferable Skills' (e.g., Data Analysis, Automation, Project Management).

TAILORING STRATEGY:
- Adjust the 'Professional Summary' to show how AI/Technical expertise can solve the problems mentioned in the JD.
- Re-order or re-word existing project bullets to emphasize 'Impact' and 'Tools' that overlap with the JD.
- Keep the Technical Skills section honest, but prioritize the ones most relevant to the JD.

OUTPUT:
- Generate ONLY the resume text.
- No introductions or explanations."""),
    HumanMessage(content=f"""
    ### TARGET JOB DESCRIPTION:
    {state['jd']}

    ### BASE RESUME (Source Data):
    {state['base_resume']}

    Please generate the tailored resume now.
    """)
      
  ])
  print("this is at agent resume llm output: "+"\n",response.content)
  
  resume_text = response.content.strip()
  return {"tailored_resume":resume_text,
          "llm_calls":state.get("llm_calls",0)+1,
          "gen_resume_count":state.get("gen_resume_count",0)+1
          }
#agent cv llm call 4
def agent_cv(state:dict):
  """llm writes the cv """
  response=model_gpt_5nano.invoke([SystemMessage(content=f"""
                                              You are a helful intelligent assitant who is expert in writing Motivation letter,
                                              write the motivation letter for this resume {state["tailored_resume"]} , Do not add explanations, only generate Motivation letter""")])
  cv=response.content.strip()
  return {"CV":cv,
          "llm_calls":state.get("llm_calls",0)+1}

async def tool_node(state: dict):
  current_messages = state["messages"]
  new_tool_messages = []
  for tool_call in current_messages[-1].tool_calls:
    print("Type of tool_call:", type(tool_call))
    print("Contents of tool_call:", tool_call)
    tool_to_execute = tools_by_name[tool_call["name"]]
    print("Tool node execution for agent parser : tool called: "+"\n")
    # print(tool_to_execute)
    try:
        observation = await tool_to_execute.ainvoke(tool_call["args"])
        new_tool_messages.append(ToolMessage(content=str(observation), tool_call_id=tool_call["id"]))
    except Exception as e:
        new_tool_messages.append(ToolMessage(content=f"Tool execution failed: {e}", tool_call_id=tool_call["id"]))
        state["bugs_fixes"] = (state.get("bugs_fixes", "") +
                               f"Tool '{tool_call['name']}' failed with args {tool_call['args']}: {e}\n")
  print("Tool Message :" +"\n",new_tool_messages)
  return {"messages": new_tool_messages}




def should_continue(state: state) -> Literal["tool_node","agent_resume_in_json","agent_parser",END]:
    messages = state["messages"]
    last_message = messages[-1]
    if state["llm_calls"]>=5:
      print("llm calls are 5 ending the loop!")
      return END
    if last_message.tool_calls:
      return "tool_node"
    if "successful" in last_message.content.lower():
    #   "messgaes":[]
      return "agent_resume_in_json" 
    return "agent_parser"
