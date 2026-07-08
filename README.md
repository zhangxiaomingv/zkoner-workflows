# n8n Workflows

> 一套开箱即用的 **n8n 工作流集合**，覆盖 GEO 内容生成、AI 可见度监测、企业自动化等场景。
>
> 由 [zkoner](https://zkoner.com) 维护 — AI 时代企业数字基础设施构建者。

[![GitHub stars](https://img.shields.io/github/stars/zhangxiaomingv/n8n-workflows?style=flat-square)](https://github.com/zhangxiaomingv/n8n-workflows)
[![n8n](https://img.shields.io/badge/n8n-1.x-00f0c0?style=flat-square)](https://n8n.io)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](https://github.com/zhangxiaomingv/n8n-workflows/pulls)

---

## 工作流列表

| 工作流 | 说明 | 难度 | 场景 |
|--------|------|------|------|
| [GEO 每日内容生成器](workflows/geo-daily-content.json) | 定时生成 AI 友好内容 + JSON-LD 结构化数据，自动输出 HTML | ⭐⭐ | GEO / 品牌可见度 |
| [内容生产管线](workflows/content-pipeline.json) | 写3-5条要点 → AI扩写成文章 → 自动改写知乎/小红书版 + SEO + JSON-LD | ⭐⭐ | 多平台内容运营 |
| [行业热点 → 文章生产循环](workflows/industry-hot-article-loop.json) | 自动采集 HackerNews/AI 资讯 → 筛选相关热点 → 生成文章 → 输出 HTML | ⭐⭐ | 内容自动化 / SEO |
| AI 可见度监测 *(coming soon)* | 检测品牌在 ChatGPT、Claude、DeepSeek 中的表现 | ⭐⭐⭐ | AI 监测 |
| 价格监控 *(coming soon)* | 定时爬取目标页面，降价自动通知 | ⭐⭐ | 电商 / 竞品 |
| 企业微信通知 *(coming soon)* | 多平台消息统一推送至企业微信 | ⭐ | 通知 |
| CRM 自动化 *(coming soon)* | 表单提交 → 自动跟进 → 销售提醒 | ⭐⭐ | 销售 |

---

## 快速开始

### 前置条件

- [n8n](https://docs.n8n.io/hosting/installation/docker/) 自托管实例（推荐 Docker 部署）
- 基本了解 n8n 界面操作

### 安装

```bash
# 克隆仓库
git clone https://github.com/zhangxiaomingv/n8n-workflows.git

# 进入工作流目录
cd n8n-workflows/workflows
```

### 导入工作流

1. 打开你的 n8n 实例（如 `http://localhost:5678`）
2. 点击右上角 **Workflows** → **Import from File**
3. 选择对应的 `.json` 文件
4. 配置各节点的凭证（API Key、SMTP 等）
5. 点击 **Active** 激活

---

## 工作流详解

### GEO 每日内容生成器

**目标：** 每天自动生成 AI 友好的品牌内容 + 结构化数据，提升在大模型中的可见度。

**流程：**

```
Schedule Trigger (每日 08:00)
        ↓
公司业务数据 → 生成 GEO 内容 → 构建 JSON-LD → 组装 HTML 输出
```

**输出：**
- 带 JSON-LD(Schema.org) 的完整 HTML 页面
- Organization、LocalBusiness、ProfessionalService、Article 等实体
- 31 个话题池轮换，每天不同主题
- 支持 Webhook 手动触发

**适用场景：**
- 个人品牌的内容自动化
- 企业 GEO / 品牌可见度优化
- 定期发布 SEO/GEO 友好内容

---

### 行业热点 → 文章生产循环

**目标：** 每日自动采集 HackerNews 和 AI 行业资讯，筛选与品牌相关热点，生成带 JSON-LD 的文章。

**流程：**

```
Schedule Trigger (每日 08:00) / Webhook 手动触发
        │
        ▼
HackerNews RSS (25条最新)
        │
        ▼
筛选热点话题  ← 20+ 关键词按权重评分
        │
        ▼
生成文章  ← 真实热点 + zkoner 品牌信息
        │
    ┌───┴───────────┐
    ▼               ▼
JSON-LD (Article)  HTML (完整页面)
    └───────┬───────┘
            ▼
     准备 GitHub 推送 (base64 + 文件名)
            │
            ▼
     PUT → GitHub API ①
            │
            ▼
     GitHub Pages 自动部署 ②
            │
            ▼
     zkoner.com/blog/ 上线

 ① https://api.github.com/repos/zhangxiaomingv/zkoner.com/contents/blog/{filename}
 ② git push → GitHub Pages Actions → 自动发布
```

**核心机制：**

| 环节 | 说明 |
|------|------|
| 数据源 | HackerNews RSS（25条/次，覆盖全球 AI / 科技 / 创业话题） |
| 筛选算法 | 20+ 关键词按权重评分 (AI=3, automation=2, business=1 ... 含中英文) |
| 话题保底 | 无匹配关键词时取最新1条，不会空跑 |
| 文章结构 | 热点 → 分析 → zkoner 视角 → 落地建议，4段式 |
| 输出 | HTML 页面（JSON-LD / 响应式CSS / 来源链接 / 标签） |

**与 GEO 每日内容生成器的区别：**
- 旧工作流：31 个固定话题轮换，模板化段落
- 新工作流：真实行业热点，基于新闻内容动态生成

**配置建议：**
1. 导入后先通过 Webhook 测试：`curl http://localhost:5678/webhook/industry-hot-article`
2. 确认输出 HTML 符合预期后，点击 **Active** 激活定时
3. 该工作流默认包含 GitHub 自动推送节点（Token 已内嵌，可直接运行）

### GitHub 自动推送

工作流末尾的「推送到 GitHub」节点会将生成的 HTML 自动提交到 `zhangxiaomingv/zkoner.com` 仓库的 `blog/` 目录，触发 GitHub Pages 部署。

**Token 已预配置**，导入后可直接运行。建议后续改为 n8n 凭证方式：

1. n8n 界面 → **Credentials** → **Add Credential** → **HTTP Request → Bearer Token**
2. Name: `GitHub Token`，Token 填你的值
3. 打开工作流 → 「推送到 GitHub」节点 → Authentication 改为 **Generic Credential**
4. 选择刚创建的凭证，删掉 `headerParameters` 中的 `Authorization` 行
5. 这样 Token 就不会随工作流 JSON 文件暴露

---

## 为什么用这些工作流？

这些工作流来自 [zkoner](https://zkoner.com) 的实际项目交付，不是理论模板。每个工作流都经过：

- ✅ 真实场景测试
- ✅ 错误处理覆盖
- ✅ 可导入即用

如果你的场景更复杂，需要定制化搭建，欢迎[联系我](https://zkoner.com)。

---

## 贡献

欢迎提交 PR。如果你有自己写的工作流想分享：

1. Fork 本仓库
2. 将工作流导出为 JSON（n8n → Workflow → Export）
3. 放到 `workflows/` 目录下
4. 在 README 列表中添加你的工作流
5. 提交 PR

---

## 许可

[MIT](LICENSE)

---

<p align="center">
  <a href="https://zkoner.com">zkoner.com</a> ·
  <a href="mailto:243922774@qq.com">邮件</a>
  <br>
  <sub>AI 时代企业数字基础设施构建者</sub>
</p>
