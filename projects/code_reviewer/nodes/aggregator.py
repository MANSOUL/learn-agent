from collections import Counter
from state import PrReviewState
from config import ROLES, REVIEW_PROMPT

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_ICON = {"critical": "危险🔴", "high": "高🟠", "medium": "中🟡", "low": "低🟢"}

def aggregator_node(state: PrReviewState) -> dict:
    """汇总报告节点"""
    all_reviews = {rk: state[role["state_field"]] for rk, role in ROLES.items()}
    # {
    #   security: {issues: [], summary: ""}
    #   performance
    #   correctness
    #   style
    # }

    all_issues = []
    for role_key, review in all_reviews.items():
        for issue in review.get("issues", []):
            issue["role"] = ROLES[role_key]["name"] # 角色名
            all_issues.append(issue)
    # [{role: "安全审查员", severity, file, line, title, description, suggestion}, ...]

    # 去重
    seen, unique = set(), []
    for issue in all_issues:
        key = (issue.get("file"), str(issue.get("line")), issue.get("title"))
        if key not in seen:
            seen.add(key)
            unique.append(issue)

    # 排序
    unique.sort(key=lambda x: SEVERITY_ORDER.get(x.get("severity", "low"), 99))

    lines = ["## 🤖 AI Code Review 报告\n", "### 各角色评价"]
    for role_key, review in all_reviews.items():
        lines.append(f"- **{ROLES[role_key]['name']}**: {review.get('summary', '')}")
    lines.append("")

    if not unique:
        lines.append("✅ **未发现明显问题,可以合并。**")
    else:
        lines.append(f"### 发现 {len(unique)} 个问题\n")
        for issue in unique:
            icon = SEVERITY_ICON.get(issue.get("severity", "low"), "⚪")
            lines.append(
                f"{icon} **[{issue.get('severity', '?').upper()}] {issue.get('title', '?')}**"
            )
            lines.append(f"- 位置: `{issue.get('file', '?')}`:{issue.get('line', '?')}")
            lines.append(f"- 审查员: {issue.get('role', '?')}")
            lines.append(f"- 问题: {issue.get('description', '?')}")
            lines.append(f"- 建议: {issue.get('suggestion', '?')}")
            lines.append("")
        counts = Counter(i.get("severity") for i in unique)
        lines.append("### 统计")
        lines.append(
            f"危险🔴 {counts.get('critical', 0)} | 高🟠 {counts.get('high', 0)} | 中🟡 {counts.get('medium', 0)} | 低🟢 {counts.get('low', 0)}"
        )

    return {"final_report": "\n".join(lines)}


