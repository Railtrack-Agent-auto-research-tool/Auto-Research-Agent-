

---

# Deep Research Agent Design

## Overview

### Introduction

The goal of this project is to build a **multi-agent deep research system** capable of:

* Coordinating research tasks
* Generating structured research briefs and plans
* Performing both academic and web-based searches
* Downloading and organizing source material
* Producing structured notes from documents
* Writing and reviewing a final research report

### What makes this system different?

Unlike typical research assistants, this system **automates the entire research pipeline**—from query clarification to final report generation—using a coordinated set of specialized agents and tools.

A core principle of this system is **traceability**.  
Every insight, claim, or conclusion can be traced back to its exact source segment across:

- **Web resources**
- **PDFs**
- **Academic papers**
- **Local documents**

To achieve this, the agents are designed to **highlight important sentences directly inside the source materials**. When an agent identifies a key fact, definition, or citation-worthy statement, it can:

- Automatically locate the sentence in a PDF or extracted text  
- Apply a highlight annotation  
- Record the exact location (page number, bounding box, or text index)  
- Store the highlighted snippet as an evidence pointer for downstream reasoning  

This provides a transparent, audit-ready trail from **final answer → retrieved evidence → source sentence → original document**.

By emphasizing evidence highlighting and traceability, the system enables:

- Higher reliability in generated research outputs  
- Easier verification of claims  
- Structured extraction of evidence for reports, summaries, and knowledge graphs  
- Full reproducibility of the research process

In short, this system is not just an assistant—it is a **traceable, evidence-driven research automation pipeline**, where **important sentences are highlighted directly inside the sources** to ensure accountability and transparency at every step.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a565d429-38ff-4f1b-8a2f-1c8146ca0259" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/822a6b57-838b-4daf-84c8-657c8a9c39f8" />



---

## Pipeline

1. **User provides a query.**
2. **Research Coordinator** checks for ambiguity and asks clarifying questions.
3. Once clarified, it **generates a Research Brief** using the `generate_research_brief` tool.
4. The brief is sent to the user for approval.
5. Once approved, the coordinator creates a **Research Plan**.
6. The Research Plan is reviewed with the user for approval.
7. After approval, the coordinator:

   * Generates arXiv queries using the **Arxiv Agent**
   * Generates search queries using the **Web Search Agent**
   * Executes searches using `execute_search_main` and `execute_web_search_main`
   * Downloads papers (`download_papers`) and articles (`download_articles`)
8. The system reads documents using `read_write_notes_for_papers_in_a_directory` and produces **structured notes**.
9. A **Writing Agent** generates a draft research report based on the notes.
10. A **Critique Agent** evaluates the draft and suggests improvements.
11. The improved **Final Report** is delivered to the user.

---

# Mermaid Diagrams

## **System Architecture Flowchart**

```mermaid
flowchart TD

    %% User
    U[User]

    %% === Coordination Layer ===
    subgraph Coordination["Research Coordination Layer"]
        RC[Research Coordinator Agent]
        RB[Research Brief]
        RP[Research Plan]
    end

    %% === Search and Collection Layer ===
    subgraph SearchLayer["Search & Collection Layer"]
        AA[Arxiv Agent]
        WA[Web Search Agent]
        DL[Download Tools]
        PDF[Local PDF Repository]
        Notes[Structured Notes]
    end

    %% === Writing & Review Layer ===
    subgraph WritingReview["Writing & Review Layer"]
        WR[Writing Agent]
        Draft[Draft Report]
        CR[Critique Agent]
        FinalReport[Final Report]
    end

    %% === User Flow ===
    U -->|1. Submit Query| RC
    RC -->|2. Ask Clarifying Questions| U
    U -->|Clarification| RC

    RC -->|3. Generate Research Brief| RB
    RC -->|4. Request Brief Approval| U
    U -->|Approve Brief| RC

    RC -->|5. Generate Research Plan| RP
    RC -->|6. Request Plan Approval| U
    U -->|Approve Plan| RC

    %% === Search & Collection ===
    RC -->|7a. Create arXiv Query| AA
    RC -->|7b. Create Web Query| WA
    AA -->|Execute arXiv Search| DL
    WA -->|Execute Web Search| DL
    DL -->|Download Docs| PDF
    PDF -->|Send Docs| Notes

    %% === Notes to Writing ===
    Notes -->|Provide Notes| WR
    WR -->|Create Draft| Draft
    Draft -->|Send for Review| CR
    CR -->|Return Final Report| FinalReport

    FinalReport -->|11. Deliver to User| U
```

---

## **Sequence Diagram**

```mermaid
sequenceDiagram
    autonumber

    participant U as User
    participant RC as Research Coordinator
    participant AA as Arxiv Agent
    participant WA as Web Search Agent
    participant PDF as Local PDF Repository
    participant Notes as Notes Generator
    participant WR as Writing Agent
    participant CR as Critique Agent

    U ->> RC: 1. Submit research query
    RC ->> U: 2. Ask clarifying questions
    U ->> RC: Provide clarification

    RC ->> U: 3. Send Research Brief
    U ->> RC: Approve Brief

    RC ->> U: 4. Send Research Plan
    U ->> RC: Approve Plan

    RC ->> AA: Generate arXiv query
    RC ->> WA: Generate web search query

    RC ->> AA: Execute arXiv search
    RC ->> WA: Execute web search

    AA ->> PDF: Provide paper IDs → downloads
    WA ->> PDF: Provide URLs → downloads

    RC ->> PDF: Gather all documents
    PDF ->> Notes: Send files for processing

    Notes ->> WR: Provide structured notes
    WR ->> CR: Send draft report
    CR ->> WR: Request improvements (if needed)

    WR ->> U: Deliver final report
```
## Set up

```shell
pip install -r requirements.txt
python agent.py
```
---

## TODO

| Task                                                                                                                                | Status |
|-------------------------------------------------------------------------------------------------------------------------------------|--------|
| Create a tool to download papers based on a query                                                                                   | ✅      |
| Create a placeholder tool to generate arxiv query                                                                                   | ✅      |
| Create the arxiv agent                                                                                                              | ✅      |
| Test the arxiv agent                                                                                                                | ✅      |
| Create the research coordinator agent                                                                                               | ✅      |
| Create the Todo tools for the research coordinator agent                                                                            | ✅      |
| Create the generate brief tool                                                                                                      | ✅      |
| Create the Websearch Agent                                                                                                          | ✅      |
| Implement the download code.                                                                                                        | ✅      |
| Create an agent that goes through the documents and writes notes                                                                    | ✅      |
| Create an agent that takes these notes and writes the report                                                                        | ✅      |
| Create an agent that critiques and improves the report                                                                              | ✅      |
| Migrate to pdftext to be able to use open source                                                                                    | ❌      |
| Research on better web search tools                                                                                                 | ❌      |
| Research on better way to retrieve information from documents so that it doesn't start highlighting random crap, maybe test docuglean | ❌      |
| Add the capability to search Nature papers, IEEE some promising API's are semantic API and CORE API                                 | ❌      |
| Add Summarization Capability for long conversations                                                                                 | ❌      |
| Add a section in the report that generates mermaid diagram that shows how each problem in the paper relates to sub problems         | ❌      |
| Evaluate the highlights the papers performs - come up with strategies that helps do this                                            | ❌      |
| Decouple Read Notes form write report work on fixing issues                                                                         | ❌      |
| us                                                                                                                                  |        |

---

