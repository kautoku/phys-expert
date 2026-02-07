---
description: Generate PyTorch loss function from paper formula
---

# /loss - Generate Loss Function from Paper

Use this workflow when user needs a PyTorch loss function based on a formula.

## Steps

// turbo
1. Query for the specific loss formula in papers
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('LOSS_TYPE loss function formula equation', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:800])
"
```

2. Extract the mathematical formula from retrieved chunks

3. Translate to PyTorch with these requirements:
   - Input tensors: `(B, C, H, W)` format
   - Use `torch.nn.functional` where appropriate
   - Handle edge cases (division by zero, normalization)
   - Include docstring with source citation

## Code Template

```python
import torch
import torch.nn.functional as F

class PhysicsLoss(torch.nn.Module):
    """
    [Loss Name] from [Paper Title] (arXiv:[ID], p.[PAGE])
    
    Formula: [LaTeX formula here]
    """
    
    def __init__(self):
        super().__init__()
    
    def forward(self, pred, target, **kwargs):
        # pred: (B, C, H, W)
        # target: (B, C, H, W)
        
        # Implementation based on paper formula
        ...
        
        return loss
```

4. Verify the implementation matches paper description

5. Provide usage example with sample tensor shapes