if __name__ == "__main__":
    mock_state = {
        "pr_url": "",
        "pr_info": "--info--",
        "pr_diff": "--diff--",
        "security_result": {
            "issues": [],
            "summary": "本次变更仅将 tools_map.py 中未使用的 SCHEMA 导入注释掉（并保留 TODO 式的注释行），未引入任何 SQL 注入、XSS、命令注入、硬编码密钥、越权或敏感信息泄露等安全风险。被注释的 SCHEMA 定义仍在 weather.py 中保留，不影响运行逻辑。附带提示（非安全问题）：weather.py 中 SCHEMA 的 properties 与 required 存在重复的 'latitude' 键、缺少 'longitude'，且嵌套 f-string 使用同类引号需 Python 3.12+ 支持，建议后续修正，但与本 PR 的安全审查结论无关。",
        },
        "performance_result": {
            "issues": [],
            "summary": "本次变更仅将 `SCHEMA as get_weather_schema` 的导入注释掉，并把 TOOLS 列表改为直接引用函数对象。文件为模块级静态导入定义，无循环、无 I/O、无查询、无重复计算，导入数量减少反而略微降低模块加载开销，未发现任何具有性能影响的问题。",
        },
        "correctness_result": {
            "issues": [
                {
                    "severity": "medium",
                    "file": "projects/assistant/tools/tools_map.py",
                    "line": "2",
                    "title": "用注释保留废弃导入，应直接删除",
                    "description": "将 `SCHEMA as get_weather_schema` 的导入用注释 `# , SCHEMA as get_weather_schema` 保留在源码中，属于典型的“注释掉的死代码”。这类残留会随时间累积（本文件下方已有 `# TOOLS = [get_weather_schema]`、`# TOOLS_MAP = {...}` 两行同类残留），既干扰阅读，也让后续维护者无法判断该导入是临时禁用还是永久废弃；且历史版本本就由 Git 保存，无需靠注释留档。",
                    "suggestion": '直接删除该注释行以及文件中其余已废弃的注释代码（`# TOOLS = [get_weather_schema]`、`# TOOLS_MAP = {"get_weather": get_weather}`），只保留 `from .weather import get_weather`、`from .search import search_web` 与 `TOOLS = [get_weather, search_web]`。若确需说明为何不再使用 SCHEMA，请用一句完整的中文注释描述原因（例如“已改用 @tool 自动推导 schema，SCHEMA 常量不再需要”），而不是保留被注释的代码片段。',
                },
                {
                    "severity": "low",
                    "file": "projects/assistant/tools/tools_map.py",
                    "line": "1",
                    "title": "注释位置割裂了 import 语句，可读性差",
                    "description": "注释被插在 `from .weather import get_weather` 与原本的 `, SCHEMA as get_weather_schema` 之间，形成一行以逗号开头的孤立注释。若日后有人误取消注释或格式化工具（black/ruff）介入，容易产生语法错误或语义歧义；同时该文件缺少模块级 docstring，未说明 TOOLS 的用途与装配约定。",
                    "suggestion": "若必须保留说明，将注释独立成完整句子置于 import 块之上，避免以逗号开头；并补充模块 docstring，例如说明“本模块集中注册 assistant 可用的工具，TOOLS 供 Agent 绑定使用”。",
                },
                {
                    "severity": "medium",
                    "file": "projects/assistant/tools/weather.py",
                    "line": "74",
                    "title": "SCHEMA 中 properties 键重复，longitude 被 latitude 覆盖",
                    "description": '本次改动移除了对 `SCHEMA` 的引用，但该常量本身存在明显缺陷：`properties` 中两次定义了 `latitude`（第二个描述为“经度，如 116.4074”，实际应为 `longitude`），Python 字典后者会覆盖前者，导致最终 schema 只有 latitude 一个字段；`required` 也写成 `["latitude", "latitude"]`。此外两个字段的 `type` 声明为 `string`，而 `get_weather(latitude: float, longitude: float)` 需要浮点数，类型不一致。一旦后续重新启用该 SCHEMA，会直接导致模型无法传入经度、调用必然失败。',
                    "suggestion": '修正为 `"longitude": {"type": "number", "description": "经度，如 116.4074"}`，并把 `latitude` 的类型改为 `number`、`required` 改为 `["latitude", "longitude"]`；若确认已全面改用 `@tool` 自动生成 schema，则应连同 SCHEMA 常量一起删除，避免留下带 bug 的死代码。',
                },
                {
                    "severity": "low",
                    "file": "projects/assistant/tools/weather.py",
                    "line": "58",
                    "title": "f-string 内使用同类引号，依赖 Python 3.12+ 语法",
                    "description": 'detail 拼接中在双引号 f-string 内又使用双引号索引（如 `current["weather_code"]`），这是 PEP 701 才允许的写法，在 Python 3.11 及以下会直接 SyntaxError。项目未声明最低 Python 版本，存在环境兼容风险；同时该段拼接逻辑较长，可读性一般。',
                    "suggestion": "改用单引号索引（`current['weather_code']`）以兼容旧版本，或将字段抽取为局部变量后再拼接；并在 README/pyproject 中明确项目所需的 Python 版本。",
                },
            ],
            "summary": "本次改动仅一行，功能上无破坏（TOOLS 已改为直接使用 @tool 对象），但实现方式欠佳：用注释保留废弃导入属于死代码，且文件中已存在多处同类注释残留，建议直接删除并补充必要说明性注释与模块 docstring。更重要的是，被移除引用的 weather.SCHEMA 本身存在 properties 键重复（longitude 被 latitude 覆盖）、required 写错、类型与函数签名不符等缺陷，应一并修正或删除，避免留下带 bug 的僵尸代码。",
        },
        "style_result": {
            "issues": [
                {
                    "severity": "low",
                    "file": "projects/assistant/tools/tools_map.py",
                    "line": "2",
                    "title": "注释掉的 SCHEMA 导入使 weather.py 中存在缺陷的 SCHEMA 变为无人校验的死代码",
                    "description": '本 PR 只是把 `SCHEMA as get_weather_schema` 的导入注释掉，改动本身语法合法、不影响运行（TOOLS 仍为 [get_weather, search_web]，agent.py 通过 create_agent 消费 langchain tool 对象，行为不变）。但注释后 weather.py 中的 SCHEMA 常量彻底失去唯一引用，其内部错误（properties 中两个键都写成 "latitude"，缺少 "longitude"；required 也是 ["latitude", "latitude"]；且类型声明为 string 而函数签名为 float）不会再被任何调用路径暴露，后续若有人直接取消注释复用该 SCHEMA，会导致模型无法传入 longitude、工具调用参数校验失败（strict=True 下 additionalProperties=False 会直接报错）。',
                    "suggestion": "要么直接删除 weather.py 中已失效的 SCHEMA 常量（langchain @tool 会自动从类型注解与 docstring 生成 schema，无需手写），要么修正为 latitude/longitude 两个正确字段并把类型改为 number，同时移除 tools_map.py 中悬空的 `# , SCHEMA as get_weather_schema` 注释行，避免误导。",
                },
                {
                    "severity": "low",
                    "file": "projects/assistant/tools/weather.py",
                    "line": "58",
                    "title": "（既有问题，非本 PR 引入）f-string 内嵌套同类双引号 + current 可能为 None，存在 SyntaxError/TypeError 风险",
                    "description": '本 PR 未修改该文件，但它是 tools_map.py 导入的目标模块，问题会随导入链一起触发：1) `f"{_WEATHER_CODE_2_TEXT.get(current["weather_code"])}；"` 在 f-string 内使用了与外层相同的双引号，仅 Python 3.12+（PEP 701）支持，在 3.8~3.11 上 import 阶段即抛 SyntaxError，导致 tools_map.py 的 `from .weather import get_weather` 失败、整个 agent 无法启动；2) `data.get("current")` 未判空，当接口返回缺少 current 字段（如参数被拒、返回 error 结构）时 current 为 None，`current["weather_code"]` 抛 TypeError，而 except 只捕获 requests.exceptions.*，异常会直接冒泡到 run_agent 使会话中断；3) `_WEATHER_CODE_2_TEXT.get(...)` 对未知 weather_code 返回 None，会拼出 "None；" 的脏文案。',
                    "suggestion": '将 f-string 内层引号改为单引号（或整体改用单引号包裹）以兼容 3.12 以下版本；对 current 做判空并返回友好提示（如 "未获取到天气数据"）；对 weather_code 使用 `_WEATHER_CODE_2_TEXT.get(code, "未知天气")` 提供默认值。',
                },
            ],
            "summary": "本 PR 的实际改动（注释掉未使用的 SCHEMA 导入）语法正确、不改变运行时行为，TOOLS 仍由两个 langchain tool 组成，agent.py 调用链不受影响，无 critical/high 级问题。主要遗留两点：一是注释而非删除，使 weather.py 中字段名重复写错（两个 latitude、缺 longitude）的 SCHEMA 变成无人发现的死代码，建议直接删除或修正；二是被导入模块 weather.py 自身存在 f-string 嵌套同种引号（Python<3.12 会 SyntaxError 导致导入失败）与 current 未判空（TypeError 未被 requests 异常捕获）的既有隐患，建议顺手修复。整体上属于安全的清理型改动，但建议以删除死代码代替注释保留。",
        },
        "final_report": "",
    }

    print(aggregator_node(mock_state))
