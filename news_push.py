import requests
import json
import os

FEISHU_WEBHOOK = os.getenv("FEISHU_WEBHOOK")

def fetch_wb_hot():
    try:
        headers = {"User-Agent":"Mozilla/5.0","Referer":"https://s.weibo.com/"}
        r = requests.get("https://api.weibo.cn/2/guest/search/hot/word",headers=headers,timeout=10)
        data = r.json()
        lst = []
        for item in data.get("data",{}).get("hotword",[]):
            word = item.get("word")
            if word: lst.append(word)
        return "【微博热搜】\n" + "\n".join([f"{i+1}. {x}" for i,x in enumerate(lst[:10])])
    except Exception as e:
        return "【微博热搜】获取失败"

def fetch_baidu_hot():
    try:
        r = requests.get("https://api.caiyunapp.com/v2/baidu_hot",timeout=10)
        data = r.json()
        lst = []
        for item in data.get("result",[]):
            lst.append(item.get("title"))
        return "【百度热榜】\n" + "\n".join([f"{i+1}. {x}" for i,x in enumerate(lst[:10])])
    except Exception as e:
        return "【百度热榜】获取失败"

def fetch_toutiao_hot():
    try:
        r = requests.get("https://api.toutiaoapi.com/api/feed/hotboard",timeout=10)
        data = r.json()
        lst = []
        for item in data.get("data",[]):
            lst.append(item.get("title"))
        return "【头条热榜】\n" + "\n".join([f"{i+1}. {x}" for i,x in enumerate(lst[:10])])
    except Exception as e:
        return "【头条热榜】获取失败"

def fetch_60s():
    try:
        r = requests.get("https://api.60s.ink/v1/api/today",timeout=10)
        data = r.json()
        news = data.get("news","")
        return "【60s新闻速览】\n" + news
    except Exception as e:
        return "【60s新闻速览】获取失败"

def push_feishu(content):
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": "📰 每日全行业热榜简报",
                    "content": [
                        [{"tag":"lark_md","text":content}]
                    ]
                }
            }
        }
    }
    headers = {"Content-Type":"application/json;charset=utf-8"}
    resp = requests.post(FEISHU_WEBHOOK,json=payload,headers=headers,timeout=15)
    res = resp.json()
    if res.get("code") ==0:
        print("✅飞书推送成功")
    else:
        print(f"❌推送失败:{res}")

if __name__ == "__main__":
    if not FEISHU_WEBHOOK:
        print("缺少FEISHU_WEBHOOK环境变量")
        exit(1)
    parts = []
    parts.append(fetch_wb_hot())
    parts.append(fetch_baidu_hot())
    parts.append(fetch_toutiao_hot())
    parts.append(fetch_60s())
    full_text = "\n\n".join(parts)
    push_feishu(full_text)
