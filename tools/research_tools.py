import railtracks as rt


@rt.function_node
def generate_research_brief(research_brief: str) -> str:
    """Return a formatted research brief.

    Args:
        research_brief (str):
            The text of the research brief to be formatted and returned.

    Returns:
        str: A formatted string that includes the provided research brief.
    """
    rt.context.put("research_brief", research_brief)
    return f"This is the research brief: \n\n {research_brief}"


@rt.function_node
def get_research_brief() -> str:
    """Retrieve the currently stored research brief from the railtracks context.

    Returns:
        str: The stored research brief if one exists. If no research brief
        has been generated, returns a default message indicating its absence.
    """
    return rt.context.get("research_brief", "No research brief generated.")


@rt.function_node
def read_write_notes_for_papers_in_a_directory(directory: str, user_research_brief: str):
    """
    Reads a collection of papers stored in a virtual directory and prepares them
    for note-taking and summarization.

    This function accesses the Railtracks context's virtual file system (VFS) to
    locate a directory containing downloaded research papers. It prints the user's
    research brief for context, then iterates through all files in the directory,
    printing each file name. This serves as the entry point for workflows that
    involve reading papers, generating summaries, and writing structured notes.

    Args:
        directory (str): The name of the virtual directory containing the papers
            that will be reviewed.
        user_research_brief (str): A textual summary of the user's research goals,
            provided to guide the note-taking and summarization process.

    Returns:
        str: A message confirming that all papers in the specified directory have
            been processed for reading and note-generation.

    Raises:
        KeyError: If the directory does not exist in the virtual file system.
    """
    vfs = rt.context.get("vfs")
    print(user_research_brief)
    directories = vfs.get("directories")
    virtual_directory = directories.get(directory)
    for file in virtual_directory:
        print(file)
    return f"Finished reading all papers in directory {directory}"



