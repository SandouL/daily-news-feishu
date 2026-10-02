import os
import requests

# 每个平台取多少条
LIMIT = 8
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
HEADERS = {"User-Agent": UA}


# ---------- 各平台抓取：返回 [(title, url, extra), ...] ----------
def fetch_bilibili():
    url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["data"]["list"][:LIMIT]:
        out.append((x["title"],
                    f"https://www.bilibili.com/video/{x['bvid']}",
                    f"播放 {x.get('play', 0)}"))
    return out


def fetch_baidu():
    url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    items = d["data"]["cards"][0]["content"][0]["content"]
    out = []
    for x in items:
        if x.get("isTop"):  # 跳过置顶宣传条
            continue
        word = x.get("word")
        link = x.get("url")
        if word and link:
            tag = x.get("hotTag", "")
            out.append((word, link, tag))
        if len(out) >= LIMIT:
            break
    return out


def fetch_toutiao():
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["data"][:LIMIT]:
        cid = x.get("ClusterId")
        out.append((x["Title"],
                    f"https://www.toutiao.com/trending/{cid}/",
                    f"热度 {x.get('HotValue', '')}"))
    return out


def fetch_sspai():
    url = ("https://sspai.com/api/v1/article/index/page/get"
           "?limit=%d&offset=0&created_at=0" % LIMIT)
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["data"][:LIMIT]:
        out.append((x["title"],
                    f"https://sspai.com/post/{x['id']}",
                    ""))
    return out


def fetch_juejin():
    url = ("https://api.juejin.cn/content_api/v1/content/article_rank"
           "?category_id=1&type=hot")
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["data"][:LIMIT]:
        c = x["content"]
        out.append((c["title"],
                    f"https://juejin.cn/post/{c['content_id']}",
                    f"热度 {x.get('content_counter', {}).get('hot_rank', '')}"))
    return out


def fetch_zhihu_daily():
    url = "https://daily.zhihu.com/api/4/news/latest"
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["stories"][:LIMIT]:
        out.append((x["title"],
                    f"https://daily.zhihu.com/story/{x['id']}",
                    ""))
    return out


def fetch_ithome():
    url = "https://api.ithome.com/json/newslist/news"
    d = requests.get(url, headers=HEADERS, timeout=15).json()
    out = []
    for x in d["newslist"][:LIMIT]:
        link = x.get("url", "")
        if link.startswith("/"):
            link = "https://www.ithome.com" + link
        out.append((x["title"], link, ""))
    return out


# ---------- 聚合 ----------
PLATFORMS = [
    ("🎬 B站热榜", fetch_bilibili),
    ("🔍 百度热搜", fetch_baidu),
    ("📰 今日头条", fetch_toutiao),
    ("📱 少数派", fetch_sspai),
    ("💻 掘金热榜", fetch_juejin),
    ("📖 知乎日报", fetch_zhihu_daily),
    ("⚙️ IT之家", fetch_ithome),
]


def build_content():
    content = []
    for name, fn in PLATFORMS:
        content.append([{"tag": "text", "text": f"\n{name}"}])
        try:
            rows = fn()
            if not rows:
                content.append([{"tag": "text", "text": "  暂无数据"}])
            for i, (title, link, extra) in enumerate(rows, 1):
                line = [{"tag": "text", "text": f"{i}. "},
                        {"tag": "a", "text": title, "href": link}]
                if extra:
                    line.append({"tag": "text", "text": f"  ({extra})"})
                content.append(line)
        except Exception as e:
            content.append([{"tag": "text", "text": f"  获取失败：{e}"}])
    return content


def send_feishu(content):
    webhook = os.getenv("FEISHU_WEBHOOK")
    if not webhook:
        print("未配置 FEISHU_WEBHOOK，仅本地预览")
        return
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "📰 每日多平台热榜汇总",
                    "content": content,
                }
            }
        },
    }
    r = requests.post(webhook, json=payload, timeout=15)
    print("飞书返回：", r.json())


if __name__ == "__main__":
    content = build_content()
    send_feishu(content)
