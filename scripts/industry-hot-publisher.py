#!/usr/bin/env python3
"""
zkoner 行业热点 → 文章生产循环  (独立脚本版)

功能: 采集 HackerNews RSS → 筛选 AI/自动化 热点 → 生成文章 → 推送到 GitHub

定时: 配合 cron, 添加到 crontab:
  0 8 * * * cd /home/zxm/n8n-workflows && python3 scripts/industry-hot-publisher.py >> scripts/publish.log 2>&1

手动执行:
  python3 scripts/industry-hot-publisher.py
"""

import json
import os
import re
import base64
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import requests
from bs4 import BeautifulSoup

# ── 配置 ──────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "YOUR_GITHUB_TOKEN")
GITHUB_REPO = "zhangxiaomingv/zkoner.com"
GITHUB_BRANCH = "main"
GITHUB_API = f"https://api.github.com/repos/{GITHUB_REPO}/contents/blog"

RSS_URLS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "https://feeds.bbci.co.uk/news/technology/rss.xml",
]
HEADERS = {"User-Agent": "zkoner-bot/1.0"}

# 品牌数据
BRAND = {
    "name": "zkoner",
    "shortDesc": "AI 时代企业数字基础设施构建者",
    "founder": "张明夷",
    "email": "243922774@qq.com",
    "phone": "19136166195",
    "location": "成都",
    "services": [
        "AI Visibility System — 品牌 AI 可见性诊断与结构化数据建设",
        "AI Automation System — n8n/Agent/API 自动化工作流搭建",
        "AI Growth System — AI 获客与潜客分析系统",
    ],
}

# 关键词权重
KEYWORDS = {
    "AI": 3, "artificial intelligence": 3, "LLM": 3, "GPT": 3,
    "large language model": 3, "ChatGPT": 3, "Claude": 3, "DeepSeek": 3,
    "automation": 2, "workflow": 2, "agent": 2, "n8n": 2,
    "SEO": 2, "GEO": 3, "generative engine": 3,
    "startup": 1, "business": 1, "enterprise": 1,
    "knowledge graph": 3, "structured data": 3, "schema.org": 3,
    "search": 1, "ranking": 1, "visibility": 2,
    "growth": 1, "marketing": 1, "content": 1,
    "创业": 2, "企业": 2, "数字化": 2, "自动化": 3, "人工智能": 3,
}


# ── RSS 采集 ──────────────────────────────────────────────────────

def fetch_rss(urls: list[str]) -> list[dict]:
    items = []
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=15)
            r.raise_for_status()
        except Exception as e:
            print(f"  [WARN] RSS 获取失败 ({url}): {e}", file=sys.stderr)
            continue

        soup = BeautifulSoup(r.text, "xml")
        for item in soup.select("item"):
            items.append({
                "title": item.find("title").text if item.find("title") else "",
                "link": item.find("link").text if item.find("link") else "",
                "description": BeautifulSoup(item.find("description").text if item.find("description") else "", "html.parser").get_text()[:300],
                "isoDate": item.find("pubDate").text if item.find("pubDate") else "",
            })
        print(f"  {url.split('/')[2]}: {len(soup.select('item'))} 条")
    return items


# ── 筛选热点 ──────────────────────────────────────────────────────

def score_topics(items: list[dict]) -> dict | None:
    scored = []
    for item in items:
        text = (item["title"] + " " + item["description"]).lower()
        score = 0
        matched = []
        for kw, weight in KEYWORDS.items():
            if kw in text:
                score += weight
                matched.append(kw)
        scored.append({**item, "score": score, "matchedKeywords": matched[:8]})

    scored.sort(key=lambda x: x["score"], reverse=True)
    top = [s for s in scored if s["score"] > 0]
    return top[0] if top else (scored[0] if scored else None)


# ── 生成文章 ──────────────────────────────────────────────────────

