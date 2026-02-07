"""
Physics Researcher Sidecar - MCP Server

This server acts as a "Physics Researcher Sidecar" for the TSMC CareerHack project.
It exposes the PhysicsKnowledgeBase functionality as MCP tools, enabling AI assistants
to search, ingest, and query physics knowledge from ArXiv papers.

The server provides three main capabilities:
1. add_knowledge_topic - Ingest papers on a specific physics topic
2. consult_physics_expert - Query the knowledge base with citations
3. verify_source - Retrieve full paper details for citation verification

Usage:
    python mcp_server.py
    
Or with uvicorn:
    uvicorn mcp_server:app --host 0.0.0.0 --port 8000
"""

from typing import Optional
from mcp.server.fastmcp import FastMCP

from physics_knowledge_db import PhysicsKnowledgeBase


# Initialize the MCP server
mcp = FastMCP("physics-agent")

# Initialize the knowledge base (singleton instance)
print("Initializing Physics Knowledge Base...")
knowledge_base = PhysicsKnowledgeBase(db_path="./db")
print("Physics Knowledge Base ready!")


@mcp.tool()
def add_knowledge_topic(topic: str, max_papers: int = 5) -> str:
    """
    Downloads and studies physics papers related to a specific topic from ArXiv.
    
    Use this tool to expand the knowledge base with papers on topics like:
    - 'Lambertian Reflectance'
    - 'Shadow Analysis'
    - 'Photometric Stereo'
    - 'Light Direction Estimation'
    
    Args:
        topic: The physics topic to search for on ArXiv (e.g., 'Lambertian Reflectance', 'Shadow Analysis')
        max_papers: Maximum number of papers to download and process (default: 5)
    
    Returns:
        A summary of the ingestion process including number of chunks stored.
    """
    try:
        total_chunks = knowledge_base.crawl_physics_knowledge(topic, max_papers=max_papers)
        
        stats = knowledge_base.get_collection_stats()
        
        return (
            f"✅ Successfully ingested papers on topic: '{topic}'\n"
            f"📚 New chunks added: {total_chunks}\n"
            f"📊 Total chunks in database: {stats['total_chunks']}\n\n"
            f"The knowledge base is now updated with the latest research on this topic."
        )
    except Exception as e:
        return f"❌ Error ingesting papers: {str(e)}"


@mcp.tool()
def consult_physics_expert(question: str, n_results: int = 3) -> str:
    """
    Queries the local physics database for specific questions.
    Returns text snippets with citations.
    
    **IMPORTANT**: Use this tool BEFORE answering any physics question to ensure
    your response is grounded in scientific literature.
    
    Args:
        question: The physics question to search for (e.g., 'How do shadows affect normal estimation?')
        n_results: Number of relevant passages to retrieve (default: 3)
    
    Returns:
        Relevant text snippets with source citations (paper title, ID, and page number).
    """
    try:
        results = knowledge_base.query_physics_db(question, n_results=n_results)
        
        if not results:
            return (
                "❌ No relevant information found in the knowledge base.\n"
                "💡 Tip: Use 'add_knowledge_topic' to ingest papers on the relevant topic first."
            )
        
        # Format output with citations
        output_parts = [
            f"🔍 Found {len(results)} relevant passages for: \"{question}\"\n",
            "=" * 60,
            ""
        ]
        
        for i, result in enumerate(results, 1):
            source_id = result.get('source_id', 'Unknown')
            title = result.get('title', 'Unknown Title')
            page = result.get('page', 'N/A')
            text = result.get('text', '')
            distance = result.get('distance', 0)
            
            # Truncate text for readability
            display_text = text[:500] + "..." if len(text) > 500 else text
            
            output_parts.append(f"📖 [{i}] PASSAGE")
            output_parts.append(f"   Source: {title}")
            output_parts.append(f"   Paper ID: {source_id}")
            output_parts.append(f"   Page: {page}")
            output_parts.append(f"   Relevance Score: {1 - distance:.3f}")
            output_parts.append(f"   \n   \"{display_text}\"")
            output_parts.append("-" * 60)
        
        output_parts.append("\n💡 Use 'verify_source' with the Paper ID to get the full citation details.")
        
        return "\n".join(output_parts)
        
    except Exception as e:
        return f"❌ Error querying knowledge base: {str(e)}"


