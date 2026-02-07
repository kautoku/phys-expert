---
description: Research a new physics topic and ingest papers into the knowledge base
---

# /research - Ingest Physics Papers

Use this workflow when the user wants to learn about a new physics concept or method.

## Steps

// turbo
1. Check current knowledge base stats
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
print(kb.get_collection_stats())
"
```

// turbo
2. Ingest papers on the requested topic (replace TOPIC with user's topic)
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
result = kb.crawl_physics_knowledge('TOPIC', max_papers=5)
print(f'Ingested {result} chunks')
"
```

// turbo
3. Query the newly ingested knowledge to provide a summary
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('TOPIC overview methods', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:600])
"
```

4. Summarize findings to the user with proper citations (Source: Paper Title, arXiv ID, page)
