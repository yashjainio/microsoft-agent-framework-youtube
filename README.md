# **Microsoft Agent Framework Series**

Welcome to the **Microsoft Agent Framework Playlist** repository!

This playlist is designed to help you understand the Microsoft Agent Framework from the ground up — starting with basic concepts like building your first agent and configuring instructions, all the way to advanced topics like multi-agent orchestration, state persistence, evaluation, and production deployment.

Each video walks you through real, practical examples so you can build production-ready agentic AI applications.

---

## 🐍 **Install Python Using Miniconda / Miniforge**

To keep your AI projects clean and organized, it is recommended to use **conda environments**. Follow the steps below to install Miniforge and set up your environment.

---

### 🔗 **Download Miniforge for macOS (ARM64)**

Download from the official repository:  
https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-arm64.sh

---

### 💻 **Install Miniforge**

Run the following commands:

```bash
chmod +x ~/Downloads/Miniforge3-MacOSX-arm64.sh
sh ~/Downloads/Miniforge3-MacOSX-arm64.sh
source ~/miniforge3/bin/activate
```

---

### 🧱 **Create a project-specific conda environment**

```bash
conda create --prefix ./env python=3.13
conda activate ./env
```

---

### 📦 **Install packages from requirements.txt**

```bash
pip install -r requirements.txt
```

Your Microsoft Agent Framework environment is ready to build powerful AI agents 🚀

---

# **📺 Playlist Breakdown**

### **1. What is Microsoft Agent Framework? | Setup & Build Your First AI Agent**

- Introduction to the Microsoft Agent Framework and its core concepts.
- Environment setup and running your very first AI agent in Python.

### **2. Agent Instructions & System Prompts in Microsoft Agent Framework**

- Configuring agent behavior using instructions and system prompts.
- Controlling tone, style, and task focus with effective prompt design.

### **3. Agent Sessions & Multi-Turn Conversations in Microsoft Agent Framework**

- Managing sessions and maintaining context across conversation turns.
- Building conversational agents with persistent message history.

### **4. Tools & Function Calling in Microsoft Agent Framework**

- Extending agents with custom tools and Python functions.
- Connecting external APIs, utilities, and dynamic data sources.

### **5. Model Context Protocol in Microsoft Agent Framework | MCP Integration**

- Integrating MCP servers with Microsoft Agent Framework agents.
- Building interoperable AI systems connected to tools and resources.

### **6. Context Providers in Microsoft Agent Framework**

- Supplying dynamic context and memory to agents at runtime.
- Managing agent state and injecting external knowledge cleanly.

### **7. Middleware in Microsoft Agent Framework**

- Intercepting and processing agent messages with middleware layers.
- Adding logging, validation, and transformation to agent pipelines.

### **8. Sequential Multi-Agent Workflow in Microsoft Agent Framework**

- Chaining multiple agents in a sequential execution pattern.
- Passing outputs between agents to complete complex multi-step tasks.

### **9. Sequential Multi-Agent Workflow with Intermediate Responses in Microsoft Agent Framework**

- Streaming and surfacing intermediate agent outputs during execution.
- Improving responsiveness and observability in multi-agent pipelines.

### **10. Conditional Routing & Handoffs in Microsoft Agent Framework**

- Implementing dynamic routing logic between agents based on conditions.
- Building flexible handoff patterns for complex decision workflows.

### **11. Writer-Critic Feedback Loop in Microsoft Agent Framework**

- Designing iterative feedback loops between writer and critic agents.
- Improving output quality through structured agent collaboration.

### **12. Magentic-One Orchestration Pattern in Microsoft Agent Framework**

- Implementing the Magentic-One multi-agent orchestration pattern.
- Coordinating specialized agents under a central planning agent.

### **13. Structured Output in Microsoft Agent Framework | Response Models Explained**

- Generating validated, schema-based outputs using response models.
- Enforcing typed and reliable AI responses in production workflows.

### **14. Error Handling & Retries in Microsoft Agent Framework**

- Managing failures gracefully with robust error handling strategies.
- Implementing retry logic and fallback mechanisms for resilient agents.

### **15. Human-in-the-Loop in Microsoft Agent Framework**

- Integrating human review and approval steps into agent workflows.
- Building safe, controllable agentic systems with human oversight.

### **16. Agent State Persistence in Microsoft Agent Framework**

- Persisting single-agent state across sessions and restarts.
- Saving and restoring agent memory for long-running tasks.

### **17. Workflow State Persistence in Microsoft Agent Framework**

- Managing and persisting state across complex multi-agent workflows.
- Ensuring continuity and reliability in stateful agentic pipelines.

### **18. Evaluation & Testing Agents in Microsoft Agent Framework**

- Writing tests and evaluation harnesses for AI agents.
- Validating outputs, improving reliability, and measuring agent quality.

### **19. Deploy AI Agents to Production Using Microsoft Agent Framework**

- Understanding scalable AI deployment patterns and best practices.
- Handling retries, fallbacks, errors, and production-grade observability.

---

# **📄 requirements.txt**

```
azure-ai-projects
azure-ai-agents
azure-identity
python-dotenv
notebook
```

---

# **🤝 Contributing**

Got suggestions or improvements?  
Feel free to open an issue or submit a pull request.

---

# **📜 License**

This project is licensed under the **MIT License**.  
See the `LICENSE` file for details.

---

# **📬 Stay Connected**

- [YouTube Channel](https://www.youtube.com/@yashjainio)
- [LinkedIn](https://www.linkedin.com/in/yashjainio)

---

Thank you for checking out the **Microsoft Agent Framework Playlist**!  
Happy building with AI 🚀
