"""
Agent 状态定义
----------------
LangGraph 通过一个共享的 state 字典在不同节点间传递数据。
这里使用 TypedDict 定义所有可能在节点间流转的字段，便于类型检查和自动补全。
"""

from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    # 用户原始问题
    question: str

    # RAG 节点检索到的文本块列表（纯文本内容）
    rag_contexts: Optional[List[str]]

    # Memory 节点组装好的记忆上下文（用户画像 + 事件记忆）
    memory_context: Optional[str]

    # Tool 节点执行后返回的结果消息列表（比如周报生成路径）
    tool_results: Optional[List[str]]

    # Generate 节点生成的最终答案
    final_answer: Optional[str]

    # 下一个要执行的节点名称，由 Supervisor 或其他节点设置
    next_node: Optional[str]

    # 来源信息列表，每个元素是 metadata 字典（例如 {"source": "xxx.pdf", "page": 1}）
    sources: Optional[List[dict]]

    # 工具生成的文件名（例如周报 Markdown 文件）
    report_file: Optional[str]
