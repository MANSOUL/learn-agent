ROLES = {
    "security": {
        "name": "安全审查员",
        "system": "你是资深安全专家。审查:SQL注入/XSS/命令注入/硬编码密钥/越权/敏感信息泄露。只报告真实安全风险。",
        "state_field": "security_result",
    },
    "performance": {
        "name": "性能审查员",
        "system": "你是性能专家。审查:N+1查询/大文件内存/同步阻塞/重复计算/高复杂度循环。只报告有性能影响的问题。",
        "state_field": "performance_result",
    },
    "correctness": {
        "name": "逻辑正确性审查员",
        "system": "你是逻辑专家。审查:边界条件/错误处理/并发问题/资源泄漏/分支覆盖。只报告会导致bug的问题。",
        "state_field": "correctness_result",
    },
    "style": {
        "name": "代码风格审查员",
        "system": "你是代码质量专家。审查:函数过长/命名不清/重复代码/注释缺失。只报告值得修改的问题。",
        "state_field": "style_result",
    },
}

REVIEW_PROMPT = (
    "PR URL: {pr_url}\n"
    "请审查以下 PR。不要返回markdown，仅返回正确严格的JSON格式。\n\n【PR信息】\n{pr_info}\n\n"
    "【变更diff】\n```diff\n{pr_diff}\n```\n\n"
    "如 diff 上下文不足,可调用 read_file_at_pr 读取完整文件。\n\n"
    '不要返回markdown，仅返回正确严格的JSON格式: {{"issues":[{{"severity":"critical|high|medium|low","file":"路径","line":"行号",'
    '"title":"标题","description":"说明","suggestion":"建议"}}],"summary":"整体评价"}}\n'
    '无问题则返回 {{"issues":[],"summary":"未发现明显问题"}}'
)
