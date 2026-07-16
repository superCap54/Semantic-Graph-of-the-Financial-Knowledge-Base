# 金融知识库语义图谱

这是一个独立的 Obsidian vault、GitHub 仓库和 Codex/AI 维护的金融知识库。

目标是持续跟踪行业或股票：从 Horizon 等信息源收集资料，保存证据层 raw，再由 AI 编译成公司、行业、事件、政策、产品五类节点，并生成日报、周报和长期分析日志。

第一验收样板：`华大基因（300676.SZ）`。

## 核心目录

```text
raw/
  horizon-reports/   # Horizon 原始 Markdown 报告
  news/              # 从报告拆出的单条新闻卡片
  announcements/     # 公告、财报、交易所文件，尽量完整保存
  policies/          # 政策原文，尽量完整保存
  reports/           # 研报，默认摘要 + 关键摘录
公司/
行业/
事件/
政策/
产品/
日报/
周报/
索引/
config/
docs/
src/
```

## 当前设计

- 采集第一步先接 Horizon：Horizon 独立运行，本项目读取它生成的 Markdown 报告。
- raw 采用混合证据策略：官方资料尽量完整保存，商业新闻保存链接、摘要和关键摘录。
- 每条信息都由 AI 判断是否重要、是否可信、归类到哪些节点。
- 评分统一用 10 分制：重要性评分、可信度评分、影响强度评分。
- 重复新闻宽松合并，只生成一个主事件，其他报道作为来源补充。
- Obsidian 输出用中文；内部配置和程序字段用英文。

完整产品规格见 [docs/product-spec.md](docs/product-spec.md)。

## 本地命令

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -e .
sgkb init
sgkb watchlist-template
sgkb import-horizon path\to\horizon-report.md --query "华大基因"
sgkb ingest --title "示例新闻" --text "新闻摘要或关键摘录"
sgkb draft --kind company --name "华大基因" --ticker "300676.SZ"
sgkb search "华大基因"
```

后续开发节奏：

1. 分步骤调试：`collect -> normalize -> analyze -> compile -> daily`。
2. 稳定后串成：`sgkb run <关注对象>`。
3. 最后再接定时任务每日运行。
