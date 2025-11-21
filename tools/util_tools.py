import railtracks as rt

@rt.function_node
def think_tool(thought: str) -> str:
    """Record an internal thought or reasoning step.

    Args:
        thought (str):
            The internal reasoning, reflection, or note that the agent
            wants to store or express.

    Returns:
        str: A formatted string containing the provided thought.
    """
    return f"Thought: {thought}"
