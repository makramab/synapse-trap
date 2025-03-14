# synapse-trap

## Project Description

SynapseTrap is a research project aimed at understanding attack vectors through the use of a sophisticated honeynet system. Unlike traditional intrusion detection systems, SynapseTrap focuses on gathering intelligence about attackers by actively engaging and analyzing their behavior. It employs a multi-agent system designed to attract, engage, analyze, and alert, with each agent possessing learning capabilities to adapt to evolving attack patterns.

The primary goal is to gain deep insights into the types of attacks being launched, the attackers' intentions, and their attack patterns, enabling the development of proactive defense strategies. By understanding the attacker's profile (e.g., impulsive vs. calculated), the system can dynamically adjust its engagement tactics to maximize data collection and resource efficiency.

This project leverages honeypots as a cost-effective method for intrusion data collection, providing a valuable alternative to the expensive process of gathering data from live incidents.

## Key Features

* **Multi-Agent System:** Utilizes a network of intelligent agents for attraction, engagement, analysis, and alerting.
* **Adaptive Learning:** Agents learn and adapt their strategies based on attacker behavior.
* **Attack Vector Analysis:** Focuses on understanding the "how" and "why" behind attacks.
* **Dynamic Engagement:** Adjusts engagement tactics based on attacker profiling.
* **Cost-Effective Data Collection:** Employs honeypots for efficient intrusion data gathering.

## Agents

1. **Attraction Agent (Filter):** Creates enticing signals to attract attackers.
2. **Engagement Agent:** Mimics real system behavior to keep attackers engaged.
3. **Analysis Agent:** Analyzes attacker behavior and infers their intentions.
4. **Alert Agent:** Notifies system administrators of potential threats.

## Sequence Diagram

```mermaid
sequenceDiagram
    participant Attacker
    participant Attraction Agent
    participant Engagement Agent
    participant Analysis Agent
    participant Alert Agent

    Attraction Agent->>Attacker: Send Attracting Signal (e.g., open port, fake vulnerability)
    Attacker->>Attraction Agent: (Possible) Initial Probe/Scan
    Attacker->>Engagement Agent: Initiate Connection/Interaction
    Engagement Agent->>Attacker: Mimic Real System Response (e.g., login prompt, fake data)
    Engagement Agent->>Analysis Agent: Send Attacker Interaction Data
    Analysis Agent->>Analysis Agent: Analyze Attacker Behavior
    Analysis Agent->>Alert Agent: Send Analysis Results
    Alert Agent->>Alert Agent: Check for Anomalies/Attacks
    Attacker->>Engagement Agent: Provide Input/Commands
    Engagement Agent->>Attacker: Process Input, Generate Realistic Response
    Engagement Agent->>Analysis Agent: Send Updated Interaction Data
    Analysis Agent->>Analysis Agent: Update Analysis
    Analysis Agent->>Alert Agent: Send Updated Analysis Results
    Alert Agent->>Alert Agent: Check for Anomalies/Attacks
    Attacker->>Engagement Agent: Further Interactions/Exploration
    Engagement Agent->>Attacker: Maintain Illusion of Real System
    Analysis Agent->>Analysis Agent: Continue Real-Time Analysis
    Alert Agent->>Alert Agent: Continue Anomaly Detection
    Alert Agent->>Alert Agent: Generate Alert (if anomaly detected)

