import os
import requests

API_BASE = "https://hot.imsyy.top/api"

def get_hot_list(platform_type: str, name: str) -> list:
    """调用三方聚合接口获取单平台热榜，返回飞书post内容块"""
    content_blocks = []
    try:
        resp = requests.get(f"{API_BASE}?type={platform_type}", timeout=15)
        data = resp.json()
        list_data = data.get("data", [])
        for idx, item in enumerate(list_data[:8], start=1):
            title = item.get("title", "")
            link = item.get("url", "")
            hot_val = item.get("hot", "")
            if not title or not link:
                continue
            content_blocks.append([
                {"tag": "text", "text": f"{idx}. "},
                {"tag": "a", "text": title, "href": link},
                {"tag": "text", "text": f" | 热度:{hot_val}"}
            ])
        if len(content_blocks) == 0:
            content_blocks.append([{"tag": "text", "text": f"{name} 暂无数据或接口返回为空"}])
    except Exception as e:
        content_blocks.append([{"tag": "text", "text": f"{name} 获取失败：{str(e)}"}])
    return content_blocks


def send_feishu_post(all_blocks):
    webhook = os.getenv("FEISHU_WEBHOOK")
    if not webhook:
        print("FEISHU_WEBHOOK 环境变量未配置")
        return

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "📰 多平台每日热榜汇总",
                    "content": all_blocks
                }
            }
        }
    }
    res = requests.post(webhook, json=payload, timeout=15)
    print("飞书返回：", res.json())


if __name__ == "__main__":
    full_content = []
    # 平台映射：接口type / 显示名称
    sources = [
        ("zhihu", "【知乎热榜】"),
        ("weibo", "【微博热搜】"),
        ("baidu", "【百度热搜】"),
        ("bilibili", "【B站热榜】"),
        ("juejin", "【掘金热榜】"),
    ]
    for api_type, show_name in sources:
        # 平台标题行
        full_content.append([{"tag": "text", "text": f"\n{show_name}\n"}])
        # 榜单条目
        block_list = get_hot_list(api_type, show_name)
        full_content.extend(block_list)

    send_feishu_post(full_content)
