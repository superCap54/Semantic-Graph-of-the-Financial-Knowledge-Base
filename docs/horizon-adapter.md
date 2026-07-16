# Horizon Adapter 设计

## 为什么先写 adapter 设计

Horizon 是第一阶段采集主入口，但本项目不直接嵌入 Horizon 代码。Horizon 独立运行，输出 Markdown 报告；本项目读取报告并编译为 Obsidian 知识库。

这不是不实现 Horizon adapter，而是把边界先定清楚：

- Horizon 负责采集和聚合。
- 本项目负责证据保存、分析、去重、事件合并、Obsidian 编译。

当前已经实现最小导入命令：

```bash
sgkb import-horizon path/to/horizon-report.md --query "华大基因"
```

它会先把 Horizon Markdown 报告保存进 `raw/horizon-reports/`。

真正的新闻拆分解析器需要一份实际 Horizon Markdown 输出样例。拿到样例后，下一步 adapter 会实现：

```text
import-horizon <report.md>
-> raw/horizon-reports/
-> raw/news/
```

## 输入

Horizon 生成的 Markdown 报告。

建议用户把报告放到：

```text
raw/horizon-reports/
```

或通过命令导入：

```bash
sgkb import-horizon path/to/horizon-report.md --query "华大基因"
```

## 输出 1：保留原始报告

原始报告保存为：

```text
raw/horizon-reports/YYYY-MM-DD 查询词 Horizon报告.md
```

## 输出 2：拆分新闻卡片

每条新闻拆成：

```text
raw/news/YYYY-MM-DD 新闻标题.md
```

内部 frontmatter 使用英文：

```yaml
---
source_adapter: horizon
query: 华大基因
title: 新闻标题
source_name: 来源名
url: https://example.com
published_at:
captured_at: 2026-07-16T00:00:00+08:00
source_tier: unknown
evidence_type: news
status: raw
---
```

正文使用中文：

```md
# 新闻标题

## 摘要

## 关键摘录

## 来源

- 原始 Horizon 报告：[[YYYY-MM-DD 华大基因 Horizon报告]]
- 原文链接：
```

## 下一步实现需要的样例

实现解析器前，需要一份真实 Horizon Markdown 输出，确认：

- 每条新闻的标题格式。
- 链接格式。
- 来源字段是否存在。
- 发布时间是否存在。
- 摘要和 AI 评分如何呈现。
- 是否有分组、列表、表格或嵌套结构。

如果 Horizon 输出格式不稳定，第一版 adapter 可以采用 AI 解析：

```text
Horizon Markdown
-> AI 识别新闻条目
-> 输出统一 raw/news 卡片
```

后续再逐步替换为确定性解析。
