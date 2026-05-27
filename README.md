### Resume-CV-Agent
A stateful, multi-agent orchestration system engineered with **LangGraph** to automate the alignment of career profiles to target job descriptions. The pipeline replaces manual editing with a deterministic, graph-based architecture that handles automated data extraction, experience tailoring, and cover letter generation.

* **Multi-Agent Orchestration:** Designed a sequential **LangGraph** topology that coordinates dedicated agents (JD Parser, Experience Tailorer, Cover Letter Generator) around a centralized, synchronized graph state.
* **Token Cost Optimization:** Implemented a context-compression layer that transforms raw, unformatted job descriptions into a dense **YAML format** before injecting them into the LLM context, minimizing input token overhead during multi-step reasoning cycles.
* **Structured Input/Output:** Enforced rigid Pydantic schemas to extract **structured JSON outputs** from the LLM, ensuring strict data contract compliance across agent state transitions and preventing execution-time parsing errors.
* **Observability & Tracing:** Integrated **LangSmith** across the entire orchestration layer to enable deep **tracing** of agent trajectories, allowing for real-time **observing** of tool-calling execution, prompt performance, and latency bottlenecks.

## Core Architecture

The system splits responsibilities across three specialized agent nodes to isolate context and optimize output accuracy:

1. **Scraping Agent:** Parses unstructured job description text from a URL to isolate core technical stacks, required domain experience, and key team responsibilities.
2. **Agent Resume:** Compares the user's master profile against the extracted job requirements, rewriting accomplishment statements to maximize semantic alignment while strictly preserving factual accuracy.
3. **Agent CV:** Ingests the targeted job requirements and profile context to generate tailored cover letters that map past achievements directly to the employer's explicit needs.

## System Design Principles

- **Task Isolation:** Distinct agent nodes prevent single-prompt context drift and isolate prompt engineering scopes.
- **Contextual Grounding:** Outputs are strictly anchored to the user's source profile data and the extracted job tokens to prevent arbitrary text generation.

## Demo



https://github.com/user-attachments/assets/a0bcf5dd-1c34-4a3c-bc4f-02c697db65ad







