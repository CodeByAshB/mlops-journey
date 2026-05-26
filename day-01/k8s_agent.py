import ollama
import subprocess

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
    print("\n🔍 Gathering cluster information...\n")
    
    pods = run_command(["kubectl", "get", "pods", "-A"])
    services = run_command(["kubectl", "get", "svc", "-A"])
    nodes = run_command(["kubectl", "get", "nodes"])
    memory = run_command(["free", "-h"])
    
    return {
        "pods": pods,
        "services": services,
        "nodes": nodes,
        "memory": memory
    }

# ============================================
# GET LOGS FOR A SPECIFIC POD
# ============================================
def get_pod_logs(pod_name):
    logs = run_command([
        "kubectl", "logs",
        pod_name,
        "--tail=20"
    ])
    return logs

# ============================================
# ASK AI
# ============================================
def ask_ai(user_question, cluster_info):
    prompt = f"""
You are an expert Kubernetes and DevOps engineer.

STRICT RULES:
- ONLY answer using the EXACT data provided below
- ONLY mention pod names that exist in the PODS section
- If you dont know, say "I can only see X in your cluster"
- NEVER invent example outputs
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

USER QUESTION: {user_question}

Answer clearly and practically.
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
# MAIN LOOP - keep asking questions
# ============================================
def main():
    print("=" * 50)
    print("🤖 K8s AI Agent")
    print("=" * 50)
    print("Commands:")
    print("  'refresh' - refresh cluster info")
    print("  'logs <pod-name>' - get pod logs")
    print("  'quit' - exit")
    print("  anything else - ask AI a question")
    print("=" * 50)

    # gather info once at start
    cluster_info = get_cluster_info()
    print("✅ Cluster info gathered!\n")

    # keep looping until user quits
    while True:
        user_input = input("\n💬 Ask me anything: ").strip()

        if not user_input:
            continue

        elif user_input.lower() == "quit":
            print("👋 Bye!")
            break

        elif user_input.lower() == "refresh":
            cluster_info = get_cluster_info()
            print("✅ Cluster info refreshed!")

        elif user_input.lower().startswith("logs "):
            pod_name = user_input.split(" ", 1)[1]
            print(f"\n📋 Logs for {pod_name}:\n")
            logs = get_pod_logs(pod_name)
            print(logs)

        else:
            print("\n🤖 AI is thinking...\n")
            answer = ask_ai(user_input, cluster_info)
            print("=" * 50)
            print(answer)
            print("=" * 50)

if __name__ == "__main__":
    main()
