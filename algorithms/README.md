# Algorithms — OpenAI / Anthropic 算法面试备战

> **目标**：L5 软件工程师在 **30 天**内通过 OpenAI / Anthropic 算法面试。
>
> **核心理念**：这两家公司**不考竞赛算法**，考"**能不能在 60 分钟内从零写出干净、模块化、handle edge case 的小系统**"。

---

## 🎯 从这里开始

1. **[📅 30 天冲刺计划](30-day-plan.md)** — 每天做什么，按表照办即可
2. **[🎓 OpenAI L5 面试拆解](company-guides/openai.md)** — 8 大题型 + L5 评分 rubric
3. **[🎓 Anthropic 面试拆解](company-guides/anthropic.md)** — 6 道固定题 + 4 级递进打法

---

## 📁 目录结构

```
algorithms/
├── 30-day-plan.md             ⭐ 主路线图，每天看一眼
├── company-guides/            🎓 OpenAI / Anthropic 拆解 + 真题清单
├── playbook/                  📋 面试沟通、边界、并发、复杂度速查
├── system-coding/             💻 13 道核心系统编码题（带完整实现）
├── patterns/                  📐 22 个算法 pattern 模板（已熟练就跳过）
├── problems/                  📝 单题深度笔记
├── viz/                       🎬 交互式可视化
└── .xhtml/graph.json          🌐 知识图谱
```

---

## 🎓 Company Guides — 知己知彼

| 文件 | 内容 |
|------|------|
| [openai.md](company-guides/openai.md) | L5 面试结构、8 大题型、评分维度、加 / 减分项 |
| [anthropic.md](company-guides/anthropic.md) | 6 道固定题、4 级递进、CodeSignal 平台 tips |

---

## 📋 Playbook — 面试当天的肌肉记忆

| 文件 | 一句话 |
|------|------|
| [umpire.md](playbook/umpire.md) | 60 分钟流程：U→M→P→I→R→E |
| [clarifying.md](playbook/clarifying.md) | 各题型澄清问题清单 |
| [edge-cases.md](playbook/edge-cases.md) | 7 大边界 + 按数据结构分的 checklist |
| [complexity.md](playbook/complexity.md) | Python 数据结构操作复杂度速查 |
| [concurrency.md](playbook/concurrency.md) | Thread/Process/asyncio 速通 + 锁与原语 |

---

## 💻 System Coding — 13 道核心题（重中之重）

> 每题都有：**问题 → 澄清问题 → 设计 → 完整实现 → L1-L4 follow-up → 边界 → 复杂度**。

### Anthropic 6 道（题库已公开）
| 题 | 重点 |
|----|------|
| [Web Crawler](system-coding/web-crawler.md) | BFS + 多线程 + politeness |
| [LRU Cache](system-coding/lru-cache.md) | OrderedDict / 双向链表 + bug-finding + 持久化 |
| [Stack Trace](system-coding/stack-trace.md) | 递归深度区分 + innermost first |
| [Distributed Mode](system-coding/distributed-mode.md) | 网络成本意识 + Misra-Gries |
| [Tokenizer](system-coding/tokenizer.md) | Trie + UNK fallback + code review |
| [LFU Cache](system-coding/lfu-cache.md) | 频率桶 + min_freq 维护 |

### OpenAI 高频
| 题 | 重点 |
|----|------|
| [KV Serializer](system-coding/kv-serializer.md) | Length-prefix encoding（Redis RESP 风格） |
| [Time-based KV Store](system-coding/time-kv-store.md) | 每 key 有序列表 + 二分 |
| [Resumable Iterator](system-coding/resumable-iterator.md) | 栈模拟 + reset + snapshot |
| [SQL Engine](system-coding/sql-engine.md) | Parser / Executor / Storage 三层 |
| [Unix `cd`](system-coding/unix-cd.md) | 路径解析 + symlink + 环检测 |
| [Spreadsheet](system-coding/spreadsheet.md) | DAG + 循环检测 + 增量更新 |
| [Rate Limiter](system-coding/rate-limiter.md) | Token bucket / sliding window |

---

## 📐 Patterns — 22 个算法模板

> 假设你已经熟，主要作为**速查**。生疏的快速复习。

### S 级（基础必会）

