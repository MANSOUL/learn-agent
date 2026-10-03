import os

from prefab_ui.app import PrefabApp
from prefab_ui.components import Column, Heading, Text, Badge, Row
from fastmcp import FastMCP


mcp = FastMCP("My MCP Server")

@mcp.tool(app=True)
def greet(name: str) -> PrefabApp:
    """用可视化卡片问候某人。"""
    with Column(gap=4, css_class="p-6") as view:
        Heading(f"Hello, {name}!")
        with Row(gap=2, align="center"):
            Text("Status")
            Badge("Greeted", variant="success")

    return PrefabApp(view=view)


def is_valid(path: str, is_dir: bool = True) -> str:
    """检查路径是否有效，防止访问根目录之外的文件。"""
    if os.path.isabs(path):
        raise ValueError("路径不能以 '/' 开头。请提供相对路径。")

    dir_path = os.path.normpath(
        os.path.join(FILE_TOOL_ROOT, path)
    )

    # 如果请求的路径不在允许的根目录下，则拒绝访问
    rel_path = os.path.relpath(
        dir_path, start=FILE_TOOL_ROOT
    )
    if rel_path.startswith("../") or rel_path == "..":
        raise ValueError(f"{('目录' if is_dir else '文件')} {path} 无权限访问。")

    # 如果请求的路径不存在，则FileNotFoundError
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"{('目录' if is_dir else '文件')} {path} 不存在。")

    if is_dir:
      # 如果不是目录，则抛出异常
      if not os.path.isdir(dir_path):
          raise NotADirectoryError(f"{path} 不是一个目录。")
    else:
      # 如果不是文件，则抛出异常
      if not os.path.isfile(dir_path):
          raise IsADirectoryError(f"{path} 不是一个文件。")

    return dir_path


FILE_TOOL_ROOT = "/Users/kuangguanghu/workspace/learn-agent/projects"
@mcp.tool
def list_dir(path: str = "") -> list:
    """列出指定目录下的文件和子目录。"""
    dir_path = is_valid(path)

    # 以字典形式列出目录下的文件，包含文件名和文件类型
    files = []
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        is_dir = os.path.isdir(file_path)
        files.append({"name": filename, "is_directory": is_dir})

    return files


@mcp.tool
def read_file(file_path: str) -> str:
    """读取指定文件的内容。"""
    file_path = is_valid(file_path, is_dir=False)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    return content

# 返回字符串的基本动态资源
@mcp.resource("resource://greeting")
def get_greeting() -> str:
    """提供简单的问候消息。"""
    return "Hello from FastMCP Resources!"
