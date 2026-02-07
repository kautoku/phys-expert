---
description: Validate model predictions using physics-based sanity checks
---

# /verify - Physics Sanity Check

Use this workflow to validate model outputs against physical principles.

## Steps

// turbo
1. Check knowledge base for validation methods
```bash
cd /home/itzu/phys-expert && python -c "
from physics_knowledge_db import PhysicsKnowledgeBase
kb = PhysicsKnowledgeBase(db_path='./db')
results = kb.query_physics_db('validation verification sanity check light direction', n_results=5)
for i, r in enumerate(results):
    print(f'\\n--- [{r.get(\"source_id\", \"?\")}] {r.get(\"title\", \"Unknown\")} (p.{r.get(\"page\", \"?\")}) ---')
    print(r.get('text', '')[:600])
"
```

2. Run geometric verification checks:
   - **Brightest Pixel Test**: Does predicted light direction align with brightest regions?
   - **Shadow Consistency**: Are shadows on opposite side of predicted light?
   - **Normal Dot Product**: Is (n · l) positive for lit areas?

3. Generate verification code:

```python
import torch
import numpy as np

def verify_light_direction(image, predicted_light, normals=None):
    """
    Sanity checks for light direction prediction.
    
    Args:
        image: (H, W, 3) RGB image
        predicted_light: (3,) normalized light direction vector
        normals: optional (H, W, 3) surface normals
    
    Returns:
        dict with verification results
    """
    results = {}
    
    # 1. Brightest pixel alignment
    gray = np.mean(image, axis=-1)
    brightest_y, brightest_x = np.unravel_index(np.argmax(gray), gray.shape)
    # Check if light direction points toward brightest region
    
    # 2. Shadow region check (dark pixels should have n·l < 0 or be occluded)
    if normals is not None:
        n_dot_l = np.sum(normals * predicted_light, axis=-1)
        dark_mask = gray < 0.1
        # In dark regions, n·l should be negative or zero
        results['shadow_consistency'] = np.mean(n_dot_l[dark_mask] <= 0.1)
    
    return results
```

4. Report findings with pass/fail status