def generate_article(topic: dict | None) -> dict:
    now = datetime.now()
    date_str = f"{now.year}年{now.month}月{now.day}日"
    iso_str = now.isoformat()

    hot_title = topic["title"][:80] + ("..." if len(topic["title"]) > 80 else "") if topic else "AI 行业最新动态"
    hot_snippet = topic.get("description", "") if topic else ""
    hot_link = topic.get("link", "") if topic else ""

    title = f"行业观察：{hot_title} | zkoner"

    sections = [
        {
            "heading": "📰 本期热点",
            "body": f"近日，{hot_title}。\n\n{hot_snippet}\n\n📍 来源：{hot_link or '行业资讯'}",
            "type": "news",
        },
        {
            "heading": "🔍 为什么这值得关注？",
            "body": "这一趋势正在影响企业数字基础设施的构建方式。对于中小企业、创业者和一人公司来说，理解并跟上这些变化，意味着能够在 AI 时代保持竞争力。",
            "type": "analysis",
        },
        {
            "heading": "💡 zkoner 的视角",
            "body": "作为 AI 时代企业数字基础设施构建者，zkoner 持续跟踪行业趋势，将其融入核心系统：\n"
            + "\n".join(f"• {s}" for s in BRAND["services"])
            + "\n\n我们认为，每个企业都应该建立属于自己的 AI 可理解身份，而不是被动等待技术浪潮的冲击。",
            "type": "perspective",
        },
        {
            "heading": "✅ 如何落地？",
            "body": "第一步：评估你的品牌在 AI 中的认知现状\n"
            "第二步：构建结构化的品牌知识体系\n"
            "第三步：用自动化工作流持续运营内容\n"
            "第四步：建立监测循环，持续优化 AI 可见度",
            "type": "action",
        },
    ]

    return {
        "title": title,
        "sections": sections,
        "hotTopic": hot_title,
        "hotLink": hot_link,
        "date_full": date_str,
        "date_iso": iso_str,
        "author": BRAND["founder"],
        "tags": ["行业热点", "AI", "企业自动化", "GEO", "zkoner"],
    }


# ── 构建 HTML ─────────────────────────────────────────────────────

