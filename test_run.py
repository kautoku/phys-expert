"""
Test Script for Physics Knowledge Base

This script manually tests the PhysicsKnowledgeBase functionality
without requiring the MCP server or VS Code integration.

Usage:
    python test_run.py
"""

from physics_knowledge_db import PhysicsKnowledgeBase


def main():
    print("=" * 60)
    print("🧪 Physics Knowledge Base Test Script")
    print("=" * 60)
    
    # Step 1: Initialize the knowledge base
    print("\n📚 Step 1: Initializing PhysicsKnowledgeBase...")
    kb = PhysicsKnowledgeBase(db_path="./db")
    
    # Step 2: Check current stats
    print("\n📊 Step 2: Checking current database stats...")
    stats = kb.get_collection_stats()
    print(f"   Current chunks in database: {stats['total_chunks']}")
    
    # Step 3: Crawl physics papers on photometric stereo
    print("\n🔍 Step 3: Crawling ArXiv for 'photometric stereo' papers...")
    total_chunks = kb.crawl_physics_knowledge("photometric stereo", max_papers=3)
    print(f"   Ingested {total_chunks} new chunks")
    
    # Step 4: Query the knowledge base
    print("\n❓ Step 4: Querying: 'how shadows affect normal estimation'...")
    results = kb.query_physics_db("how shadows affect normal estimation", n_results=3)
    
    print("\n" + "=" * 60)
    print("📖 QUERY RESULTS")
    print("=" * 60)
    
    if not results:
        print("   No results found.")
    else:
        for i, result in enumerate(results, 1):
            print(f"\n[{i}] Source: {result['source_id']}")
            print(f"    Title: {result['title'][:60]}...")
            print(f"    Page: {result['page']}")
            print(f"    Relevance: {1 - result['distance']:.3f}")
            print(f"    Text: {result['text'][:200]}...")
            
            # Verify the reference
            ref = kb.get_reference(result['source_id'])
            if ref:
                print(f"    📄 Citation: {ref['title']}")
                print(f"    🔗 URL: {ref['url']}")
    
    # Step 5: Final stats
    print("\n" + "=" * 60)
    print("📊 FINAL STATISTICS")
    print("=" * 60)
    final_stats = kb.get_collection_stats()
    print(f"   Total chunks in database: {final_stats['total_chunks']}")
    
    print("\n✅ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
