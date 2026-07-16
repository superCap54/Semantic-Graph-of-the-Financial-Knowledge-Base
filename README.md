# Semantic Graph of the Financial Knowledge Base

本仓库用于构建一个本地优先的金融知识库语义图谱：从新闻、公告、研报、网页剪藏、API 聚合源中收集原始资料，再由 LLM/Codex 增量编译成 Obsidian 可浏览、可回链、可追问的 Markdown wiki。

## 可行性判断

可以做到，而且第一版不需要数据库。

核心原因是 Obsidian 的知识图谱并不要求真实图数据库。只要 Markdown 中稳定使用 `[[双链]]`、frontmatter、标签和索引页，Obsidian 就能渲染公司、行业、产品、事件、政策之间的关系图。数据库可以等到数据量、并发、检索性能或多用户协作真的需要时再加。

## MVP 流水线

1. 输入一个点：股票、公司、行业、产品、政策词、事件词。
2. 抓取资料：先接 RSS/API/网页剪藏，后续可参考 Horizon 的多源抓取、去重、评分、摘要机制。
3. 保存原文：所有未加工资料进入 `knowledge/raw/`。
4. LLM 编译：把原始资料拆成 `公司 / 行业 / 产品 / 事件 / 政策` 五类词条。
5. 写入 Obsidian wiki：输出到 `knowledge/wiki/`，用 `[[词条名]]` 形成语义链接。
6. 自增长：每次新资料进入后，更新相关词条、索引、待研究问题和关系候选。

## 当前仓库结构

```text
apps/
  api/                  # 预留：本地后端/API 服务
  web/                  # 预留：本地前端
config/
  sources.example.yaml  # 信息源配置样例
docs/
  architecture.md       # 架构说明
  obsidian-linking.md   # Obsidian 写作与链接规范
  roadmap.md            # 分阶段路线图
knowledge/
  raw/                  # 原始资料，不强求结构漂亮
  wiki/
    companies/
    industries/
    products/
    events/
    policies/
  indexes/              # LLM 维护的索引和摘要
  outputs/              # Q&A、图表、报告、slides 等派生输出
src/
  semantic_graph_kb/    # 本地 CLI 工具
```

## 本地使用

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
sgkb init
sgkb ingest --title "示例新闻" --source "manual" --text "某公司发布新产品，带动行业关注。"
sgkb draft --kind company --name "示例公司"
sgkb search "新产品"
```

## 设计原则

- 原始资料不可丢：`raw/` 是证据层。
- Wiki 可被重编译：`wiki/` 是 LLM 维护的解释层。
- 链接优先于文件夹：Obsidian 图谱来自内容里的 `[[链接]]`。
- 小规模先不用 RAG：先维护索引页和短摘要，让 Codex 直接读文件。
- 所有结论要能追溯：词条里保留 `来源`、`相关事件`、`待验证`。

