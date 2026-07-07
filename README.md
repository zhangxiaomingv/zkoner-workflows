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
