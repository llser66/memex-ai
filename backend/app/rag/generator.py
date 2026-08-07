from openai import OpenAI

from app.core.config import DEEPSEEK_API_KEY


client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)



def build_prompt(question, documents):

    context = ""


    for doc in documents:

        context += f"""
来源：
{doc["metadata"]["source"]}

页码：
{doc["metadata"]["page"]}

内容：
{doc["text"]}

-----------------
"""


    prompt = f"""

你是一个个人AI知识助手。

请严格根据下面提供的资料回答问题。

要求：

1. 只能使用资料中的信息
2. 如果资料没有答案，请回答不知道
3. 回答必须标注来源和页码


资料：

{context}


用户问题：

{question}


"""


    return prompt



def generate_answer(question, documents):


    prompt = build_prompt(
        question,
        documents
    )


    response = client.chat.completions.create(

        model="deepseek-chat",


        messages=[

            {
                "role":"system",
                "content":"你是一个专业知识助手"
            },

            {
                "role":"user",
                "content":prompt
            }

        ],


        temperature=0.2
    )


    return response.choices[0].message.content