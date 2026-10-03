import os
demo_path = os.path.realpath(
    os.path.join(
        "/Users/kuangguanghu/workspace/learn-agent/projects/", "../projects_demo"
    )
)
# print("当前工作目录:", os.getcwd())
# print("当前目录下的文件和子目录:", os.listdir(demo_path))
print(demo_path)
print(os.path.relpath(demo_path, start='/Users/kuangguanghu/workspace/learn-agent/projects/'))
