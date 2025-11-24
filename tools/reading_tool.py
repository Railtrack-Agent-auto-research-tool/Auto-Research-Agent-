from pypdf import PdfReader
from io import BytesIO
import railtracks as rt
import os
import openai
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import numpy as np
import pickle


@rt.function_node
def get_pdf_bytes_from_vfs(directory, filename):
    vfs = rt.context["vfs"]
    directories = vfs["directories"]
    if directory not in directories:
        raise ValueError(f"Directory {directory} not found in VFS")
    if filename not in directories[directory]:
        raise ValueError(f"File {filename} not found in VFS directory {directory}")
    return directories[directory][filename]  # this should be bytes


@rt.function_node
def extract_paragraphs_from_bytes(pdf_bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    # Split based on double newlines (paragraphs)
    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 50]
    return paragraphs


@rt.function_node
def summarize_paragraph(paragraph, model):
    prompt = f"""
You are an expert note-taker.

Summarize the following paragraph in 2-3 sentences (core idea), 
then write 3-5 bullet-point notes.

Paragraph:
{paragraph}

Format your response as:

Core Idea:
- ...

Notes:
- ...
- ...
- ...
"""
    response = model.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]



@rt.function_node
def process_pdf_file(directory, filename, model):
    pdf_bytes = get_pdf_bytes_from_vfs(directory, filename)
    paragraphs = extract_paragraphs_from_bytes(pdf_bytes)
    results = []

    for i, para in enumerate(paragraphs, 1):
        notes = summarize_paragraph(para, model)
        results.append({
            "paragraph_number": i,
            "paragraph_text": para,
            "notes": notes
        })
    return results


@rt.function_node
def process_pdf_folder(directory, model, save_to_vfs=True):
    vfs = rt.context["vfs"]
    directories = vfs["directories"]
    if directory not in directories:
        raise ValueError(f"Directory {directory} not found in VFS")

    pdf_files = list(directories[directory].keys())
    all_results = {}

    for pdf_file in pdf_files:
        if not pdf_file.lower().endswith(".pdf"):
            continue
        print(f"Processing {pdf_file}...")
        notes = process_pdf_file(directory, pdf_file, model)
        all_results[pdf_file] = notes

        # Optional: save notes back to VFS as a text file
        if save_to_vfs:
            notes_text = ""
            for n in notes:
                notes_text += f"\n--- Paragraph {n['paragraph_number']} ---\n"
                notes_text += n['notes'] + "\n"
            directories[directory][pdf_file + "_notes.txt"] = notes_text.encode("utf-8")

    return all_results






# Initialize embeddings
# embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")
embedding_model = rt.llm.PortKeyLLM(os.getenv("EMBEDDING", "@openai/text-embedding-3-small"))

@rt.function_node
def paragraphs_to_embeddings(paragraphs, vectorstore_path="vectorstore.pkl"):
    """
    Convert a list of paragraphs to embeddings and store in a vector store (FAISS).
    """
    # Create documents
    docs = [Document(page_content=p, metadata={"paragraph_number": i+1}) 
            for i, p in enumerate(paragraphs)]

    # Generate embeddings and create vector store
    texts = [doc.page_content for doc in docs]
    metadatas = [doc.metadata for doc in docs]
    embeddings = embedding_model.embed_documents(texts)

    # FAISS vector store
    try:
        # Try loading existing vectorstore
        with open(vectorstore_path, "rb") as f:
            vectorstore = pickle.load(f)
    except FileNotFoundError:
        vectorstore = FAISS.from_texts(texts, embedding_model, metadatas=metadatas)

    # Add new embeddings
    vectorstore.add_texts(texts, metadatas=metadatas)

    # Save vector store
    with open(vectorstore_path, "wb") as f:
        pickle.dump(vectorstore, f)

    return f"{len(paragraphs)} paragraphs added to vector store."


@rt.function_node
def retrieve_relevant_paragraphs(query, vectorstore_path="vectorstore.pkl", top_k=5):
    """
    Retrieve the top_k relevant paragraphs for a query from the vector store.
    """
    # Load vector store
    with open(vectorstore_path, "rb") as f:
        vectorstore = pickle.load(f)

    results = vectorstore.similarity_search(query, k=top_k)
    # Return list of tuples: (paragraph_text, metadata)
    return [(r.page_content, r.metadata) for r in results]


@rt.function_node
def summarize_retrieved_paragraphs(query, model, vectorstore_path="vectorstore.pkl", top_k=5):
    """
    Retrieve relevant paragraphs for a query and summarize each paragraph.
    """
    retrieved = retrieve_relevant_paragraphs(query, vectorstore_path, top_k)
    summaries = []

    for paragraph, metadata in retrieved:
        prompt = f"""
You are an expert note-taker.

Summarize the following paragraph in 2-3 sentences (core idea), 
then write 3-5 bullet-point notes.

Paragraph:
{paragraph}

Format your response as:

Core Idea:
- ...

Notes:
- ...
- ...
- ...
"""
        response = model.chat.completions.create(
            model="gpt-4.1",
            messages=[{"role": "user", "content": prompt}]
        )
        summaries.append({
            "paragraph_number": metadata.get("paragraph_number"),
            "paragraph_text": paragraph,
            "notes": response.choices[0].message["content"]
        })

    return summaries

