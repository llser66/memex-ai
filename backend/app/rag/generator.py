from openai import OpenAI

from app.core.config import DEEPSEEK_API_KEY


def get_client() -> OpenAI:
    """延迟创建 DeepSeek 客户端，避免缺少配置时阻塞健康检查。"""
    if not DEEPSEEK_API_KEY:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY，请在环境变量或 .env 中设置。")

    return OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )


def build_prompt(question, contexts, memory_context=""):

    # RAG 检索资料
    context_text = "\n\n".join(contexts)

    prompt = f"""
你是 Memex AI，一个个人工作记忆助手。

请结合下面的“用户长期记忆”和“知识库资料”回答问题。

如果知识库资料中有答案，优先依据资料回答。
如果用户长期记忆中有相关信息，也可以使用。
如果两者都没有，请明确说明不知道，不要编造。

【用户长期记忆】
{memory_context}

【知识库资料】
{context_text}

【用户问题】
{question}
"""

    return prompt


def generate_answer(question, contexts, memory_context=""):

    prompt = build_prompt(
        question,
        contexts,
        memory_context
    )

    response = get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业、准确的 AI 助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content


def generate_answer_stream(question, contexts, memory_context=""):
    """以 token 流的形式生成回答，供 SSE 接口使用。"""
    prompt = build_prompt(question, contexts, memory_context)
    response = get_client().chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业、准确的 AI 助手。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        stream=True,
    )

    for chunk in response:
        if not chunk.choices:
            continue
        content = chunk.choices[0].delta.content
        if content:
            yield content