| Pattern | 一句话本质 | 文件 |
|---|---|---|
| 哈希表 | 用空间换时间 | [hash-table.md](patterns/hash-table.md) |
| 双指针 | 对撞 / 快慢两种形态 | [two-pointers.md](patterns/two-pointers.md) |
| 滑动窗口 | 右扩左缩 | [sliding-window.md](patterns/sliding-window.md) |
| 二分查找 | 半开区间 + `<` ↔ `<=` | [binary-search.md](patterns/binary-search.md) |
| 二叉树递归 | 当前做什么 + 子树返回什么 | [tree-traversal.md](patterns/tree-traversal.md) |
| BFS | 按层扩张，边权 1 时即最短路 | [bfs.md](patterns/bfs.md) |
| 链表操作 | dummy + 画图 + 改前先存 | [linked-list.md](patterns/linked-list.md) |
| 动态规划基础 | 状态 → 转移 → 边界 → 顺序 | [dp.md](patterns/dp.md) |

### A 级（进阶高频）

| Pattern | 一句话本质 | 文件 |
|---|---|---|
| 回溯 | 选 → 递归 → 撤销 | [backtracking.md](patterns/backtracking.md) |
| 堆 / 优先队列 | O(log n) 取最值 | [heap.md](patterns/heap.md) |
| 单调栈 | 找下一个更大 / 更小 | [monotonic-stack.md](patterns/monotonic-stack.md) |
| 单调队列 | 滑窗 + 单调栈 | [monotonic-queue.md](patterns/monotonic-queue.md) |
| 并查集 | 路径压缩 + 按秩合并 | [union-find.md](patterns/union-find.md) |
| 拓扑排序 | 入度 0 出队 → 删出边 | [topological-sort.md](patterns/topological-sort.md) |
| 二维 / 区间 DP | 长度从小到大 | [interval-dp.md](patterns/interval-dp.md) |
| 快速选择 | 快排只递归 K 所在的一半 | [quickselect.md](patterns/quickselect.md) |
| 前缀和 / 差分 | 变化量层面合并 | [difference-array.md](patterns/difference-array.md) |
| Trie | 共享前缀的字符串共享路径 | [trie.md](patterns/trie.md) |
| Dijkstra | 堆 + BFS，非负权 | [patterns/dijkstra.md](patterns/dijkstra.md) |
| 贪心 | Exchange argument 证明 | [greedy.md](patterns/greedy.md) |
| 树形 DP | 后序聚合 + 两种返回值 | [tree-dp.md](patterns/tree-dp.md) |
| 位运算 | XOR 性质 + 状压 DP | [bit-manipulation.md](patterns/bit-manipulation.md) |

---

## 📝 Problems

| # | 题目 | 难度 | Pattern | 文件 | Viz |
|---|---|---|---|---|---|
| 1674 | Minimum Moves to Make Array Complementary | Medium | 差分数组 | [📝](problems/1674-min-moves-complementary.md) | [🎬](viz/1674.html) |

---

## 🧠 写笔记的原则

- **Pattern 文件**：写「为什么这个套路有效 / 什么时候用」，不是「步骤几步」
- **System-coding 文件**：写「设计 + 完整实现 + L1-L4 follow-up + 边界」
- **Problem 文件**：写「为什么属于这个 pattern + 关键陷阱 + 代码骨架」

每道新题做完都问：
- 这题暴露的 pattern 是哪个？已有文档吗？
- 我最初的思路（包括错的）是什么？为什么错？
- 一句话能描述这个 pattern 的本质吗？

---

## ⚠️ 重要原则

### Do
- ✅ 把 [playbook/](playbook/) 当成"作战手册"，面试前每次复读
- ✅ 每道题都按 [UMPIRE 流程](playbook/umpire.md) 走，培养肌肉记忆
- ✅ **大声讲题**，录音回放找改进点
- ✅ 60 分钟做不完 → 立刻看答案，**不要硬撑**

### Don't
- ❌ 重新刷 LC top 150（你已经会）
- ❌ 学竞赛算法（KMP / 线段树 / Manacher / FFT 等 —— **OpenAI/Anthropic 不考**）
- ❌ Day 30 前夜还在做新题
- ❌ 沉默地写代码（沉默就是挂面）

---

## 资源来源

- [hellointerview.com OpenAI L5 guide](https://www.hellointerview.com/guides/openai/l5)
- [hellointerview.com OpenAI coding questions](https://www.hellointerview.com/blog/openai-coding-questions)
- [linkjob.ai Anthropic question bank](https://www.linkjob.ai/interview-questions/anthropic-coding-interview/)
- [interviewing.io Anthropic](https://interviewing.io/anthropic-interview-questions)
- 多位 2025-2026 候选人 Medium / Glassdoor 复盘
