# Phys-Agent Usage Guide

## Overview
The Phys-Agent is a physics research assistant MCP server for the TSMC CareerHack project. It enables AI assistants to search ArXiv, ingest physics papers, and answer questions with citations.

---

## Installation

```bash
# Install all dependencies
pip install -r requirements.txt
```

---

## Running the Server

### Option 1: Direct Execution (stdio mode for VS Code)
```bash
python mcp_server.py
```

### Option 2: Test without MCP
```bash
python test_run.py
```

---

## VS Code / Antigravity MCP Configuration

Add the following to your `.vscode/mcp.json` or MCP settings file:

```json
{
  "servers": {
    "physics-agent": {
      "command": "python",
      "args": ["/home/itzu/phys-expert/mcp_server.py"]
    }
  }
}
```

Or for the Antigravity settings format:

```json
{
  "physics-agent": {
    "command": "python",
    "args": ["/home/itzu/phys-expert/mcp_server.py"]
  }
}
```

---

## Available MCP Tools

| Tool | Description |
|------|-------------|
| `add_knowledge_topic(topic)` | Downloads and studies physics papers from ArXiv on a topic |
| `consult_physics_expert(question)` | Queries the knowledge base with formatted citations |
| `verify_source(paper_id)` | Retrieves full paper details for citation verification |
| `get_knowledge_stats()` | Returns database statistics |

---

## Example Usage in AI Assistant

```
User: How does Lambertian reflectance affect lighting estimation?

AI: [Calls add_knowledge_topic("Lambertian reflectance lighting")]
    [Calls consult_physics_expert("Lambertian reflectance lighting estimation")]
    
    Based on the physics literature, Lambertian reflectance...
    
    Sources:
    [1] Paper Title, Page 5 (arXiv:2xxx.xxxxx)
```

---

## Project Structure

```
phys-expert/
├── physics_knowledge_db.py   # Core knowledge base class
├── mcp_server.py             # MCP server interface
├── test_run.py               # Test script
├── requirements.txt          # Dependencies
├── README.md                 # This file
└── db/                       # ChromaDB persistent storage
```
