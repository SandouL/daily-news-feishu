import os
import requests

def get_zhihu_hot():
    url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=8"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    data_list = data.get("data", [])
    lines = []
    for idx, item in enumerate(data_list, start=1):
        target = item.get("target", {})
        title = target.get("title", "")
        qid = target.get("id", "")
        hot_score = target.get("metrics", {}).get("hot_score", "")
        if not title:
            continue
        link = f"https://www.zhihu.com/question/{qid}"
        lines.append(f"{idx}. {title} | 热度:{hot_score} | {link}")
    return "【知乎热榜】\n" + "\n".join(lines)


def get_weibo_hot():
    url = "https://weibo.com/ajax/side/hotSearch"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    realtime_list = data.get("data", {}).get("realtime", [])
    lines = []
    for idx, item in enumerate(realtime_list[:8], start=1):
        word = item.get("word", "")
        hot_num = item.get("num", "")
        if not word:
            continue
        link = f"https://s.weibo.com/weibo?q={word}"
        lines.append(f"{idx}. {word} | 热度:{hot_num} | {link}")
    return "\n\n【微博热搜】\n" + "\n".join(lines)


def get_baidu_hot():
    url = "https://api.toutiaoapi.com/api/feed/top_search/v1/"
    resp = requests.get(url, timeout=10)
    data = resp.json()
    data_list = data.get("data", [])
    lines = []
    for idx, item in enumerate(data_list[:8], start=1):
        title = item.get("title", "")
        link = item.get("url", "")
        if not title:
            continue
        lines.append(f"{idx}. {title} | {link}")
    return "\n\n【百度热搜】\n" + "\n".join(lines)


def get_bilibili_hot():
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()
    list_data = data.get("data", {}).get("list", [])
    lines = []
    for idx, item in enumerate(list_data[:8], start=1):
        title = item.get("title", "")
        short_link = item.get("short_link_v2", "")
        play = item.get("play", "")
        if not title:
            continue
        lines.append(f"{idx}. {title} | 播放:{play} | {short_link}")
    return "\n\n【B站热榜】\n" + "\n".join(lines)


def get_juejin_hot():
    url = "https://api.juejin.cn/recommend_api/v1/article/recommend_hot_list?sort_type=1&page_size=8&cursor=0"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.post(url, headers=headers, timeout=10, json={"id_type":2,"sort_type":1,"page_size":8,"cursor":"0"})
    data = resp.json()
    data_list = data.get("data", [])
    lines = []
    for idx, item in enumerate(data_list, start=1):
        article_info = item.get("article_info", {})
        title = article_info.get("title", "")
        aid = article_info.get("article_id","")
        view = article_info.get("view_count","")
        if not title:
            continue
        link = f"https://juejin.cn/post/{aid}"
        lines.append(f"{idx}. {title} | 阅读:{view} | {link}")
    return "\n\n【掘金热榜】\n" + "\n".join(lines)


def get_all_hot_content():
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
