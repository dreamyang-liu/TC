# OpenAI 算法 / 编码面试拆解（L5 视角）

> 数据来源：[hellointerview.com/guides/openai/l5](https://www.hellointerview.com/guides/openai/l5)、[hellointerview.com/blog/openai-coding-questions](https://www.hellointerview.com/blog/openai-coding-questions)、Medium 候选人复盘（2025-2026）。

---

## L5（Staff）面试结构

| 轮次 | 时长 | 考察重点 |
|------|------|---------|
| Recruiter / HM 电话 | 30 min | 领导力、对 mission 的认同 |
| Coding Screen | 60 min | 系统编码题，**代码量大、边界多** |
| System Design Screen | 60 min | 架构、trade-off 推理 |
| **Onsite Loop（4-6 轮）** | | |
| Coding | 60 min | 同上，更深 |
| System Design | 60 min | 失败处理、operational complexity |
| Technical Project Presentation | 45 min | 讲你自己做过的项目 |
| Behavioral × 2 | 30-45 min | 领导力、协作、影响力 |
| Domain（可选） | 60 min | ML infra / 分布式 / Safety |

⚠️ **整个流程 8-12 周**，慢的拖 4 个月。耐心准备，别等"快通知"。

---

## 编码面试核心特征

OpenAI 已经**明确远离经典 LeetCode tricky 题**，转向**生产级系统编码**：

| 维度 | 传统 LC 风格 | OpenAI 风格 |
|------|------------|------------|
| 题目 | 单个算法巧思 | 完整小系统实现 |
| 代码量 | 30-50 行 | **100-200+ 行** |
| 评分 | AC = 通过 | **结构 + 边界 + 可读** |
| Follow-up | 复杂度优化 | 持久化、并发、API、监控 |

**面试官明说的话**："We care more about how you reason about and debug your code that reflects actual engineering work."

---

## 8 大题型（必须每个都练到 60 min 内做完）

### 1. KV Store Serialize/Deserialize
- 实现序列化 / 反序列化，**key 和 value 都可能含任意字符**（包括分隔符）
- 核心 trick：**长度前缀编码**（length-prefix），类似 Redis RESP 协议
- Follow-up：流式 parse、二进制 vs 文本、版本演化
- 👉 [system-coding/kv-serializer.md](../system-coding/kv-serializer.md)

### 2. Time-Based Key-Value Store
- `set(key, value, timestamp)`、`get(key, timestamp)` 返回 ≤ timestamp 的最新 value
- 核心：每个 key 维护一个**按时间有序的列表**，用二分查找
- Follow-up：删除历史、压缩 GC、并发写
- 👉 [system-coding/time-kv-store.md](../system-coding/time-kv-store.md)

### 3. Resumable / Pausable Iterator
- 一个迭代器，支持 `next()` / `pause()` / `resume()` / `skip()` / `reset()`
- 嵌套结构（迭代器里包子迭代器）也要支持
- Follow-up：序列化迭代器状态（断点续传）
- 👉 [system-coding/resumable-iterator.md](../system-coding/resumable-iterator.md)

### 4. In-Memory Database with SQL
- 实现 `CREATE TABLE`, `INSERT`, `SELECT ... WHERE ...`, 简单 `JOIN`
- 核心：**parser + executor 分层**
- Follow-up：索引、事务、ACID
- 👉 [system-coding/sql-engine.md](../system-coding/sql-engine.md)

### 5. Unix `cd` 命令（带 symlink）
- 实现 `cd` 处理 `.`、`..`、绝对 / 相对路径、symlink 解析、**环检测**
- 核心：**栈 + visited set**
- Follow-up：符号链接深度限制、权限检查
- 👉 [system-coding/unix-cd.md](../system-coding/unix-cd.md)

### 6. Spreadsheet Formula Evaluation
- 单元格引用其他单元格（如 `A1 = B1 + C1`），求所有值
- 核心：**拓扑排序检测循环依赖**，DAG 上求值
- Follow-up：增量更新、循环修复
- 👉 [system-coding/spreadsheet.md](../system-coding/spreadsheet.md)

### 7. Multithreaded Web Crawler
- 起始 URL → 同域内 BFS → 多线程
- 核心：**ThreadPoolExecutor + 锁保护 visited**
- Follow-up：politeness、robots.txt、分布式、内容去重
- 👉 [system-coding/web-crawler.md](../system-coding/web-crawler.md)

### 8. Meeting Rooms / 区间调度
- 区间冲突检测、最小会议室数、活动安排
- 核心：**扫描线 / 最小堆**（不算严格 "system coding"，但 OpenAI 也会问 LC 风格的）
- 解法见 [patterns/heap.md](../patterns/heap.md) + 扫描线技巧
- Follow-up：跨时区、recurring meetings、capacity 上限

---

## 评分维度（按面试官内部 rubric 拆）

| 维度 | 通过最低线 | L5 标准 |
|------|----------|---------|
| **Correctness** | 主要 case 跑过 | 所有 edge case 自查并解决 |
| **Code Quality** | 能跑、变量名 OK | 模块化、复用、可测试 |
| **Communication** | 能讲清思路 | 主动 trade-off 分析 |
| **Debugging** | 找出 obvious bug | 系统化 self-critique |
| **Scope Management** | 完成基础需求 | 主动提出 follow-up |

---

## 准备策略（300+ LC 基础者）

### 第 1 阶段（5 天）：节奏感
- 把上面 8 道题，每天一道，**60 分钟内做完**
- 用真实的 Python（不要伪代码）
- 写完后**审视代码**：能否抽出小函数？变量名 OK 吗？

### 第 2 阶段（5 天）：边界 + Follow-up
- 同样 8 道题重做，每道留 **15 分钟专注 edge cases**
- 写 follow-up 实现（持久化、多线程版本）
- 大声"讲题"——录下来听一遍

### 第 3 阶段（剩余时间）：广度
- 跨 pattern 题型混练（避免"看到 KV 就用 length-prefix"反射）
- 每天加 30 min behavioral 准备

---

## 高频陷阱（面试中真的发生过）

1. **题目隐含约束没问** → "key/value 里能不能有 `\n`？" 不问就死
2. **没想 thread safety** → follow-up 一定问，事先没架构好就改不动
3. **代码全堆在 main 函数** → 不模块化就显得不像 senior
4. **跑测试时找不到 bug 还死撑** → 主动认 "let me add a print"
5. **结尾不收尾** → 没讲复杂度、没讲改进空间就到点

---

## 给 OpenAI 加分项

- 提到 **production patterns**（idempotency、retry、observability）
- 主动写 **type hints**（`def get(self, key: str, ts: int) -> Optional[str]`）
- 用 `dataclass` 做小 data type
- 加 **简短 docstring**（一行就够）
- 提到 **alternative approaches** 然后说为什么选这个

## 给 OpenAI 减分项

- 直接套 LC 模板，不解释为什么
- 没 trade-off 分析就开始写
- 复杂度算错（特别是字符串拼接的 O(n²)）
- API 设计反人类（返回 magic value 而不是 None / 抛异常）
- Follow-up 答 "我不知道" 而不是 "我会这样想 ……"

---

## 必读 reference 在 repo 里的位置

- [playbook/umpire.md](../playbook/umpire.md) — 解题流程
- [playbook/edge-cases.md](../playbook/edge-cases.md) — 边界 checklist
- [playbook/concurrency.md](../playbook/concurrency.md) — 多线程 follow-up
- [system-coding/](../system-coding/) — 8 道核心题完整实现
