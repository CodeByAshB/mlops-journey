# Day 01 — K8s AI Agent 🤖

## What I built
An AI-powered Kubernetes agent that:
- Collects real cluster data (pods, services, nodes, memory)
- Lets you ask questions in plain English
- AI analyses and responds using only real cluster data
- Interactive loop — keep asking questions
- Fetch logs for any pod

## Tech Stack
- Python 3.12
- Ollama (local AI runtime)
- qwen2.5:0.5b (small language model)
- kubectl (Kubernetes CLI)
- EC2 t3.medium (Ubuntu)

## How to run

### 1. Activate venv
source venv/bin/activate

### 2. Run agent
python3 k8s_agent.py

### 3. Commands
- Type any question → AI answers
- 'logs <pod-name>' → get pod logs
- 'refresh' → refresh cluster info
- 'quit' → exit

## Example Questions
- "are my pods healthy?"
- "how many pods are running?"
- "what services do i have?"
- "logs nginx-7854ff8877-wkdmz"

## Lessons Learned
- qwen:latest (3.5GB) crashed — t3.medium only has 2.5GB free RAM
- qwen2.5:0.5b (397MB) works fine
- Small models hallucinate more — need stricter prompts
- Always check model size vs available RAM before running

## Project Structure
day-01/
├── k8s_agent.py      # main agent code
├── requirements.txt  # python dependencies
└── README.md         # this file
