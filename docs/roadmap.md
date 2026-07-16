# Roadmap

## Phase 0: Local skeleton

- 初始化仓库结构。
- 约定 Obsidian 双链规范。
- 提供本地 CLI：init、ingest、draft、search。

## Phase 1: Manual ingest + Codex compile

- 手动粘贴新闻或网页剪藏进 `knowledge/raw/`。
- Codex 按五类词条增量编译 wiki。
- 维护索引页、待验证列表、断链列表。

## Phase 2: Source connectors

- RSS connector。
- 财经新闻 API connector。
- 公告/交易所/监管信息 connector。
- Horizon-style aggregator adapter。

## Phase 3: Local web app

- 输入股票/词条并触发抓取。
- 展示 raw 队列、编译状态、相关词条。
- 本地全文搜索。
- 一键打开 Obsidian 文件。

## Phase 4: LLM compile automation

- 自动实体抽取。
- 自动去重和合并。
- 自动更新相关 wiki 文件。
- 自动写 `open-questions.md` 和 `health-check.md`。

## Phase 5: Graph intelligence

- 图谱健康检查。
- 关系强度评分。
- 事件时间线。
- 行业传导链分析。
- 主题研究报告和 Marp slides 输出。

## Phase 6: Optional database/RAG

只有当文件系统路线不够用时再引入：

- SQLite：任务队列、抓取历史、全文索引。
- DuckDB：批量分析。
- Vector DB：语义检索。
- Graph DB：复杂路径查询。

