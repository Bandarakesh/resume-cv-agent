# from langchain.chat_models import init_chat_model
# from tools import web_scrapper_tool, resume_text_to_yaml_tool
# import os
# from dotenv import load_dotenv
# load_dotenv()
# OPENAI_API_KEY=os.getenv("OPEN_API_KEY")

# model=init_chat_model("gpt-4o-mini",temperature=0)
# tools=[web_scrapper_tool,resume_text_to_yaml_tool]
# tools_by_name={tool.name:tool for tool in tools}
# model_with_tools=model.bind_tools(tools)
from langchain.chat_models import init_chat_model
from tools import web_scrapping_tool
import os
from dotenv import load_dotenv
from langchain.messages import HumanMessage
from pydantic import Field
load_dotenv()  
api_key=os.getenv("OPEN_API_KEY")
# print(api_key)
LANGCHAIN_API_KEY=os.getenv("LANGCHAIN_API_KEY")
model=init_chat_model("gpt-4o-mini",api_key=api_key,temperature=0)
tools = [web_scrapping_tool]
tools_by_name = {tool.name: tool for tool in tools}
model_with_tools = model.bind_tools(tools)
# print(tools_by_name)
# tool_call={"name":"web_scrapper_tool"}
# tool_to_execute = tools_by_name[tool_call["name"]]

# print(tool_to_execute)
from pydantic import BaseModel
from typing import List, Dict, Optional


# ---------- Basic Info ----------
class ContactInfo(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class SkillCategory(BaseModel):
    name: str
    skills: List[str] = Field(default_factory=list)


class TechnicalSkills(BaseModel):
    categories: List[SkillCategory] = Field(default_factory=list)


# ---------- Projects ----------
class Project(BaseModel):
    name: str
    duration: Optional[str] = None
    details: List[str] = Field(default_factory=list)


# ---------- Certifications ----------
class Certification(BaseModel):
    name: str = Field(...)  # required
    issuer: Optional[str] = None
    details: Optional[str] = None


# ---------- Education ----------
class Education(BaseModel):
    university: Optional[str] = None
    location: Optional[str] = None
    degree: Optional[str] = None
    duration: Optional[str] = None
    gpa: Optional[str] = None
    coursework: Optional[Dict[str, List[str]]] = None


# ---------- MAIN MODEL ----------
class Resume(BaseModel):
    contact_info: ContactInfo

    professional_summary: Optional[str] = None

    technical_skills: TechnicalSkills

    projects: List[Project] = Field(default_factory=list)

    certifications: List[Certification] = Field(default_factory=list)

    education: List[Education] = Field(default_factory=list)

normal_model=init_chat_model("gpt-4o-mini",api_key=api_key, temperature=0)
structured_model=normal_model.with_structured_output(Resume)

from pydantic import BaseModel
from typing import List, Optional


class JobDescription(BaseModel):
    title: Optional[str]
    company: Optional[str]
    location: Optional[str]

    responsibilities: List[str]
    requirements: List[str]
    preferred_qualifications: List[str]

    about_company: Optional[str]
    eligibility: Optional[str]

model_for_jd=init_chat_model("gpt-4o-mini",api_key=api_key)
model_jd=model_for_jd.with_structured_output(JobDescription)

model_gpt_5nano=init_chat_model("gpt-5.4-nano-2026-03-17",api_key=api_key,temperature=0.1)