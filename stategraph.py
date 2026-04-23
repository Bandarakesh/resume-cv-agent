from typing import Optional, TypedDict, Annotated,Dict
from langchain.messages import AnyMessage
import operator

#Defining the state graph
class state(TypedDict):
  base_url:str
  resume_text:str
  base_resume:Dict[str,any]
  messages: Annotated[list[AnyMessage],operator.add]
  jd:Optional[str]
  structured_jd:Optional[str]

  tailored_resume:Optional[str]
  CV:Optional[str]
  overleaf_resume:Optional[str]
  overleaf_cv:Optional[str]
  llm_calls:int
  bugs_fixes:Optional[str]