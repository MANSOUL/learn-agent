import json

def demonstrate_tool_design():
    """演示高质量工具定义 vs 低质量工具定义。"""
    print("=" * 60)
    print("  工具设计对比：好 vs 坏")
    print("=" * 60)

    bad_tool = {
        "type": "function",
        "function": {
            "name": "do_stuff",
            "description": "处理数据。",
            "parameters": {
                "type": "object",
                "properties": {"data": {"type": "string"}},
            },
        },
    }

    good_tool = {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": (
                "向指定邮箱发送邮件。适用于发送通知、报告、提醒等场景。"
                "不支持发送带附件的邮件。收件人地址必须包含 @。"
                "示例：send_email(to='user@example.com', "
                "subject='日报', body='今日数据...')"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "收件人邮箱地址，如 user@example.com",
                    },
                    "subject": {
                        "type": "string",
                        "description": "邮件主题，不超过 100 字",
                    },
                    "body": {
                        "type": "string",
                        "description": "邮件正文，纯文本格式",
                    },
                },
                "required": ["to", "subject", "body"],
            },
        },
    }

    print("\n❌ 低质量工具定义：")
    print(json.dumps(bad_tool, indent=2, ensure_ascii=False))

    print("\n✅ 高质量工具定义：")
    print(json.dumps(good_tool, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    demonstrate_tool_design()