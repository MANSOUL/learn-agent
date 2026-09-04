import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from tavily import TavilyClient

load_dotenv()

# 获取 API_KEY
_API_KEY = os.getenv("TAVILY_KEY")

@tool
def search_web(query: str) -> str:
    """从互联网搜索相关内容。

    Args:
        query: 查询条件

    Returns:
        搜索到的相关内容
    """
    client = TavilyClient(_API_KEY)
    response = client.search(
        query=query,
        search_depth="basic",  # "basic"快 / "advanced"更全但慢
        max_results=5,
        include_answer=False,  # 附带一个 AI 总结的一句话答案
        include_raw_content=False,
    )
    # print(response)
    return build_search_context(response["results"])


def build_search_context(results: list[dict]) -> str:
    parts = [
        "以下是从互联网检索到的最新参考资料,优先基于这些资料回答,并在答案末尾附上来源编号:"
    ]
    for i, r in enumerate(results, 1):
        date = f" (发布日期: {r['published_date']})" if r.get("published_date") else ""
        parts.append(
            f"\n[{i}] 标题: {r['title']}{date}\n"
            f"    链接: {r['url']}\n"
            f"    内容: {r['content']}\n"
        )
    return "\n".join(parts)
