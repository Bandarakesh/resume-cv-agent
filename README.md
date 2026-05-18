# resume-cv-agent

A multi-agent orchestration system designed to ingest job descriptions and systematically align career profiles to target roles. This project replaces manual profile updates with a stateful, component-driven pipeline that handles data extraction, experience tailoring, and cover letter generation.

## Core Architecture

The system splits responsibilities across three specialized agent nodes to isolate context and optimize output accuracy:

1. **Scraping Agent:** Parses unstructured job description text from a URL to isolate core technical stacks, required domain experience, and key team responsibilities.
2. **Agent Resume:** Compares the user's master profile against the extracted job requirements, rewriting accomplishment statements to maximize semantic alignment while strictly preserving factual accuracy.
3. **Agent CV:** Ingests the targeted job requirements and profile context to generate tailored cover letters that map past achievements directly to the employer's explicit needs.

## System Design Principles

- **Task Isolation:** Distinct agent nodes prevent single-prompt context drift and isolate prompt engineering scopes.
- **Contextual Grounding:** Outputs are strictly anchored to the user's source profile data and the extracted job tokens to prevent arbitrary text generation.

##Demo


https://github.com/user-attachments/assets/53b129f5-ec8d-4dda-861f-c9ff755fdb32





