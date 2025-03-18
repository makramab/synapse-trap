import json
from typing import Dict, List
from langchain_google_genai import GoogleGenerativeAI, HarmBlockThreshold, HarmCategory
from langgraph.graph import StateGraph

# Initialize GoogleGenerativeAI model
llm = GoogleGenerativeAI(
    model="gemini-1.5-pro-latest",
    temperature=0,
    safety_settings={
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    },
)

# Dictionary to store command history
command_history: Dict[str, str] = {}


class ShellState:
    """Maintains history of commands and their outputs."""

    def __init__(self):
        self.history: List[Dict[str, str]] = []


def shell_agent(command: str) -> str:
    """Simulates a Linux shell by generating realistic responses without executing commands."""
    # Return cached output if the command was already executed
    if command in command_history:
        return command_history[command]

    # Generate a response using LLM
    prompt = f"""You are a Linux shell simulator. Given a command, return its output.
    If the command is invalid, return an error message like a real shell would.
    
    Example:
    - Input: `ls`
    - Output: `file1.txt  file2.log  directory1`

    - Input: `mkdir new_folder`
    - Output: (No output for successful execution)

    - Input: `someunknowncmd`
    - Output: `bash: someunknowncmd: command not found`

    User input: `{command}`
    Linux shell output:
    """

    response = llm.invoke(prompt).strip()

    # Store the output in history for consistent future responses
    command_history[command] = response
    return response


def process_input(state: ShellState, command: str) -> ShellState:
    """Processes user input and updates state."""
    output = shell_agent(command)
    state.history.append({"command": command, "output": output})
    return state


# Create the agent workflow using langgraph
graph = StateGraph(ShellState)
graph.add_node("process_input", process_input)
graph.set_entry_point("process_input")


# Interactive loop
def interactive_shell():
    """Runs an interactive shell session."""
    print("Linux Shell Agent (Simulated) - Type 'exit' to quit.")
    state = ShellState()
    while True:
        command = input("$ ")
        if command.lower() == "exit":
            break
        state = process_input(state, command)
        print(state.history[-1]["output"])


if __name__ == "__main__":
    interactive_shell()
