import os
import re
import requests
import base64
import json
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def _get_request_headers():
    h = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        h["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return h

def parse_pr_url(url: str) -> tuple[str, str, int]:
    """解析 PR URL，返回 owner, repo, pr_number"""
    m = re.match(f"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)", url)
    if not m:
        raise ValueError(f"无效的 PR URL：${url}")
    return m.group(1), m.group(2), m.group(3)


@tool
def get_pr_info(url: str) -> str:
    """通过 PR URL 获取 PR 的信息：PR #，作者，分支，描述，变更文件数，变更统计，变更文件清单

        Args:
            url: PR URL

        Returns
            返回 PR 的信息
    """

    owner, repo, pr_number = parse_pr_url(url)

    # 获取 作者信息
    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=_get_request_headers(),
        timeout=15,
    )
    # response.raise_for_status()  # 非 2xx 抛 HTTPError
    if response.status_code != 200:
        return f"获取 PR 失败：${reponse.status_code} {r.text[:300]}"
    pr_data = response.json()

    # 获取变更文件清单
    files = []
    page = 1
    while True:
        file_resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}/files",
            headers=_get_request_headers(),
            params={"per_page": 100, "page": page},
            timeout=15,
        )
        if file_resp.status_code != 200:
            break

        batch = file_resp.json()
        
        if not batch:
            break

        for b in batch:
            files.append(
                {
                    "path": b["filename"],
                    "status": b["status"], # added/modified/removed/rename
                    "additions": b["additions"],
                    "deletions": b["deletions"],
                    "changes": b["changes"],
                }
            )
        page += 1

    summary = (
        f"PR #{pr_number}: {pr_data['title']}\n"
        f"作者: {pr_data['user']['login']}\n"
        f"分支: {pr_data['head']['ref']} -> {pr_data['base']['ref']}\n"
        f"描述: {pr_data.get('body', '无')}\n"
        f"变更文件数: {len(files)}\n"
        f"变更统计: +{sum(f['additions'] for f in files)} -{sum(f['deletions'] for f in files)}\n"
        "\n变更文件清单:\n" +
        "\n".join(
          f"  [{f['status']}] {f['path']} (+{f['additions']}/-{f['deletions']})"
          for f in files
        )
    )
    return summary


@tool
def get_pr_diff(url: str, file_filter: str = None, max_lines: int = 3000) -> str:
    """获取 PR diff的内容

    Args:
        url: PR URL

    Returns:
        PR diff的内容
    """
    owner, repo, pr_number = parse_pr_url(url)

    # 获取 PR 所有的变化，变化以
    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
        headers={**_get_request_headers(), "Accept": "application/vnd.github.diff"},
        timeout=30,
    )
    if resp.status_code != 200:
        return f"获取 diff 失败：{resp.status_code}"

    diff = resp.text
    # print(diff)
    # 按文件切分
    files = re.split(r"(?=^diff --git )", diff, flags=re.M)
    if file_filter:
        files = [f for f in files if file_filter in f]

    parts = []
    total_lines = 0
    for f in files:
        flines = f.count("\n")
        if total_lines + flines > max_lines:
            parts.append(f"...[diff 已截断，剩余 {len(files)-len(parts)} 个文件未展示]")
            break
        parts.append(f)
        total_lines += flines

    return "\n".join(parts)


@tool
def read_file_at_pr(url: str, file_path: str) -> str:
    """读取 PR 分支上某个文件的完整内容

    Args:
        url: PR URL
        file_path: 文件路径 如 projects/assistant/tools/tools_map.py
    
    Returns:
        文件内容
    """

    owner, repo, pr_number = parse_pr_url(url)

    resp = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/pulls/{pr_number}",
        headers=_get_request_headers(),
        timeout=15,
    )

    pr_info = resp.json()
    pr_ref = pr_info["head"]["ref"]

    r = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/contents/{file_path}",
        params={"ref": pr_ref},
        headers=_get_request_headers(),
        timeout=15,
    )
    if r.status_code != 200:
        return f"读取文件失败：{r.status_code}"
    content_data = r.json()
    content = base64.b64decode(content_data["content"]).decode(
        "utf-8", errors="replace"
    )
    lines = content.splitlines()
    if len(lines) > 500:
        content = "\n".join(lines[:500]) + f"\n...(共 {len(lines)} 行，已截断)"
    # print(f"文件：{file_path} @ {ref}\n{content}")
    return f"文件：{file_path} @ {pr_ref}\n{content}"


@tool
def post_pr_comment(url: str, body: str) -> str:
    """将 Review 结果评论到issues

    Args:
        url: PR URL
        body: Review 结果
      
    Returns:
        成功或失败文案
    """
    owner, repo, pr_number = parse_pr_url(url)
    resp = requests.post(
        f"{GITHUB_API}/repos/{owner}/{repo}/issues/{pr_number}/comments",
        headers=_get_request_headers(),
        json={"body": body},
        timeout=15,
    )

    if resp.status_code in (200, 201):
        return "✅ 评论发布成功"
    
    return f"❌ 评论发布失败：{resp.status_code} {resp.text[:300]}"


if __name__ == "__main__":
    # print(parse_pr_url("https://github.com/MANSOUL/learn-agent/pull/1"))
    # print(get_pr_info("https://github.com/MANSOUL/learn-agent/pull/1"))
    # print(get_pr_diff("https://github.com/MANSOUL/learn-agent/pull/1"))
    # print(
    #     read_file_at_pr.invoke({
    #         "url": "https://github.com/MANSOUL/learn-agent/pull/1",
    #         "file_path":"projects/assistant/tools/tools_map.py",
    #     })
    # )
    print(
        post_pr_comment.invoke({
            "url": "https://github.com/MANSOUL/learn-agent/pull/1",
            "body": "test1",
        })
    )
