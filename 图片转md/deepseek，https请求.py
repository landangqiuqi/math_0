import requests
import json

# 配置参数
DEEPSEEK_API_KEY = "sk-c3b9d4aca1544ee4982a5e14010dd120"  # 替换为你的真实API密钥
API_URL = "https://api.deepseek.com/v1/chat/completions"

# 纯字符串prompt构建函数
def build_prompt(query: str) -> str:
    examples = [
        "以下两端文字是图片转成txt的，但是输出有问题，一份是图片转.md，但是可能把英文转成中文且文字顺序有问题，另一份不能处理公式会识别成错误的东西",
        "但他们都是识别的同一个图片，请你帮我恢复成正常的带公式的.md"
    ]
    return "\n".join(examples) + f"\n问题: {query}\n回答:"

# 直接调用API
def ask_deepseek(query: str) -> str:
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": build_prompt(query)
        }],
        "temperature": 0.3,
        "max_tokens": 4096
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()  # 自动抛出HTTP错误
    
    return response.json()["choices"][0]["message"]["content"]

# 执行问答
question = ""
answer = ask_deepseek(question)
print("证明步骤：", answer.strip())
