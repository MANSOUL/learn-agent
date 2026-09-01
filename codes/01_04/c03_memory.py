class AgentMemory:
    """
    Agent 记忆系统 —— 模拟三种记忆类型。

    这是一个简化版实现，帮助理解每种记忆的本质。
    实际项目中用 LangChain 的 Memory 模块或向量数据库。
    """

    def __init__(self, max_short_term: int = 10):
        """
        Args:
            max_short_term: 短期记忆最多保留的对话轮数。
        """
        self.long_term = [] # 长期记忆：重要信息列表
        self.short_term = [] # 短期记忆：最近的对话[(user_msg, assistant_msg)]
        self.working_memory = {} # 工作记忆：键值对保存
        self.max_short_term = max_short_term
        self.summary = "" # 摘要

    def add_conversation_to_short_term(self, user_msg: str, assistant_msg: str):
        """
        将对话添加到短期记忆中

        Args:
          user_msg: 用户消息
          assistant_msg: 智能体消息
        """
        self.short_term.append((user_msg, assistant_msg))

        # 如果已经超出了最多保留的对话轮数，则压缩对话成摘要
        if len(self.short_term) > self.max_short_term:
            self.compress()

    def compress(self):
        """压缩历史对话成摘要，并存入长期记忆"""
        history = self.short_term.pop(0)
        combine = f"[用户]：{history[0]}\n[助手]：{history[1]}"
        self.long_term.append(combine)
        if not self.summary:
            self.summary = f"早期对话摘要：\n{combine}"
        else:
            self.summary += f"\n...\n{combine}"

    def set_working(self, key: str, value: str):
        """
        写入工作记忆

        Args:
            key: 键
            value: 值
        """
        self.working_memory[key] = value

    def get_working(self, key: str) -> str: 
        """
        读取工作记忆

        Args:
            key: 键

        Returns:
          工作记忆的值
        """
        return self.working_memory[key]
    
    def get_context_for_llm(self) -> str:
        """
        组装发送给 LLM 的完整上下文

        摘要+工作记忆+短期记忆

        Returns:
            格式化的上下文
        """
        parts = []

        if self.summary:
            parts.append(f"## 历史摘要：\n{self.summary}\n")

        if self.working_memory:
            working_items = "\n".join(
                f"  {k}:{v}" for k, v in self.working_memory.items()
            )
            parts.append(f"## 当前任务状态：\n{working_items}\n")

        if self.short_term:
            recent = "\n".join(
                f"[用户]：{u}\n[助手]：{a}" 
                for u, a in self.short_term[-5:]
            )
            parts.append(f"## 最近对话：\n{recent}")

        return "\n".join(parts)

if __name__ == "__main__":
    memory = AgentMemory(max_short_term = 5)

    memory.set_working("function_calling", "get_weather")
    memory.set_working("invoke", "calculate")

    for num in range(1, 11):
        memory.add_conversation_to_short_term(user_msg=f"用户问题-{num}" , assistant_msg=f"助手回答-{num}")

    print(memory.get_context_for_llm())
