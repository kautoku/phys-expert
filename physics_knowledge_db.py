"""
Physics Knowledge Base Module

A module for ingesting, storing, and querying physics knowledge from ArXiv papers
using ChromaDB for vector storage and sentence-transformers for embeddings.
"""

import os
import re
import tempfile
import requests
from typing import List, Dict, Any, Optional

import arxiv
import chromadb
import fitz  # pymupdf
from sentence_transformers import SentenceTransformer

# Regex pattern for GitHub repository URLs
GITHUB_PATTERN = re.compile(r'https://github\.com/[\w\-]+/[\w\-]+')


class PhysicsKnowledgeBase:
    """
    A knowledge base for physics papers that supports:
    - Searching ArXiv for relevant papers
    - Extracting and chunking text from PDFs
    - Storing embeddings in ChromaDB for semantic search
    - Querying the knowledge base with citations
    """

    def __init__(self, db_path: str = "./db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the PhysicsKnowledgeBase.

        Args:
            db_path: Path for persistent ChromaDB storage.
            model_name: Name of the sentence-transformer model to use.
        """
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get or create the collection for physics papers
        self.collection = self.client.get_or_create_collection(
            name="physics_papers",
            metadata={"description": "Physics papers from ArXiv"}
        )
        
        # Initialize the embedding model
        print(f"Loading embedding model: {model_name}...")
        self.embedding_model = SentenceTransformer(model_name)
        print("Embedding model loaded successfully.")
        
        # Store paper metadata for reference lookup
        self._paper_metadata: Dict[str, Dict[str, str]] = {}

    def search_arxiv(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """
        Search ArXiv for papers matching the query.

        Args:
            query: Search query string.
            max_results: Maximum number of results to return.

        Returns:
            List of dictionaries containing paper metadata:
            {title, pdf_url, summary, paper_id}
        """
        results = []
        
        try:
            # Create ArXiv search client
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance
            )
            
            # Fetch results
            client = arxiv.Client()
            for paper in client.results(search):
                # Extract GitHub URL from abstract if present
                github_match = GITHUB_PATTERN.search(paper.summary)
                repo_url = github_match.group(0) if github_match else None
                
                paper_metadata = {
                    "title": paper.title,
                    "pdf_url": paper.pdf_url,
                    "summary": paper.summary,
                    "paper_id": paper.get_short_id(),
                    "repo_url": repo_url
                }
                results.append(paper_metadata)
                
                # Cache metadata for later reference
                self._paper_metadata[paper.get_short_id()] = {
                    "title": paper.title,
                    "url": paper.pdf_url,
                    "summary": paper.summary,
                    "repo_url": repo_url
                }
                
                if repo_url:
                    print(f"  📦 Found GitHub repo: {repo_url}")
                
            print(f"Found {len(results)} papers for query: '{query}'")
            
        except Exception as e:
            print(f"Error searching ArXiv: {e}")
        
        return results

    def read_paper(self, pdf_url: str, chunk_size: int = 500) -> List[Dict[str, Any]]:
        """
        Download and extract text from a PDF, chunking it into smaller pieces.

        Args:
            pdf_url: URL to the PDF file.
            chunk_size: Approximate number of words per chunk.

        Returns:
            List of dictionaries containing:
            {text, page_number}
        """
        chunks = []
        
        try:
            # Download PDF to a temporary file
            print(f"  Downloading PDF from: {pdf_url}")
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            # Write to temporary file
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                tmp_file.write(response.content)
                tmp_path = tmp_file.name
            
            try:
                # Open PDF with pymupdf
                doc = fitz.open(tmp_path)
                
                # Extract text from each page
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text()
                    
                    if text.strip():
                        # Split text into chunks by words
                        words = text.split()
                        
                        for i in range(0, len(words), chunk_size):
                            chunk_words = words[i:i + chunk_size]
                            chunk_text = " ".join(chunk_words)
                            
                            if chunk_text.strip():
                                chunks.append({
                                    "text": chunk_text,
                                    "page_number": page_num + 1  # 1-indexed
                                })
                
                doc.close()
                print(f"  Extracted {len(chunks)} chunks from {len(doc)} pages")
                
            finally:
                # Clean up temporary file
                os.unlink(tmp_path)
                
        except requests.RequestException as e:
            print(f"  Error downloading PDF: {e}")
        except fitz.FileDataError as e:
            print(f"  Error reading PDF: {e}")
        except Exception as e:
            print(f"  Unexpected error processing PDF: {e}")
        
        return chunks

    def fetch_github_context(self, repo_url: str) -> Dict[str, str]:
        """
        Fetch README.md and requirements.txt from a GitHub repository.

        Args:
            repo_url: GitHub repository URL (e.g., https://github.com/user/repo)

        Returns:
            Dictionary with {readme: str, requirements: str} content.
        """
        context = {"readme": "", "requirements": ""}
        
        if not repo_url:
            return context
        
        # Convert github.com URL to raw.githubusercontent.com
        # https://github.com/user/repo -> https://raw.githubusercontent.com/user/repo/main/
        try:
            # Extract user/repo from URL
            parts = repo_url.replace("https://github.com/", "").split("/")
            if len(parts) < 2:
                return context
            
            user, repo = parts[0], parts[1]
            raw_base = f"https://raw.githubusercontent.com/{user}/{repo}"
            
            # Try to fetch README.md (try main branch first, then master)
            readme_fetched = False
            for branch in ["main", "master"]:
                readme_url = f"{raw_base}/{branch}/README.md"
                try:
                    response = requests.get(readme_url, timeout=15)
                    if response.status_code == 200:
                        context["readme"] = response.text
                        readme_fetched = True
                        print(f"  📖 Fetched README.md from {branch} branch")
                        
                        # Also try requirements.txt from same branch
                        req_url = f"{raw_base}/{branch}/requirements.txt"
                        try:
                            req_response = requests.get(req_url, timeout=10)
                            if req_response.status_code == 200:
                                context["requirements"] = req_response.text
                                print(f"  📦 Fetched requirements.txt")
                        except requests.RequestException:
                            pass
                        
                        break
                except requests.RequestException:
                    continue
            
            if not readme_fetched:
                print(f"  ⚠️ Could not fetch README.md from {repo_url}")
                
        except Exception as e:
            print(f"  ❌ Error fetching GitHub context: {e}")
        
        return context

    def crawl_physics_knowledge(self, topic: str, max_papers: int = 5) -> int:
        """
        Main ingestion function: search ArXiv, download papers, and store in ChromaDB.
        Also fetches GitHub implementation details if available.

        Args:
            topic: Topic to search for on ArXiv.
            max_papers: Maximum number of papers to process.

        Returns:
            Total number of chunks ingested.
        """
        print(f"\n{'='*60}")
        print(f"Starting knowledge crawl for topic: '{topic}'")
        print(f"{'='*60}\n")
        
        total_chunks = 0
        
        # Search ArXiv for papers
        papers = self.search_arxiv(query=topic, max_results=max_papers)
        
        if not papers:
            print("No papers found. Crawl complete.")
            return 0
        
        # Process each paper
        for idx, paper in enumerate(papers, 1):
            paper_id = paper["paper_id"]
            title = paper["title"]
            pdf_url = paper["pdf_url"]
            repo_url = paper.get("repo_url")
            
            print(f"\n[{idx}/{len(papers)}] Ingesting paper: {title}")
            print(f"  Paper ID: {paper_id}")
            
            # Read and chunk the paper
            chunks = self.read_paper(pdf_url)
            
            if not chunks:
                print(f"  Skipping paper (no chunks extracted)")
                continue
            
            # Prepare data for ChromaDB - Paper content
            documents = []
            metadatas = []
            ids = []
            
            for chunk_idx, chunk in enumerate(chunks):
                # Generate unique ID for each chunk
                chunk_id = f"{paper_id}_chunk_{chunk_idx}"
                
                documents.append(chunk["text"])
                metadatas.append({
                    "source_id": paper_id,
                    "title": title,
                    "page": chunk["page_number"],
                    "url": pdf_url,
                    "type": "paper_content"
                })
                ids.append(chunk_id)
            
            # Generate embeddings for paper content
            print(f"  Generating embeddings for {len(documents)} paper chunks...")
            embeddings = self.embedding_model.encode(documents).tolist()
            
            # Store paper content in ChromaDB
            try:
                self.collection.upsert(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                total_chunks += len(documents)
                print(f"  ✅ Stored {len(documents)} paper chunks")
                
            except Exception as e:
                print(f"  Error storing chunks in ChromaDB: {e}")
            
            # Fetch and store GitHub implementation details if available
            if repo_url:
                print(f"  🔗 Fetching GitHub implementation details...")
                github_context = self.fetch_github_context(repo_url)
                
                github_documents = []
                github_metadatas = []
                github_ids = []
                
                # Process README content
                if github_context["readme"]:
                    # Chunk the README (500 words per chunk)
                    readme_words = github_context["readme"].split()
                    chunk_size = 500
                    
                    for i in range(0, len(readme_words), chunk_size):
                        chunk_words = readme_words[i:i + chunk_size]
                        chunk_text = " ".join(chunk_words)
                        
                        if chunk_text.strip():
                            github_documents.append(chunk_text)
                            github_metadatas.append({
                                "source_id": paper_id,
                                "title": f"{title} - GitHub README",
                                "page": 0,
                                "url": repo_url,
                                "type": "implementation_details"
                            })
                            github_ids.append(f"{paper_id}_github_readme_{i // chunk_size}")
                
                # Process requirements.txt
                if github_context["requirements"]:
                    github_documents.append(f"Dependencies and requirements: {github_context['requirements']}")
                    github_metadatas.append({
                        "source_id": paper_id,
                        "title": f"{title} - Dependencies",
                        "page": 0,
                        "url": repo_url,
                        "type": "implementation_details"
                    })
                    github_ids.append(f"{paper_id}_github_requirements")
                
                # Store GitHub content if we have any
                if github_documents:
                    print(f"  Generating embeddings for {len(github_documents)} GitHub chunks...")
                    github_embeddings = self.embedding_model.encode(github_documents).tolist()
                    
                    try:
                        self.collection.upsert(
                            ids=github_ids,
                            documents=github_documents,
                            embeddings=github_embeddings,
                            metadatas=github_metadatas
                        )
                        total_chunks += len(github_documents)
                        print(f"  ✅ Stored {len(github_documents)} implementation chunks")
                        
                    except Exception as e:
                        print(f"  Error storing GitHub chunks: {e}")
        
        print(f"\n{'='*60}")
        print(f"Crawl complete! Total chunks ingested: {total_chunks}")
        print(f"{'='*60}\n")
        
        return total_chunks

    def query_physics_db(self, question: str, n_results: int = 3) -> List[Dict[str, Any]]:
        """
        Query the knowledge base for relevant information.

        Args:
            question: The question to search for.
            n_results: Number of results to return.

        Returns:
            List of dictionaries containing:
            {text, source_id, title, page, url, distance}
        """
        results = []
        
        try:
            # Generate embedding for the question
            question_embedding = self.embedding_model.encode([question]).tolist()
            
            # Query ChromaDB
            query_results = self.collection.query(
                query_embeddings=question_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            if query_results and query_results["documents"]:
                documents = query_results["documents"][0]
                metadatas = query_results["metadatas"][0]
                distances = query_results["distances"][0]
                
                for doc, meta, dist in zip(documents, metadatas, distances):
                    results.append({
                        "text": doc,
                        "source_id": meta.get("source_id", "Unknown"),
                        "title": meta.get("title", "Unknown"),
                        "page": meta.get("page", 0),
                        "url": meta.get("url", ""),
                        "distance": dist
                    })
            
            print(f"Found {len(results)} relevant chunks for: '{question}'")
            
        except Exception as e:
            print(f"Error querying database: {e}")
        
        return results

    def get_reference(self, paper_id: str) -> Optional[Dict[str, str]]:
        """
        Get full reference information for a paper by its ID.

        Args:
            paper_id: The ArXiv paper ID.

        Returns:
            Dictionary with {title, url} or None if not found.
        """
        # First check cached metadata
        if paper_id in self._paper_metadata:
            return {
                "title": self._paper_metadata[paper_id]["title"],
                "url": self._paper_metadata[paper_id]["url"]
            }
        
        # Try to find in ChromaDB
        try:
            # Query by metadata filter
            results = self.collection.get(
                where={"source_id": paper_id},
                limit=1,
                include=["metadatas"]
            )
            
            if results and results["metadatas"]:
                meta = results["metadatas"][0]
                return {
                    "title": meta.get("title", "Unknown"),
                    "url": meta.get("url", "")
                }
                
        except Exception as e:
            print(f"Error retrieving reference: {e}")
        
        return None

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the current collection.

        Returns:
            Dictionary with collection statistics.
        """
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": "physics_papers"
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_chunks": 0, "error": str(e)}


# Example usage and testing
if __name__ == "__main__":
    # Initialize the knowledge base
    kb = PhysicsKnowledgeBase()
    
    # Example: Crawl papers about lighting direction estimation
    print("\n--- Testing Physics Knowledge Base ---\n")
    
    # Search for papers
    papers = kb.search_arxiv("lighting direction estimation image physics", max_results=2)
    for paper in papers:
        print(f"Found: {paper['title'][:60]}...")
    
    # Crawl and ingest (limit to 2 papers for testing)
    kb.crawl_physics_knowledge("lighting direction estimation physics-based", max_papers=2)
    
    # Query the database
    results = kb.query_physics_db("How is lighting direction estimated using shadows?")
    
    print("\n--- Query Results ---")
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] Source: {result['source_id']}, Page: {result['page']}")
        print(f"    Title: {result['title'][:50]}...")
        print(f"    Text: {result['text'][:200]}...")
        
        # Get full reference
        ref = kb.get_reference(result['source_id'])
        if ref:
            print(f"    Reference: {ref['title']}")
    
    # Show stats
    stats = kb.get_collection_stats()
    print(f"\n--- Collection Stats ---")
    print(f"Total chunks stored: {stats['total_chunks']}")
