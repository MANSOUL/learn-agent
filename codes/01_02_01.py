import subprocess
import sys
from pathlib import Path

def check_python_version():
  """检查 python 版本是否符合要求（》=3.10）"""
  version = sys.version_info
  if version.major >= 3 and version.minor >= 10:
    print(f"✅ python {version.major}.{version.minor}.{version.micro} - 符合要求")
    return True
  print(f"✅ python {version.major}.{version.minor}.{version.micro} - 不符合要求，至少需要 3.10")
  return False

def install_dependencies():
  """从版本依赖文件安装课程依赖"""
  requirements = Path(__file__).resolve().parents[1] / "requirements.txt"
  print(f"正在安装 {requirements} 中列出的依赖...")
  # subprocess.check_all(
  #   [sys.executable, "-m", "pip", "install", "-r", str(requirements)]
  # )
  # print("\n✅ 所有依赖安装完成！")

check_python_version()
install_dependencies()