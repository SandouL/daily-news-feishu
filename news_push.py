import os
import requests

def get_zhihu_hot():
    """知乎热榜"""
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=8"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    lines = []
    for idx, item in enumerate(data["data"], start=1):
        title = item["target"]["title"]
        link = "https://www.zhihu.com/question/" + str(item["target"]["id"])
        hot = item["target"]["metrics"]["hot_score"]
        lines.append(f"{idx}. {title} | 热度:{hot} | {link}")
    return "【知乎热榜】\n" + "\n".join(lines)


def get_weibo_hot():
    """微博热搜"""
    url = "https://weibo.com/ajax/side/hotSearch"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    lines = []
    for idx, item in enumerate(data["data"]["realtime"][:8], start=1):
        title = item["word"]
        link = f"https://s.weibo.com/weibo?q={item['word']}"
        hot = item.get("num", "")
        lines.append(f"{idx}. {title} | 热度:{hot} | {link}")
    return "\n\n【微博热搜】\n" + "\n".join(lines)


def get_baidu_hot():
    """百度热搜"""
    url = "https://api.toutiaoapi.com/api/feed/top_search/v1/"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    lines = []
    for idx, item in enumerate(data["data"][:8], start=1):
        title = item["title"]
        link = item["url"]
        lines.append(f"{idx}. {title} | {link}")
    return "\n\n【百度热搜】\n" + "\n".join(lines)


def get_bilibili_hot():
    """B站热榜"""
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    lines = []
    for idx, item in enumerate(data["data"]["list"][:8], start=1):
        title = item["title"]
        link = item["short_link_v2"]
        play = item["play"]
        lines.append(f"{idx}. {title} | 播放:{play} | {link}")
    return "\n\n【B站热榜】\n" + "\n".join(lines)


def get_juejin_hot():
    """掘金热榜"""
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_hot_list?sort_type=1&page_size=8&cursor=0"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.post(url, headers=headers, timeout=10, json={"id_type":2,"sort_type":1,"page_size":8,"cursor":"0"})
    data = resp.json()
    lines = []
    for idx, item in enumerate(data["data"], start=1):
        title = item["article_info"]["title"]
        link = f"https://juejin.cn/post/{item['article_info']['article_id']}"
        view = item["article_info"]["view_count"]
        lines.append(f"{idx}. {title} | 阅读:{view} | {link}")
    return "\n\n【掘金热榜】\n" + "\n".join(lines)


def get_all_hot_content():
    """聚合全部平台，异常捕获，单个平台抓取失败不影响整体推送"""
    content = ""
    try:
        content += get_zhihu_hot()
    except Exception as e:
        content += "\n【知乎热榜】抓取失败：" + str(e)
    try:
        content += get_weibo_hot()
    except Exception as e:
        content += "\n\n【微博热搜】抓取失败：" + str(e)
    try:
        content += get_baidu_hot()
    except Exception as e:
        content += "\n\n【百度热搜】抓取失败：" + str(e)
    try:
        content += get_bilibili_hot()
    except Exception as e:
        content += "\n\n【B站热榜】抓取失败：" + str(e)
    try:
        content += get_juejin_hot()
    except Exception as e:
        content += "\n\n【掘金热榜】抓取失败：" + str(e)
    return content


def send_feishu_post(title: str, body_text: str):
    webhook = os.getenv("FEISHU_WEBHOOK")
    if not webhook:
        print("错误：未读取到 FEISHU_WEBHOOK 环境变量")
        return

    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": [
                        [
                            {"tag": "text", "text": body_text}
                        ]
                    ]
                }
            }
        }
    }
    resp = requests.post(webhook, json=payload, timeout=15)
    result = resp.json()
    print("飞书接口返回：", result)
    return result


if __name__ == "__main__":
    full_text = get_all_hot_content()
    send_feishu_post("📰 多平台每日热榜汇总", full_text)
