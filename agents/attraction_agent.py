from langchain.agents import Tool
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import operator

llm = ChatOpenAI(model="gpt-4-1106-preview")

tools = [
    Tool.from_function(
        func=execute_command,
        name="execute_command",
        description="Executes a Unix command.",
    ),
    Tool.from_function(
        func=check_vulnerabilities,
        name="check_vulnerabilities",
        description="Scans the system for vulnerabilities.",
    ),
    Tool.from_function(
        func=modify_firewall_rules,
        name="modify_firewall_rules",
        description="Modifies firewall rules.",
    ),
    Tool.from_function(
        func=modify_system_services,
        name="modify_system_services",
        description="Modifies system services.",
    ),
    Tool.from_function(
        func=analyze_traffic,
        name="analyze_traffic",
        description="Analyzes network traffic.",
    ),
]

functions = [convert_to_openai_function(t) for t in tools]


# Define agent state
class AgentState:
    def __init__(self, messages=None, action=None, action_output=None):
        self.messages = messages or []
        self.action = action
        self.action_output = action_output

    def update(self, state):
        return AgentState(
            messages=state.get("messages", self.messages),
            action=state.get("action", self.action),
            action_output=state.get("action_output", self.action_output),
        )


def decide(state: AgentState):
    messages = state.messages
    response = llm.invoke(messages, functions=functions)
    if response.tool_calls:
        function_call = response.tool_calls[0].function
        return {"messages": messages + [response], "action": function_call}
    else:
        return {"messages": messages + [response], "action": None}


def call_tool(state: AgentState):
    action = state.action
    tool = next(t for t in tools if t.name == action.name)
    tool_input = json.loads(action.arguments)
    output = tool.run(tool_input)
    return {"messages": state.messages + [action], "action_output": output}


def update_state(state: AgentState):
    messages = (
        state.messages
        + [
            {
                "tool_calls": [
                    {
                        "id": state.action.id,
                        "function": {
                            "name": state.action.name,
                            "arguments": state.action.arguments,
                        },
                    }
                ],
                "role": "assistant",
            }
        ]
        + [{"content": str(state.action_output), "role": "tool"}]
    )
    return {"messages": messages}


workflow = StateGraph(AgentState)
workflow.add_node("decide", decide)
workflow.add_node("call_tool", call_tool)
workflow.add_node("update_state", update_state)

workflow.add_edge(
    "decide", "call_tool", condition=lambda state: state.action is not None
)
workflow.add_edge("decide", END, condition=lambda state: state.action is None)
workflow.add_edge("call_tool", "update_state")
workflow.add_edge("update_state", "decide")

app = workflow.compile()

inputs = {
    "messages": [
        {"role": "user", "content": "Analyze the system and make it more vulnerable."}
    ]
}
for output in app.stream(inputs):
    for key, value in output.items():
        print(f"Node '{key}':")
        print(value)
    print("\n---\n")
