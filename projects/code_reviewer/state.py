from typing import TypedDict

class PrReviewState(TypedDict):
    """LangGraph Agent 的状态定义

    这是 LangGraph 最核心的概念。所有节点共享这个状态，
    节点通过读取/修改状态来协作完成任务。

    Annotated[list, add_messages] 表示消息列表使用
    追加模式（新消息添加到末尾，不会覆盖）。
    """
    # messages: Annotated[list, add_messages]
    pr_url: str  # pr 地址
    pr_info: str  # pr 信息
    pr_diff: str  # pr diff
    security_result: dict # 安全
    performance_result: dict # 性能
    correctness_result: dict # 正确性
    style_result: dict # 风格
    final_report: str  #最终报告
