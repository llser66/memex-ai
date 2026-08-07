from openai import OpenAI

from app.core.config import DEEPSEEK_API_KEY



client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)


def build_prompt(question, documents):

    context = ""

    for doc in documents:

        context += (
            f"""
来源:
{doc['metadata']['source']}

页码:
{doc['metadata']['page']}

内容:
{doc['text']}

-------------
"""
        )


    prompt = f"""
你是一个个人AI知识助手。

请严格根据下面提供的资料回答问题。

如果资料中没有答案，请明确说不知道。

回答必须包含来源信息。



资料:

{context}


用户问题:

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
                "content":"你是一个专业AI助手"
            },

            {
                "role":"user",
                "content":prompt
            }

        ],

        temperature=0.2
    )


    answer = response.choices[0].message.content


    return answer