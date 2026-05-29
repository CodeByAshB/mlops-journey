from fastapi import FastAPI
import subprocess
import ollama

# ============================================
# CREATE FASTAPI APP
# ============================================
app = FastAPI(
    title="K8s AI Agent API",
    description="Ask questions about your Kubernetes cluster in plain English",
    version="1.0.0"
)

# ============================================
# HELPER FUNCTION - runs any shell command
# ============================================
def run_command(command):
    result = subprocess.run(
        command,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        return f"Error: {result.stderr}"
    return result.stdout.strip()

# ============================================
# GATHER CLUSTER INFO
# ============================================
def get_cluster_info():
    pods     = run_command(["kubectl", "get", "pods", "-A"])
    services = run_command(["kubectl", "get", "svc",   "-A"])
    nodes    = run_command(["kubectl", "get", "nodes"])
    memory   = run_command(["free", "-h"])

    return {
        "pods":     pods,
        "services": services,
        "nodes":    nodes,
        "memory":   memory
    }

# ============================================
# ASK AI
# ============================================
def ask_ai(question, cluster_info):
    prompt = f"""
You are an expert Kubernetes and DevOps engineer.

STRICT RULES:
- ONLY use the provided cluster information
- ONLY mention pods/services that exist in the data below
- NEVER hallucinate or invent data
- Keep answers SHORT and factual
- NO markdown, NO code blocks, just plain text

CLUSTER INFORMATION:
---
PODS:
{cluster_info['pods']}

SERVICES:
{cluster_info['services']}

NODES:
{cluster_info['nodes']}

MEMORY:
{cluster_info['memory']}
---

USER QUESTION: {question}
"""

    response = ollama.chat(
        model="qwen2.5:0.5b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response["message"]["content"]

# ============================================
# ENDPOINTS
# ============================================

# Endpoint 1 - health check
# just to check if API is alive
@app.get("/health")
def health_check():
    return {"status": "alive", "message": "K8s AI Agent is running!"}

# Endpoint 2 - get raw cluster info
# returns raw kubectl data
@app.get("/cluster")
def get_cluster():
    info = get_cluster_info()
    return {
        "pods":     info["pods"],
        "services": info["services"],
        "nodes":    info["nodes"],
        "memory":   info["memory"]
    }

# Endpoint 3 - ask AI a question
# main endpoint
@app.post("/ask")
def ask_question(question: str):
    cluster_info = get_cluster_info()
    answer = ask_ai(question, cluster_info)
    return {
        "question": question,
        "answer":   answer
    }

# Endpoint 4 - get logs for a pod
@app.get("/logs/{pod_name}")
def get_logs(pod_name: str):
    logs = run_command([
        "kubectl", "logs",
        pod_name,
        "--tail=20"
    ])
    return {
        "pod":  pod_name,
        "logs": logs
    }
