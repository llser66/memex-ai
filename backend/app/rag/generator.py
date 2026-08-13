from openai import OpenAI

from app.core.config import DEEPSEEK_API_KEY


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def build_prompt(
    question,
    contexts,
    memory_context=""
):

    # =========================
    # 1. 构建知识库上下文
    # =========================

    context = ""

    for i, text in enumerate(contexts):

        context += f"""
知识片段 {i + 1}：

{text}

--------------------
"""


    # =========================
    # 2. 构建 Prompt
    # =========================

    prompt = f"""
你是一个个人AI知识助手。

你拥有两类信息：

1. 用户上传的知识库资料
2. 用户个人记忆

请根据提供的信息回答用户问题。

回答规则：

1. 优先根据知识库资料回答。
2. 如果知识库资料没有答案，可以参考用户个人记忆。
3. 如果知识库和用户记忆都没有相关信息，请明确说“不知道”。
4. 不允许编造信息。
5. 回答要简洁、准确。


====================
知识库资料
====================

{context}


====================
用户个人记忆
====================

{memory_context}


====================
用户问题
====================

{question}

"""

    return prompt


def generate_answer(
    question,
    contexts,
    memory_context=""
):

    # 构建 Prompt
    prompt = build_prompt(
        question,
        contexts,
        memory_context
    )


    # 调用 DeepSeek
    response = client.chat.completions.create(

        model="deepseek-chat",

        messages=[

            {
                "role": "system",
                "content": "你是一个专业的个人AI知识助手。"
            },

            {
                "role": "user",
                "content": prompt
            }

        ],

        temperature=0.2
    )


    # 获取回答
    answer = response.choices[0].message.content


    return answer