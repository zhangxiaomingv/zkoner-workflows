# 行业热点 → 内容生产循环

## 完整循环逻辑

```
每日 08:00 定时触发 ─┐
                      ├──→ HackerNews RSS (25条)
手动触发 (Webhook)  ──┘
                            │
                            ▼
                      筛选热点话题
                      (按 AI/GEO/自动化 等20+关键词加权评分)
                            │
                            ▼
                      生成文章
                      (真实热点标题 + zkoner 品牌数据)
                            │
                    ┌───────┴───────┐
                    ▼               ▼
              构建 JSON-LD      组装 HTML
              (Article Schema)  (完整页面)
                    │               │
                    └───────┬───────┘
                            ▼
                     准备 GitHub 推送
                     (base64 编码 + 文件名生成)
                            │
                            ▼
                     GitHub API: PUT
                     /repos/zhangxiaomingv/zkoner.com/
                       contents/blog/{filename}
                            │
                            ▼
                     GitHub Pages 自动部署
                            │
                            ▼
                     zkoner.com/blog/ 上线
                            │
                            ▼
                     监测系统下次检测到新内容
```

## 与旧工作流的对比

| | `geo-daily-content` | `industry-hot-article-loop` |
|---|---|---|
| 话题来源 | 31个固定话题池轮换 | HackerNews 实时热点 |
| 筛选算法 | 无 (按日期轮转) | 20+关键词加权评分 |
| 内容时效性 | 固定模板 | 基于当日新闻动态生成 |
| 保底机制 | 循环到下一个话题 | 无匹配取最新一条 |
| 自动发布 | 无 (手动部署) | GitHub API 自动推送到仓库 |

## 关键词评分系统

Code 节点中的 `KEYWORDS` 对象控制话题筛选：

```js
权重3: AI / LLM / GPT / ChatGPT / Claude / DeepSeek / GEO / 结构化数据
权重2: automation / workflow / agent / SEO / visibility / 创业 / 数字化
权重1: startup / business / search / growth / marketing / content
```

## GitHub 推送

- **目标仓库**: `zhangxiaomingv/zkoner.com`
- **路径**: `blog/{date}-{slug}.html`
- **API**: `PUT /repos/{owner}/{repo}/contents/{path}`
- **认证**: Bearer Token (需在 n8n Credentials 中配置)
- **Branch**: `main`

## 数据流

```
RSS 条目 → { title, link, contentSnippet, isoDate }
    ↓ 筛选
{ topic: { title, score, matchedKeywords, ... }, runnerUp, totalScanned }
    ↓ 生成
{ title, sections: [], hotTopic, hotLink, date, tags, ... }
    ↓ JSON-LD     ↓ HTML                  ↓ GitHub 准备
{ jsonldArticle }  { html, title, ... } → { apiUrl, githubPayload }
                                            ↓
                                         GitHub API Response
```

## 使用

1. 导入 n8n (Import from File)
2. 在 n8n 中创建 **Bearer Token** 凭证, 填入 GitHub Personal Access Token
3. 将凭证关联到「推送到 GitHub」节点
4. 通过 Webhook 测试:
   ```bash
   curl http://localhost:5678/webhook/industry-hot-article
   ```
5. 检查 GitHub 仓库是否有新提交
6. 确认后点击 **Active** 激活定时
