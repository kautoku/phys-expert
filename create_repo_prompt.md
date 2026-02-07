# 1
You are an expert Python developer participating in a hackathon. We are building a "Phys-Agent" backend using the Model Context Protocol (MCP).

Please create a Python module named `physics_knowledge_db.py`.
**Context:** The goal is to estimate lighting direction in images using physics principles.
**Environment:** Linux x86, Python 3.9.

**Requirements:**
1.  **Libraries**: Use `chromadb` for the vector database, `sentence-transformers` for embeddings (use a small, fast model like 'all-MiniLM-L6-v2'), `arxiv` for searching, and `pymupdf` (fitz) for reading PDFs.
2.  **Class Structure**: Create a class `PhysicsKnowledgeBase`.

**Implement the following methods in the class:**
1.  `__init__`: Initialize the ChromaDB client (persistent storage in `./db`) and the embedding model.
2.  `search_arxiv(self, query: str, max_results=5)`: Use the `arxiv` library to find papers. Return a list of metadata (title, pdf_url, summary, paper_id).
3.  `read_paper(self, pdf_url: str)`: Download the PDF from the URL, extract text using `pymupdf`, and chunk the text (e.g., 500 words per chunk). Return a list of text chunks with page numbers.
4.  `crawl_physics_knowledge(self, topic: str)`: This is the main ingestion function.
    * Call `search_arxiv` with the topic.
    * Loop through results: Call `read_paper`.
    * Store chunks in ChromaDB. **Crucial**: Store metadata `{source_id: paper_id, title: title, page: page_num, url: pdf_url}` so we can cite it later.
    * Print status updates (e.g., "Ingesting paper: [Title]...").
5.  `query_physics_db(self, question: str, n_results=3)`: Convert the question to an embedding, query ChromaDB, and return the top matching text chunks along with their metadata (Source ID, Page Number).
6.  `get_reference(self, paper_id: str)`: A helper to retrieve the full title and URL for a given `paper_id` to generate citations.

**Constraint**: Handle exceptions gracefully (e.g., if a PDF fails to download, skip it).


# 2
Now, let's build the MCP server interface. Create a file named `mcp_server.py`.

**Goal**: Expose the `PhysicsKnowledgeBase` methods as MCP tools so the AI Assistant in VS Code can use them.
**Framework**: Use `mcp` (Model Context Protocol) python SDK (or `fastmcp` if you prefer simplicity).

**Instructions:**
1.  **Import**: Import `PhysicsKnowledgeBase` from `physics_knowledge_db`.
2.  **Initialize**: Create an instance of the knowledge base.
3.  **Define MCP Tools**: Create the following tools decorated with `@mcp.tool()`:

    * **Tool 1: `add_knowledge_topic`**
        * **Maps to**: `crawl_physics_knowledge(topic)`
        * **Description**: "Downloads and studies physics papers related to a specific topic (e.g., 'Lambertian Reflectance', 'Shadow Analysis') from ArXiv."

    * **Tool 2: `consult_physics_expert`**
        * **Maps to**: `query_physics_db(question)`
        * **Description**: "Queries the local physics database for specific questions. Returns text snippets with citations. Use this BEFORE answering any physics question."
        * **Output formatting**: Ensure the output includes the text snippet, source title, and page number for verification.

    * **Tool 3: `verify_source`**
        * **Maps to**: `get_reference(paper_id)`
        * **Description**: "Retrieves the full details of a cited paper to verify the agent's claims."

4.  **Main Execution**: Set up the server to run with `uvicorn` or standard interaction loop.

**Important**: Add a docstring to the top of the file explaining that this server acts as a "Physics Researcher Sidecar" for the TSMC CareerHack project.




# 3
Finally, help me configure the environment and VS Code settings.

1.  **requirements.txt**: Generate a list of all libraries used in the previous two steps (e.g., `mcp`, `chromadb`, `arxiv`, `pymupdf`, `sentence-transformers`, `uvicorn`).
2.  **Usage Guide**:
    * Provide the command to run the server locally.
    * Provide the JSON configuration snippet to add this server to the VS Code / Antigravity MCP settings (usually in `.vscode/mcp-settings.json` or equivalent).
    * The config should look like:
        ```json
        "physics-agent": {
            "command": "python",
            "args": ["path/to/mcp_server.py"]
        }
        ```
3.  **Test Script**: Write a small `test_run.py` that manually initializes `PhysicsKnowledgeBase`, runs `crawl_physics_knowledge("photometric stereo")`, and then `query_physics_db("how shadows affect normal estimation")` to prove the logic works without the UI.
