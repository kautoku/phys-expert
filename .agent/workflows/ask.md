---
description: Ask a physics question and get an answer grounded in the knowledge base
---

# /ask - Consult Physics Expert

Use this workflow when the user asks a physics question. **You MUST query the database before answering.**

## Steps

// turbo
1. Query the knowledge base for relevant information
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('USER_QUESTION_HERE', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:800])
"
```

2. If results are relevant (check distance scores), answer with citations:
   - Format: `📚 Source: "Paper Title" (arXiv:XXXX, p.Y)`
   - Include the key information from retrieved chunks
   - Note confidence level based on number of relevant matches

3. If NO relevant results found, respond with:
   - *"I cannot verify this in the knowledge base."*
   - Suggest running `/research TOPIC` to ingest relevant papers first

## Response Template

```
📚 Source: "[Paper Title]" (arXiv:[ID], p.[PAGE])

💡 According to this paper, [ANSWER BASED ON RETRIEVED TEXT]...

⚠️ Confidence: [X] relevant chunks found.
```
