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
def read_write_notes_for_papers_in_a_directory(directory: str):
    """
    Reads the virtual file system (VFS) and prints the names of all papers
    stored in the specified directory.

    This function accesses the Railtracks context's virtual file system (`vfs`)
    to locate a directory of downloaded papers. It iterates through all files
    in that virtual directory and prints their names. This is typically used
    as a preliminary step before reading or writing notes associated with
    each paper.

    Args:
        directory (str): The name of the directory inside the VFS that contains
            the papers to be processed.

    Returns:
        str: A message indicating that all papers in the specified directory
            have been read.

    Raises:
        KeyError: If the directory does not exist within the virtual file
            system structure.
    """
    vfs = rt.context.get("vfs")
    directories = vfs.get("directories")
    virtual_directory = directories.get(directory)
    for file in virtual_directory:
        print(file)
    return f"Finished reading all papers in directory {directory}"


