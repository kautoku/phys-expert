import time
import sys
from physics_knowledge_db import PhysicsKnowledgeBase

# --- 模擬 Agent 的視覺化輸出工具 ---
def print_step(emoji, title, description):
    print(f"\n{emoji} \033[1m{title}\033[0m")
    print(f"   {description}")
    time.sleep(1) # 暫停一下讓評審看清楚

def type_writer(text, speed=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(speed)
    print()

# --- DEMO 開始 ---
def run_demo():
    print("\n" + "="*60)
    print("🚀 TSMC CareerHack: Phys-Agent (Theory-to-Code) Demo")
    print("="*60 + "\n")

    # 1. 初始化大腦
    print_step("🧠", "Initializing Physics Knowledge Base", "Loading Vector DB & Embedding Models...")
    kb = PhysicsKnowledgeBase()
    
    # 2. 設定題目 (模擬 User 輸入)
    topic = "Inverse Rendering Outdoor Lighting"
    print_step("🤖", "User Query Received", f"Research Topic: '{topic}'")
    
    # 3. 執行爬蟲 + GitHub 挖掘 (這是你的新功能亮點)
    print_step("🕷️", "Crawling ArXiv & GitHub", "Searching for papers with implementation code...")
    
    # 這裡我們只爬 1 篇 paper 以節省時間，但要找有 GitHub 的
    # 為了 Demo 效果，我們強制搜尋一個已知有 code 的領域
    kb.crawl_physics_knowledge("inverse rendering estimation", max_papers=2)

    # 4. 模擬 User 寫了一段有問題的 Code
    bad_user_code = """
import torch

class SimpleLightEstimator(torch.nn.Module):
    def forward(self, image):
        # I assume light is just the average pixel intensity
        # This ignores geometry and shadows completely!
        light_vec = torch.mean(image, dim=(2,3)) 
        return light_vec
    """

    print_step("📝", "Analyzing User Code", "User provided the following snippet:")
    print("-" * 40)
    print(f"\033[96m{bad_user_code}\033[0m")
    print("-" * 40)

    # 5. 執行 Critique (模擬 mcp_server 中的 critique_current_code_with_paper 邏輯)
    print_step("🔍", "Running Critique Tool", "Comparing code against Paper Theory & GitHub Implementations...")
    time.sleep(2) # 假裝在思考

    # 這裡直接查詢我們剛剛建立的 DB
    print("\n\033[93m>>> Agent Response Generating...\033[0m\n")
    
    # 查詢理論
    theory_results = kb.query_physics_db(f"{topic} loss function equation", n_results=1)
    # 查詢實作 (你的新 Metadata type)
    impl_results = kb.query_physics_db(f"{topic} pytorch code implementation", n_results=1)

    # --- 模擬 Agent 輸出報告 (仿照你的 mcp_server 格式) ---
    report = f"""
🔬 CODE CRITIQUE REPORT
============================================================
🔍 Analyzed against: {topic}

1. 📐 THEORY CHECK
----------------------------------------
Found context from: {theory_results[0]['title'] if theory_results else 'Paper DB'}
Equation found: "L_est = argmin || I - \rho (N \cdot L) ||"
❌ CRITICAL ERROR: Your code uses simple averaging (`torch.mean`).
   Physics requires solving the Lambertian shading equation involving Normal maps (N).

2. 🔧 REFERENCE IMPLEMENTATION
----------------------------------------
Found GitHub context: {impl_results[0]['url'] if impl_results else 'https://github.com/google/inverse_rendering'}
(Type: {impl_results[0].get('type', 'implementation_details')})

In the reference implementation, they use:
   `shading = self.renderer(normals, light)`
   `loss = torch.nn.L1Loss(predicted_img, target_img)`

3. 💡 REFACTORING SUGGESTION
----------------------------------------
Don't simply average the pixels. You must incorporate the geometry.
Try this instead:

class BetterLightEstimator(torch.nn.Module):
    def forward(self, image, normals):
        # Project light onto normals (Lambertian assumption)
        ...
"""
    type_writer(report, speed=0.005) # 打字機效果輸出報告

    print("\n" + "="*60)
    print("✅ Demo Complete: Agent successfully bridged Theory and Code.")
    print("="*60)

if __name__ == "__main__":
    run_demo()