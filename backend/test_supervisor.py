from app.agent.supervisor import supervisor_node


test_questions = [
    "我最近上传过什么文件？",
    "我的工作是什么？",
    "帮我创建一个明天上午10点的日历",
    "帮我看看简历里面写了什么",
]


for question in test_questions:

    state = {
        "question": question,
        "rag_contexts": [],
        "memory_context": "",
        "tool_results": [],
        "final_answer": "",
        "next_node": "supervisor"
    }

    result = supervisor_node(state)

    print("----------------------------")
    print("问题：", question)
    print("下一节点：", result["next_node"])