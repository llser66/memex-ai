"""
LangGraph 图构建
---------------
定义整个 Agent 的工作流：
    supervisor -> (rag | memory | tool) -> generate -> END

使用 StateGraph 来管理节点和状态流转。
"""

from langgraph.graph import StateGraph, END
from app.agent.state import AgentState
from app.agent.supervisor import supervisor_node
from app.agent.rag_node import rag_node
from app.agent.memory_node import memory_node
from app.agent.tool_node import tool_node
from app.agent.generate_node import generate_node


def create_initial_state(question: str) -> AgentState:
    """创建一次 Agent 执行所需的初始状态。"""
    return {
        "question": question,
        "rag_contexts": [],
        "memory_context": "",
        "tool_results": [],
        "final_answer": "",
        "next_node": "supervisor",
        "sources": [],
        "report_file": None,
    }


def prepare_agent_state(question: str) -> AgentState:
    """执行 Supervisor 和上下文节点，但暂不调用最终 LLM 生成。

    普通接口由完整 LangGraph 负责生成答案；流式接口需要在拿到上下文后
    使用 OpenAI-compatible streaming API，因此复用同一组节点执行一次预处理。
    """
    state = create_initial_state(question)
    state.update(supervisor_node(state))

    nodes = {
        "rag": rag_node,
        "memory": memory_node,
        "tool": tool_node,
    }
    next_node = state["next_node"]
    state.update(nodes[next_node](state))
    return state


def build_agent_graph():
    # 创建状态图，状态类型为 AgentState
    graph = StateGraph(AgentState)

    # 添加所有节点
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("rag", rag_node)
    graph.add_node("memory", memory_node)
    graph.add_node("tool", tool_node)
    graph.add_node("generate", generate_node)

    # 设置入口节点为 supervisor
    graph.set_entry_point("supervisor")

    # 条件边：根据 supervisor 返回的 next_node 决定下一个节点
    graph.add_conditional_edges(
        "supervisor",
        lambda state: state["next_node"],   # 读取 next_node 字段
        {
            "rag": "rag",
            "memory": "memory",
            "tool": "tool",
        }
    )

    # 普通边：rag/memory/tool 完成后都进入 generate
    graph.add_edge("rag", "generate")
    graph.add_edge("memory", "generate")
    graph.add_edge("tool", "generate")

    # generate 完成后结束流程
    graph.add_edge("generate", END)

    # 编译图，返回可执行对象
    return graph.compile()
