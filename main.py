from langchain.agents import Tool
from langchain.agents import AgentType, initialize_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from typing import Dict, List, Optional, Sequence, Tuple, Union
import asyncio
import random
import time
from langchain.tools import BaseTool

import nest_asyncio

nest_asyncio.apply()

# Replace with your actual OpenAI API key
OPENAI_API_KEY = "<>"


# Mock Attacker and System Administrator (for POC)
class MockAttacker:
    def __init__(self):
        self.actions = ["probe", "scan", "login", "exploit"]

    def simulate_action(self):
        return random.choice(self.actions)


class MockSystemAdministrator:
    def receive_alert(self, alert_message):
        print(f"System Administrator received alert: {alert_message}")


# Mock Honeynet Agents
class AttractionAgent:
    def send_signal(self):
        print("Attraction Agent: Sending signal (fake open port)")
        return "signal_sent"


class EngagementAgent:
    def __init__(self):
        self.llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)
        self.tools = [
            Tool(
                name="fake_login",
                func=lambda input_text: "Fake login successful",
                description="Use this to simulate a login prompt",
            ),
            Tool(
                name="fake_data",
                func=lambda input_text: "Fake data: sensitive information",
                description="Use this to simulate data retrieval",
            ),
        ]
        self.agent = initialize_agent(
            self.tools,
            self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
        )

    def engage(self, attacker_action):
        print(f"Engagement Agent: Attacker action: {attacker_action}")
        try:
            response = self.agent.run(attacker_action)
            print(f"Engagement Agent: Response: {response}")
            return response
        except Exception as e:
            print(f"Engagement Agent: Error: {e}")
            return "Engagement failed"


class AnalysisAgent:
    def __init__(self):
        self.llm = ChatOpenAI(openai_api_key=OPENAI_API_KEY)

    def analyze(self, interaction_data):
        print("Analysis Agent: Analyzing interaction data")
        try:
            analysis = self.llm.predict(f"Analyze this interaction: {interaction_data}")
            print(f"Analysis Agent: Analysis: {analysis}")
            return analysis
        except Exception as e:
            print(f"Analysis Agent: Error: {e}")
            return "Analysis failed"


class AlertAgent:
    def generate_alert(self, analysis_results):
        print("Alert Agent: Generating alert")
        if (
            "attack" in analysis_results.lower()
            or "exploit" in analysis_results.lower()
        ):
            alert_message = f"Potential attack detected: {analysis_results}"
            print(f"Alert Agent: Alert: {alert_message}")
            return alert_message
        else:
            return None


# LangGraph Nodes (using basic graph functions)
def attraction(state):
    attacker.simulate_action()
    AttractionAgent().send_signal()
    return {"attacker_action": attacker.simulate_action()}


def engagement(state):
    interaction_data = EngagementAgent().engage(state["attacker_action"])
    return {"interaction_data": interaction_data}


def analysis(state):
    analysis_results = AnalysisAgent().analyze(state["interaction_data"])
    return {"analysis_results": analysis_results}


def alert(state):
    alert_message = AlertAgent().generate_alert(state["analysis_results"])
    if alert_message:
        system_admin.receive_alert(alert_message)
    return {"alert": alert_message}


# LangGraph Graph (manual node creation)
def should_alert(state):
    if state.get("alert"):
        return "end"
    else:
        return "engagement"


# Initialization
attacker = MockAttacker()
system_admin = MockSystemAdministrator()

graph = StateGraph(dict)  # Create a graph with a dictionary state.
graph.add_node("attraction", attraction)
graph.add_node("engagement", engagement)
graph.add_node("analysis", analysis)
graph.add_node("alert", alert)

graph.add_conditional_edges("alert", should_alert)
graph.add_edge("attraction", "engagement")
graph.add_edge("engagement", "analysis")
graph.add_edge("analysis", "alert")
graph.set_entry_point("attraction")

chain = graph.compile()

# Execution
inputs = {"attacker_action": None}
for _ in range(5):  # Simulate 5 attack attempts
    result = asyncio.run(chain.ainvoke(inputs))
    time.sleep(1)  # Simulate time between attacks
