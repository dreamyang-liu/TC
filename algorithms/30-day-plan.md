# 30 天 OpenAI / Anthropic 算法面试冲刺计划

> **前提**：300+ LC 基础，模板熟练，目标公司 OpenAI / Anthropic。
>
> **核心理念**：这两家公司**不考竞赛算法**，考"**能不能写出干净、模块化、handle edge case 的小系统**"。计划侧重 [system-coding/](system-coding/) 和真题模拟，而不是再刷 100 道 LC。

---

## 总体时间分配

| 阶段 | 天数 | 目标 |
|------|------|------|
| Phase 1：地基 + 工具 | Day 1-3 | 把 playbook 内化成肌肉记忆 |
| Phase 2：System-Coding 深耕 | Day 4-15 | 13 道题各做 1-2 遍，60 分钟内完成 |
| Phase 3：真题模拟 | Day 16-22 | Anthropic 6 + OpenAI 8 全真模拟 |
| Phase 4：薄弱点 + Mock | Day 23-27 | 找朋友 mock，针对性补 |
| Phase 5：终冲 + 行为题 | Day 28-30 | 节奏稳住，behavioral 准备 |

**每天投入**：3-4 小时。**晚上必复盘**，记错题。

---

## Phase 1：地基（Day 1-3）

### Day 1 — 工具 + 心态
**早上（90 min）**
- [ ] 通读 [playbook/umpire.md](playbook/umpire.md)
- [ ] 通读 [playbook/clarifying.md](playbook/clarifying.md)
- [ ] **录音练习**：选一道熟悉的 LC（如 [206. 反转链表](https://leetcode.cn/problems/reverse-linked-list/)），按 UMPIRE 流程录音 15 min。听回放，注意：哪里 "嗯…啊…"、哪里没讲复杂度

**下午（90 min）**
- [ ] 通读 [playbook/edge-cases.md](playbook/edge-cases.md) + [complexity.md](playbook/complexity.md)
- [ ] [company-guides/openai.md](company-guides/openai.md) + [anthropic.md](company-guides/anthropic.md)
- [ ] 决定：你今天起 **每道题都按 UMPIRE 走一遍**

**晚上（30 min）**
- [ ] 在笔记本里写一份"面试澄清问题 cheatsheet"，A4 纸一张 —— 自己写比看强 10 倍

### Day 2 — 并发基础
**早上（90 min）**
- [ ] [playbook/concurrency.md](playbook/concurrency.md)
- [ ] 跑通 `ThreadPoolExecutor` + `Lock` 的 3 个 demo（用 Jupyter notebook 实验）

**下午（90 min）**
- [ ] 看 [system-coding/web-crawler.md](system-coding/web-crawler.md) 的 L1 + L3
- [ ] 自己 from scratch 写一个**单线程** crawler（不看答案）
- [ ] 跑通后**改成多线程**

**晚上（30 min）**
- [ ] 思考：如果让你解释 GIL，3 分钟讲清楚 —— 写下要点

### Day 3 — LRU/LFU 双拼
**早上（90 min）**
- [ ] [system-coding/lru-cache.md](system-coding/lru-cache.md)
- [ ] 不看答案，**手写 OrderedDict 版** + **手写双向链表版**，各 30 分钟

**下午（90 min）**
- [ ] [system-coding/lfu-cache.md](system-coding/lfu-cache.md)
- [ ] 实现 LFU。**这道题 60 分钟内做完很难**，第一次允许 90 分钟

**晚上**
- [ ] 把 LRU 改成**线程安全版**，跑 4 个 worker 并发测试

---

## Phase 2：System-Coding 深耕（Day 4-15）

**节奏**：每天 1 道（60 分钟限时） + 复盘（30 分钟）+ 一道相关 LC 热身（30 分钟）。

| Day | 主题 | 题目 | 配套 LC 热身 |
|----|------|------|------|
| 4 | KV 序列化 | [kv-serializer](system-coding/kv-serializer.md) | [271. 字符串的编解码](https://leetcode.cn/problems/encode-and-decode-strings/) |
| 5 | 时序 KV | [time-kv-store](system-coding/time-kv-store.md) | [981. 时序 KV](https://leetcode.cn/problems/time-based-key-value-store/) |
| 6 | 嵌套迭代器 | [resumable-iterator](system-coding/resumable-iterator.md) | [341. 扁平化嵌套迭代器](https://leetcode.cn/problems/flatten-nested-list-iterator/) |
| 7 | Stack Trace | [stack-trace](system-coding/stack-trace.md) | — (无对应) |
| 8 | Tokenizer | [tokenizer](system-coding/tokenizer.md) | [208. Trie](https://leetcode.cn/problems/implement-trie-prefix-tree/) |
| 9 | Spreadsheet | [spreadsheet](system-coding/spreadsheet.md) | [207. 课程表](https://leetcode.cn/problems/course-schedule/) |
| 10 | Unix cd | [unix-cd](system-coding/unix-cd.md) | [71. 简化路径](https://leetcode.cn/problems/simplify-path/) |
| 11 | SQL 引擎 (基础) | [sql-engine](system-coding/sql-engine.md) (L1+L2) | [770. 字符串解析器](https://leetcode.cn/problems/basic-calculator-iv/) |
| 12 | SQL 引擎 (扩展) | sql-engine L3+L4 | — |
| 13 | Rate Limiter | [rate-limiter](system-coding/rate-limiter.md) | [LCP 17. 速算机器人](https://leetcode.cn/problems/nGK0Fy/) |
| 14 | Web Crawler (复习+多线程) | [web-crawler](system-coding/web-crawler.md) L3+L4 | [1242. 多线程网页爬虫](https://leetcode.cn/problems/web-crawler-multithreaded/) |
| 15 | 分布式 Mode | [distributed-mode](system-coding/distributed-mode.md) | — |

**每道题流程**：
1. **不看答案** 60 分钟做 L1+L2
2. **超时立刻看答案**对照（不要硬撑超过 60 分钟，时间宝贵）
3. **补完整 L3+L4 讨论** (笔记)
4. **3 个测试用例**（基础、边界、压力）
5. **30 分钟复盘**：哪卡住？为什么？

---

## Phase 3：真题全真模拟（Day 16-22）

### Day 16-18：Anthropic 6 道题极限挑战

| Day | 题 | 时长 | 平台 |
|----|----|------|------|
| 16 上午 | Web Crawler L1-L4 | 90 min | 模拟 CodeSignal（用 IDE 关掉补全） |
| 16 下午 | LRU L1-L4 | 90 min | 同上 |
| 17 上午 | Stack Trace L1-L4 | 90 min | 同上 |
| 17 下午 | Tokenizer L1-L3 | 90 min | 同上 |
| 18 上午 | Distributed Mode | 90 min | 白板 + 伪代码（不需要跑） |
| 18 下午 | **复盘 + 弱点笔记** | 全天 | — |

### Day 19-21：OpenAI 8 道题档位测试

每天 2 道，60 分钟限时（OpenAI 节奏）：

| Day | 上午 | 下午 |
|----|------|------|
| 19 | KV Serializer | Time KV Store |
| 20 | Resumable Iterator | Spreadsheet |
| 21 | Unix cd | SQL Engine (L1+L2) |
| 22 | Rate Limiter | LFU Cache |

### Day 22：休息 + 自我评估
- [ ] 列出哪 3 道题做得最差
- [ ] 在 Day 23-27 补它们

---

## Phase 4：弱点专攻 + Mock（Day 23-27）

### Day 23-25：薄弱点重做
- 拿出 Day 22 找到的 3 道题，**每天一道，重新 60 分钟做**
- 比第一次快 30% 以上才算 ready

### Day 26：朋友 Mock #1
- 找一个朋友（最好做过面试官）
- 让对方从 [openai.md](company-guides/openai.md) 或 [anthropic.md](company-guides/anthropic.md) **随机选一道**
- 完整模拟 60-90 min
- 对方做的事：澄清问题、中途打断、问 follow-up

### Day 27：朋友 Mock #2
- 换一道题再来
- 这次模拟"找 bug"题（如 LRU L2）

---

## Phase 5：终冲 + Behavioral（Day 28-30）

### Day 28：Behavioral 准备
（虽然你说算法为主，但 L5 onsite 一定有 behavioral）

写出 **5 个 STAR 故事**（Situation, Task, Action, Result）：
1. 你做过最 **技术深** 的项目
2. 一次 **和同事冲突** 怎么解决
3. **失败 / 学到东西** 的项目
4. **跨团队协作** 的经历
5. 你 **做的最有 impact** 的事

每个故事写 200-300 字，反复练 5 遍。

### Day 29：节奏 + 速度
- 找你最自信的 3 道 system-coding 题
- **每道限时 45 分钟**（比真实快 25%）
- 这是给你正式面试当天的"信心剂"

### Day 30：休息 + 心态
- **不要再做新题**
- 把 [playbook/](playbook/) 整个再看一遍
- 写出"明天面试 cheat sheet"：
  - 5 个澄清问题
  - 我的 5 个 STAR 故事 1-line summary
  - 我的项目 30-second pitch
- **早睡**

---

## 每日自检表

```
□ 今天按 UMPIRE 流程做题了吗？
□ 我开始写代码前问澄清问题了吗？
□ 我自己想出至少 3 个 edge case 了吗？
□ 我大声讲了思路（哪怕没人听）吗？
□ 我讲了复杂度吗？
□ 60 分钟内做完了吗？没的话，是哪一步卡住？
```

**贴在显示器上**。

---

## 每周回顾问题

```
1. 我这周哪道题做得最差？为什么？
2. 我哪个 pattern 还在反复犯错？
3. 我哪些"澄清问题"忘记问？
4. 我在 follow-up 阶段答了哪些不完整？
5. 距离真实面试，我最大的差距是 ___（补完）
```

---

## 替代节奏（如果你只剩 14 天）

跳过 Phase 1 直接进 Phase 2：
- Day 1-7：13 道 system-coding（每天 1.5-2 道）
- Day 8-11：Anthropic 6 + OpenAI 8 模拟
- Day 12-13：弱点 + Mock
- Day 14：休息

---

## 替代节奏（如果只剩 7 天 / 紧急）

只做 Anthropic 6 + OpenAI top 4：
- Day 1：Web Crawler + LRU
- Day 2：Stack Trace + Tokenizer
- Day 3：Distributed Mode + KV Serializer
- Day 4：Time KV + Spreadsheet
- Day 5：Resumable Iterator + SQL Engine
- Day 6：Mock interview
- Day 7：休息

---

## 资源清单

### 必看
- [playbook/](playbook/) — 全部
- [company-guides/](company-guides/) — 全部
- [system-coding/](system-coding/) — 13 道

### 选看
- [patterns/](patterns/) — 应该已经熟，遇到忘了的随手翻
- [glassdoor.com/Interview/Anthropic](https://www.glassdoor.com/Interview/Anthropic-Software-Engineer-Interview-Questions-EI_IE8109027.0,9_KO10,27.htm) — 最新候选人复盘
- [interviewing.io/anthropic](https://interviewing.io/anthropic-interview-questions) — Mock interview 资源

### 不要做的事
- ❌ 重新刷一遍 LC top 150（你已经会）
- ❌ 学竞赛算法（线段树、KMP、Manacher 等 —— OpenAI / Anthropic 不考）
- ❌ 看 5 个 YouTube 频道（信息过载）
- ❌ Day 30 前夜还在做新题（影响心态）

---

## 最后一句话

> **这两家公司测的是"工程师的真实工作能力"，不是"算法竞赛能力"。
> 你已经 300+ LC，模板没问题。真正的差距是：能不能 60 分钟从零写一个 200 行的可读、能跑、handle 边界的小系统。**

30 天专注练这个，你就拿到了 offer 的 80%。剩下 20% 是运气和 culture fit。

Good luck. 👋
