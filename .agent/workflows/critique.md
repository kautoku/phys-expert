---
description: Review user's PyTorch code against paper theory and reference implementations
---

# /critique - Critique Code Against Papers

Use this workflow when the user asks "Is my code correct?" or wants code review.

## Steps

// turbo
1. Query knowledge base for theory on the topic
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('TOPIC formula implementation', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:800])
"
```

// turbo
2. Query for implementation details (GitHub READMEs, code snippets)
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('TOPIC implementation code pytorch', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:800])
"
```

3. Compare user's code against paper theory:
   - Check if formulas match the paper
   - Verify tensor dimension handling (B, 3, H, W)
   - Look for common issues (Y-up vs Y-down, normalization, etc.)

4. Report findings in structured format:

## Response Template

```
## 📋 Code Critique Report

### ✅ Theory Check
- Paper formula: [LaTeX from paper]
- Your implementation: [matches/differs]

### 🔍 Implementation Comparison
- Reference: [cite paper or GitHub]
- Discrepancies found: [list any issues]

### 💡 Refactoring Suggestions
1. [Specific improvement with citation]
2. [Another improvement]

📚 Sources: [List all papers consulted]
```
