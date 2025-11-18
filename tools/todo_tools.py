from typing import List

import railtracks as rt
from pydantic import BaseModel, Field


class Todo(BaseModel):
    content: str = Field(description="A todo that needs to be done.")
    status: str = Field(description="Status of the todo, in-progress, done, or failed.")

@rt.function_node
def write_todo(todo:List[Todo]):
    """Store a list of Todo items in the railtracks context.

    Each Todo item includes:
        - content (str): A description of the task.
        - status (str): The task status, one of: "in-progress", "done", or "failed".

    Args:
        todo (List[Todo]):
            A list of Todo objects, each containing a task description
            and its current status.

    Returns:
        str: A confirmation message indicating that the Todo list has
        been updated, including the stored items.
    """
    rt.context.put("todo",todo)
    return f"Updated Todo List:{todo}"

@rt.function_node
def read_todo():
    """Retrieve the stored Todo list from the railtracks context.

    Each Todo item includes:
        - content (str): A description of the task.
        - status (str): The task status, one of: "in-progress", "done", or "failed".

    Returns:
        str: A formatted string representing the current stored Todo
        list. If no todos are stored, returns a message indicating
        that none were found.
    """
    todo = rt.context.get("todo",[])
    if todo:
        return f"Current Todo List {todo}"
    else:
        return "No todo found"

