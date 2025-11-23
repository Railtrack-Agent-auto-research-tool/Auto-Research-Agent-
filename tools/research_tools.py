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
def read_write_papers_in_a_directory(directory: str):
    vfs = rt.context.get("vfs")
    directories = vfs.get("directories")
    virtual_directory = directories.get(directory)
    for file in virtual_directory:
        print(file)
    return f"Finished reading all papers in directory {directory}"