@mcp.tool()
def verify_source(paper_id: str) -> str:
    """
    Retrieves the full details of a cited paper to verify the agent's claims.
    
    Use this tool to get complete citation information for any paper referenced
    in the knowledge base responses.
    
    Args:
        paper_id: The ArXiv paper ID (e.g., '2002.01588v1')
    
    Returns:
        Full paper details including title and URL for verification.
    """
    try:
        reference = knowledge_base.get_reference(paper_id)
        
        if not reference:
            return (
                f"❌ Paper ID '{paper_id}' not found in the knowledge base.\n"
                "💡 Make sure the paper has been ingested using 'add_knowledge_topic'."
            )
        
        title = reference.get('title', 'Unknown')
        url = reference.get('url', 'No URL available')
        
        return (
            f"📄 PAPER REFERENCE\n"
            f"{'=' * 60}\n"
            f"📌 Paper ID: {paper_id}\n"
            f"📚 Title: {title}\n"
            f"🔗 URL: {url}\n"
            f"{'=' * 60}\n\n"
            f"You can access the full paper at the URL above for verification."
        )
        
    except Exception as e:
        return f"❌ Error retrieving reference: {str(e)}"


@mcp.tool()
def get_knowledge_stats() -> str:
    """
    Returns statistics about the current physics knowledge base.
    
    Use this to check how many papers and chunks are currently stored.
    
    Returns:
        Statistics about the knowledge base.
    """
    try:
        stats = knowledge_base.get_collection_stats()
        
        return (
            f"📊 KNOWLEDGE BASE STATISTICS\n"
            f"{'=' * 40}\n"
            f"📚 Total text chunks: {stats.get('total_chunks', 0)}\n"
            f"🗂️  Collection name: {stats.get('collection_name', 'N/A')}\n"
            f"{'=' * 40}"
        )
        
    except Exception as e:
        return f"❌ Error getting stats: {str(e)}"