def build_html(article: dict) -> str:
    body = ""
    for s in article["sections"]:
        body += f'''<section class="section-{s['type']}">
  <h2>{s['heading']}</h2>
  <p>{s['body'].replace(chr(10)+chr(10), '</p><p>').replace(chr(10), '<br>')}</p>
</section>
'''

    source_html = ""
    if article["hotLink"]:
        link = article["hotLink"].replace("https://", "")[:50]
        source_html = f'<p style="font-size:0.75rem;color:#4a4a60;">📡 话题来源：<a href="{article["hotLink"]}" target="_blank" rel="noopener" style="color:#00a080;">{link}</a></p>'

    tags_html = "".join(
        f'<span style="font-family:monospace;font-size:0.62rem;padding:3px 8px;border-radius:4px;background:rgba(124,92,252,0.08);color:#7c5cfc;border:1px solid rgba(124,92,252,0.12);">{t}</span>'
        for t in article["tags"]
    )

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{article["title"]}</title>
<meta name="description" content="{article["hotTopic"][:120]}">
<link rel="canonical" href="https://zkoner.com/blog/">
<style>
body{{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",Roboto,"Noto Sans SC",sans-serif;background:#07070a;color:#e2e2ea;max-width:720px;margin:40px auto;padding:0 20px;line-height:1.8;}}
h1{{font-size:1.6rem;font-weight:650;letter-spacing:-0.5px;margin-bottom:8px;}}
.meta{{color:#4a4a60;font-size:0.82rem;margin-bottom:32px;}}
section{{margin-bottom:28px;padding:20px;border:1px solid #1a1a30;border-radius:8px;background:#0c0c14;}}
.section-news{{border-left:3px solid #7c5cfc;}}
.section-analysis{{border-left:3px solid #00f0c0;}}
.section-perspective{{border-left:3px solid #ffb74d;}}
.section-action{{border-left:3px solid #ff5f56;}}
h2{{font-size:1rem;font-weight:600;color:#00f0c0;margin-bottom:8px;}}
p{{color:#7a7a90;font-size:0.9rem;line-height:1.8;margin-bottom:8px;}}
a{{color:#00f0c0;}}
.footer{{margin-top:40px;padding:24px;border-top:1px solid #1a1a30;text-align:center;}}
.tags{{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0 16px;}}
</style>
</head>
<body>

<h1>{article["title"]}</h1>
<div class="meta">{article["date_full"]} · {article["author"]}</div>
<div class="tags">{tags_html}</div>
{source_html}
{body}
<div class="footer">
<p><strong style="color:#00f0c0;">zkoner</strong><br>AI 时代企业数字基础设施构建者</p>
<p style="margin-top:8px;font-size:0.8rem;">{article["author"]} · {BRAND["email"]} · {BRAND["phone"]}</p>
<p style="font-size:0.75rem;color:#4a4a60;">成都 · 中国 | <a href="https://zkoner.com">zkoner.com</a></p>
</div>

</body>
</html>'''


# ── JSON-LD ───────────────────────────────────────────────────────

def build_jsonld(article: dict) -> str:
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article["title"],
        "datePublished": article["date_iso"],
        "dateModified": article["date_iso"],
        "author": {"@type": "Person", "name": article["author"]},
        "publisher": {"@type": "Organization", "name": "zkoner", "url": "https://zkoner.com"},
        "about": {"@type": "Thing", "name": article["hotTopic"]},
        "keywords": ", ".join(article["tags"]),
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


# ── 推送到 GitHub ────────────────────────────────────────────────

def push_to_github(html_with_ld: str, article: dict) -> bool:
    # 生成文件名
    slug = re.sub(r'[^a-zA-Z0-9一-鿿-]', '', article["hotTopic"][:40].replace(' ', '-'))
    filename = f'{datetime.now().strftime("%Y-%m-%d")}-{slug}.html'

    # base64
    content_b64 = base64.b64encode(html_with_ld.encode("utf-8")).decode("utf-8")

    # GitHub API
    payload = {
        "message": f"auto: {article['title'][:80]}",
        "content": content_b64,
        "branch": GITHUB_BRANCH,
    }

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.put(
            f"{GITHUB_API}/{filename}",
            headers=headers,
            json=payload,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            print(f"  ✅ 推送到 GitHub: blog/{filename}")
            return True
        else:
            print(f"  ❌ GitHub API 错误 ({resp.status_code}): {resp.json().get('message', '')}", file=sys.stderr)
            return False
    except Exception as e:
        print(f"  ❌ GitHub 请求失败: {e}", file=sys.stderr)
        return False


# ── 主流程 ────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*50}")
    print(f"  zkoner 行业热点 → 文章生产")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")

    # Step 1: RSS 采集
    print(f"\n📡 采集行业资讯 ...")
    items = fetch_rss(RSS_URLS)
    print(f"  合计: {len(items)} 条")

    if not items:
        print("  ❌ 没有获取到任何内容", file=sys.stderr)
        sys.exit(1)

    # Step 2: 筛选热点
    print(f"\n🔍 筛选热点话题 ...")
    topic = score_topics(items)
    if topic:
        print(f"  最高分: {topic['score']} 分 — {topic['title'][:60]}")
    else:
        print(f"  ⚠ 无匹配，取最新一条保底")
        topic = items[0]

    # Step 3: 生成文章
    print(f"\n📝 生成文章 ...")
    article = generate_article(topic)
    print(f"  标题: {article['title'][:60]}")

    # Step 4: 构建 HTML + JSON-LD
    print(f"\n🔧 构建输出 ...")
    html = build_html(article)
    jsonld = build_jsonld(article)
    html_with_ld = html.replace("</head>", f'<script type="application/ld+json">{jsonld}</script>\n</head>')
    print(f"  HTML: {len(html_with_ld)} bytes")
    print(f"  JSON-LD: ✓")

    # Step 5: 推送到 GitHub
    print(f"\n🚀 推送到 GitHub ...")
    ok = push_to_github(html_with_ld, article)

    print(f"\n{'='*50}")
    if ok:
        print(f"  ✅ 完成! 文章已发布到 zkoner.com/blog/")
    else:
        print(f"  ⚠ 文章已生成但推送失败。HTML 保存在本地:")
        local_path = Path(__file__).parent / "last-article.html"
        local_path.write_text(html_with_ld, encoding="utf-8")
        print(f"      {local_path}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    main()
