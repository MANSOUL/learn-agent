import subprocess, os, tempfile
from pathlib import Path
from github import get_pr_info_json

def run_static_analysis(pr_url: str) -> str:
    """clone PR 分支,跑静态分析,返回结果摘要"""

    # 拿 PR 的 head ref 和 clone URL
    pr = get_pr_info_json(pr_url)
    clone_url = pr["head"]["repo"]["clone_url"]
    ref = pr["head"]["ref"]

    with tempfile.TemporaryDirectory() as tmp:
        # shallow clone PR 分支
        subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", ref, clone_url, tmp],
            capture_output=True,
            text=True,
            timeout=120,
        )
        os.chdir(tmp)

        results = []

        # 1. ruff(lint + 格式)
        r = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)
        if r.stdout.strip():
            results.append(f"### ruff (lint)\n```\n{r.stdout[:3000]}\n```")

        # 2. mypy(类型)
        r = subprocess.run(["mypy", "."], capture_output=True, text=True)
        if r.stdout.strip():
            results.append(f"### mypy (类型检查)\n```\n{r.stdout[:3000]}\n```")

        # 3. bandit(安全)
        r = subprocess.run(["bandit", "-r", ".", "-ll"], capture_output=True, text=True)
        if "No issues identified" not in r.stdout:
            results.append(f"### bandit (安全扫描)\n```\n{r.stdout[:3000]}\n```")

        return "\n\n".join(results) if results else "静态分析未发现问题"
