# Deep Research Agent Design

## Overview
### Introduction
The aim of this project is to create a deep research agent

### What is different about this from other deep research agent?

Provides the ability to perform research, by downloading the necessary papers and documents.


### Pipeline
1. User provides a user query.
2.  A Research Coordinator looks at the user query and first clarify what the user wants to research.
3. After we get this clarification we generate a Research Brief.
4. After generating the research brief, we ask the user to approve the research brief.
5. After the research brief is approved we develop a research plan.
6. We review the research plan with the user and get their approval.
7. After the research plan is approved, we start collecting relevant papers and articles and dump them in a pdf file in a local repository.
8. Then we get a junior research agent to read each article and web page, highlight important details and note them down.
9. Then we give these to a writer agent to write the paper.
10. Once the paper is written we get the critique agent to look at the final report and critique the report, and see if we missed anything and if possible get the research agent to make additional changes.
11. Finally, after the critique agent we present the final report to the user and ask them if they are satisfied with it or not.

```mermaid
flowchart TD

    %% User
    U[User]

    %% === Research Coordination Layer ===
    subgraph Coordination["Research Coordination Layer"]
        RC[Research Coordinator Agent]
        RB[Research Brief]
        RP[Research Plan]
    end

    %% === Research Execution Layer ===
    subgraph Execution["Research Execution Layer"]
        CS[Collector Agent]
        JRA[Junior Research Agent]
        Notes[Structured Notes]
        PDF[Local PDF Repository]
    end

    %% === Writing & Review Layer ===
    subgraph WritingReview["Writing & Review Layer"]
        WA[Writer Agent]
        Draft[Draft Report]
        CA[Critique Agent]
        FinalReport[Final Report]
    end


    %% === User Flow ===
    U -->|1. Submit Query| RC
    RC -->|2. Request Clarification| U
    U -->|Clarification| RC

    RC -->|3. Generate Research Brief| RB
    RC -->|4. Ask for Brief Approval| U
    U -->|Approve Brief| RC

    RC -->|5. Generate Research Plan| RP
    RC -->|6. Ask for Plan Approval| U
    U -->|Approve Plan| RC


    %% === Research Execution Flow ===
    RC -->|7. Initiate Collection| CS
    CS -->|Download Sources| PDF
    PDF -->|Send Docs| JRA

    JRA -->|8. Read & Extract Highlights| Notes

    %% === Writing Flow ===
    Notes -->|9. Provide Notes| WA
    WA -->|Write Report| Draft
    Draft -->|10. Send for Critique| CA
    CA -->|Review & Improve| FinalReport

    %% === Final Output ===
    FinalReport -->|11. Deliver to User| U
```
```mermaid
sequenceDiagram
    autonumber

    participant U as User
    participant RC as Research Coordinator
    participant PDF as Local PDF Repository
    participant JRA as Junior Research Agent
    participant WA as Writer Agent
    participant CA as Critique Agent

    U ->> RC: 1. Submit research query
    RC ->> U: 2. Ask clarifying questions
    U ->> RC: Provide clarification

    RC ->> U: 3. Send Research Brief for approval
    U ->> RC: Approve Research Brief

    RC ->> U: 4. Send Research Plan for approval
    U ->> RC: Approve Research Plan

    RC ->> PDF: 5. Collect relevant papers & articles
    PDF ->> JRA: Provide documents

    JRA ->> JRA: 6. Read & extract key ideas
    JRA ->> WA: Send structured notes

    WA ->> WA: 7. Write research report
    WA ->> CA: Send draft report

    CA ->> CA: 8. Review & critique
    CA ->> WA: Request improvements (if needed)

    WA ->> U: 9. Present final report
    U ->> WA: Approve or request revisions

```
## TODO
| Task                                                                               | Status |
|------------------------------------------------------------------------------------|--------|
| Create a tool to download papers based on a query                                  | ✅      |
| Create a placeholder tool to generate arxiv query                                  | ✅      |
| Create the arxiv agent                                                             | ✅      |
| Test the arxiv agent                                                               | ✅      |
| Create the research coordinator agent                                              | ✅      |
| Create the Todo tools for the research coordinator agent                           | ✅      |
| Create the generate brief tool                                                     | ✅      |
| Create the Websearch Agent                                                         | ✅      |
| Implement the download code.                                                       | ✅      |
| Create an an agent that goes through the documents and writes notes and summaries  | ❌      |
| Create an agent that takes these summaries and writes these notes.                 | ❌      |
| Create an agent that provides feedback on the report and makes appropriate changes | ❌      |
|                                                                                    |        |