@mcp.tool()
def critique_current_code_with_paper(current_code_snippet: str, topic_or_paper_id: str) -> str:
    """
    Critiques user code by comparing it against academic paper theory and reference implementations.
    
    This tool bridges theory and practice by:
    1. Retrieving the mathematical/theoretical foundation from papers
    2. Retrieving implementation details from associated GitHub repositories
    3. Comparing the user's code against both sources
    
    Args:
        current_code_snippet: The user's code to critique (Python/PyTorch typically)
        topic_or_paper_id: Either a topic to search for or a specific paper ID
    
    Returns:
        A structured critique with Theory Check, Reference Implementation comparison, 
        and Refactoring Suggestions.
    """
    try:
        output_parts = [
            f"🔬 CODE CRITIQUE REPORT",
            f"{'=' * 60}",
            f"📝 Analyzing code against paper theory and implementations",
            f"🔍 Topic/Paper: {topic_or_paper_id}",
            f"{'=' * 60}\n"
        ]
        
        # Query 1: Get theoretical/mathematical context
        theory_results = knowledge_base.query_physics_db(
            f"{topic_or_paper_id} formula equation mathematical definition loss function",
            n_results=3
        )
        
        # Query 2: Get implementation details (preferentially from GitHub)
        impl_results = knowledge_base.query_physics_db(
            f"{topic_or_paper_id} implementation code python pytorch",
            n_results=3
        )
        
        # Also try to filter for implementation_details type if available
        # (This is a semantic search, so we include keywords that would appear in READMEs)
        
        if not theory_results and not impl_results:
            return (
                f"❌ No relevant information found for '{topic_or_paper_id}'.\n"
                f"💡 Tip: Use 'add_knowledge_topic' to ingest papers on this topic first.\n"
                f"   Example: add_knowledge_topic('{topic_or_paper_id}')"
            )
        
        # === THEORY CHECK SECTION ===
        output_parts.append("📐 THEORY CHECK")
        output_parts.append("-" * 40)
        
        if theory_results:
            output_parts.append("Found theoretical context from papers:\n")
            for i, result in enumerate(theory_results, 1):
                title = result.get('title', 'Unknown')
                source_id = result.get('source_id', 'Unknown')
                page = result.get('page', 'N/A')
                text = result.get('text', '')[:400]  # Truncate for readability
                
                output_parts.append(f"  [{i}] From: {title}")
                output_parts.append(f"      Paper ID: {source_id}, Page: {page}")
                output_parts.append(f"      \"{text}...\"\n")
            
            output_parts.append("  ⚡ Compare your code against these formulas/definitions.")
            output_parts.append("  ⚠️  Check: Are you implementing the math correctly?\n")
        else:
            output_parts.append("  ⚠️ No theoretical context found. Consider ingesting more papers.\n")
        
        # === REFERENCE IMPLEMENTATION SECTION ===
        output_parts.append("\n🔧 REFERENCE IMPLEMENTATION")
        output_parts.append("-" * 40)
        
        impl_with_github = [r for r in impl_results if "GitHub" in r.get('title', '') or 
                           r.get('url', '').startswith('https://github.com')]
        
        if impl_with_github:
            output_parts.append("Found implementation details from GitHub repositories:\n")
            for i, result in enumerate(impl_with_github, 1):
                title = result.get('title', 'Unknown')
                url = result.get('url', '')
                text = result.get('text', '')[:500]
                
                output_parts.append(f"  [{i}] From: {title}")
                output_parts.append(f"      URL: {url}")
                output_parts.append(f"      \"{text}...\"\n")
        elif impl_results:
            output_parts.append("Found implementation context from papers:\n")
            for i, result in enumerate(impl_results[:2], 1):
                title = result.get('title', 'Unknown')
                text = result.get('text', '')[:400]
                output_parts.append(f"  [{i}] From: {title}")
                output_parts.append(f"      \"{text}...\"\n")
        else:
            output_parts.append("  ⚠️ No implementation references found.\n")
        
        # === USER CODE ANALYSIS ===
        output_parts.append("\n📋 YOUR CODE SNIPPET")
        output_parts.append("-" * 40)
        # Show first 500 chars of user code
        code_preview = current_code_snippet[:500]
        if len(current_code_snippet) > 500:
            code_preview += "\n... (truncated)"
        output_parts.append(f"```python\n{code_preview}\n```\n")
        
        # === REFACTORING SUGGESTIONS ===
        output_parts.append("\n💡 REFACTORING SUGGESTIONS")
        output_parts.append("-" * 40)
        output_parts.append("""
Based on the retrieved context, consider checking:

1. **Loss Function**: Does your loss match the paper's equation?
   - Check normalization (mean vs sum)
   - Check coefficient values

2. **Data Preprocessing**: Are you normalizing inputs correctly?
   - Many physics methods expect specific input ranges

3. **Output Scaling**: Is your output in the expected range?
   - Light directions often need normalization

4. **Numerical Stability**: Are you handling edge cases?
   - Division by zero, very small values, etc.

Use 'verify_source' with the Paper ID to access the full paper for detailed verification.
""")
        
        output_parts.append("=" * 60)
        
        return "\n".join(output_parts)
        
    except Exception as e:
        return f"❌ Error during code critique: {str(e)}"


# Main execution
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🚀 Starting Physics Researcher Sidecar MCP Server")
    print("=" * 60)
    print("\nAvailable tools:")
    print("  1. add_knowledge_topic - Ingest papers from ArXiv")
    print("  2. consult_physics_expert - Query the knowledge base")
    print("  3. verify_source - Get full paper citations")
    print("  4. get_knowledge_stats - View database statistics")
    print("  5. critique_current_code_with_paper - Compare code against paper theory")
    print("\n" + "=" * 60 + "\n")
    
    # Run the MCP server using stdio transport (default for VS Code integration)
    mcp.run()
