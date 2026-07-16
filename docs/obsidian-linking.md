# Obsidian Linking Conventions

## 五类核心词条

词条默认分为五类：

- `company`：公司，如 `[[贵州茅台]]`
- `industry`：行业，如 `[[白酒行业]]`
- `product`：产品，如 `[[飞天茅台]]`
- `event`：事件，如 `[[2026-07-16 贵州茅台渠道调价传闻]]`
- `policy`：政策，如 `[[消费税改革]]`

## 文件位置

```text
knowledge/wiki/companies/
knowledge/wiki/industries/
knowledge/wiki/products/
knowledge/wiki/events/
knowledge/wiki/policies/
```

文件名使用可读中文名，必要时加日期消歧：

```text
knowledge/wiki/events/2026-07-16 贵州茅台渠道调价传闻.md
```

## Frontmatter

每个 wiki 词条都应包含：

```yaml
---
kind: company
aliases: []
tags:
  - finance/company
status: seed
updated_at: 2026-07-16
sources: []
---
```

## 正文结构

建议结构：

```markdown
# 词条名

## 摘要

## 关键事实

## 相关公司

## 相关行业

## 相关产品

## 相关事件

## 相关政策

## 来源

## 待验证
```

## 链接规则

- 所有实体第一次出现时使用 `[[双链]]`。
- 事件名尽量带日期，避免重名。
- 不确定关系写入 `待验证`，不要伪装成事实。
- 每条关键事实后尽量附来源链接或 raw 文件链接。
- 同义词放入 `aliases`，不要创建多个重复词条。

## 索引页

`knowledge/indexes/` 由 LLM 维护：

- `companies.md`
- `industries.md`
- `products.md`
- `events.md`
- `policies.md`
- `open-questions.md`
- `health-check.md`

索引页不是最终真相，只是导航和压缩上下文。

