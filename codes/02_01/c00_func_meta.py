import inspect

def func_meta_demo(arg1: str, arg2: int) -> str:
    """获取函数元信息

    Args:
        arg1: 参数1
        arg2: 参数2
    Returns:
        返回参数1
    """
    return arg1

print(func_meta_demo.__name__)
print(func_meta_demo.__doc__)
print(func_meta_demo.__annotations__)

print("\n----\n")

sig = inspect.signature(func_meta_demo)
print(sig)  
print(sig.parameters)  

for name, param in sig.parameters.items():
    print(f"参数名: {name}")
    print(f"  类型: {param.annotation}") 
    print(f"  默认值: {param.default}")
