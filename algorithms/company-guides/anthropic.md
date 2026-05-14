# Anthropic 算法 / 编码面试拆解

> 数据来源：[linkjob.ai Anthropic 题库](https://www.linkjob.ai/interview-questions/anthropic-coding-interview/)、[interviewing.io/anthropic](https://interviewing.io/anthropic-interview-questions)、2025-2026 候选人复盘。

---

## 面试流程

| 阶段 | 时长 | 内容 |
|------|------|------|
| HM Screen | 60 min | 动机 + 经历 |
| Online Assessment | 90 min | **单题 4 级递进**（CodeSignal） |
| Onsite Loop | 5 轮 | Coding × 1-2、System Design × 1、Behavioral × 2 |

⏱️ **平均 20 天**走完流程（OpenAI 慢得多）。

---

## 关键反差点（和 OpenAI 比）

| 维度 | Anthropic | OpenAI |
|------|-----------|--------|
| 题库 | **只有 6 道**，公开半公开 | 题库大，每个面试官不同 |
| 风格 | First principles，干净模块化 | 生产化、handle 真实场景 |
| 反作弊 | LLM detect 是否在"针对测试用例 hack" | 主要靠面试官眼力 |
| 平台 | CodeSignal（必须能跑） | CoderPad |
| OA 长度 | 90 min 单题 4 级 | 60 min 多题 |

⚠️ **"不会因为背模板而得分"** —— Anthropic 招聘邮件原话。题不是算法 trick，是"能不能写出可读、可扩展、handle edge case 的代码"。

---

## 6 道固定题（必须 100% 掌握）

### Q1. Web Crawler
- **L1**：单线程 BFS，同域内抓 URL
- **L2**：处理 URL fragment（`#` 后内容）、去重
- **L3**：改成多线程（`ThreadPoolExecutor`）
- **L4**：politeness（同一 host 限频）、分布式扩展讨论
- 👉 [system-coding/web-crawler.md](../system-coding/web-crawler.md)

### Q2. LRU Cache
- **L1**：实现基础 LRU（双向链表 + 哈希）
- **L2**：**找 bug**！代码里 `kwargs` hashing 有问题
- **L3**：持久化到磁盘
- **L4**：CPU-bound vs I/O-bound 在分布式环境的讨论
- 👉 [system-coding/lru-cache.md](../system-coding/lru-cache.md)

### Q3. Stack Trace → Event Conversion
- **L1**：profiler 采样数据（时间戳 + 调用栈） → 转成 start/end events
- **L2**：相同的连续栈不产生新事件
- **L3**：**递归调用要按深度区分**（`{"a", "b", "a"}` 两个 a 是不同 frame）
- **L4**：多个函数同一时间结束 → **逆序输出**（innermost first）
- 👉 [system-coding/stack-trace.md](../system-coding/stack-trace.md)

### Q4. Distributed Mode / Median
- **场景**：10 个节点，每个有 `send/recv/barrier` 原语
- **约束**：本地读 10 bytes/s，网络 1 byte/s
- **L1**：求 mode（众数），naive 是每个节点本地计数 → 汇总到 Node 0
- **L2**：能否更快？(网络贵 → 减少传输量)
- **L3**：求 median 怎么改？（hint：分桶 / 二分）
- **L4**：节点 fail 怎么办？
- 👉 [system-coding/distributed-mode.md](../system-coding/distributed-mode.md)

### Q5. Profiler Trace（Q3 变体）
- 跟 Q3 类似，但措辞更像 LC 题
- 重点：**理解问题** > 实现速度

### Q6. Tokenizer
- **L1**：实现 greedy tokenization：给一个 vocab dict，把字符串切成 token 序列
- **L2**：**code review**：找现有实现的 bug
  - vocab 不覆盖所有字符时挂掉
  - 输入中字面 `UNK` 字符串和 unknown token 冲突
  - 短 token 匹配效率低
- **L3**：fallback：未知字符标记 `<UNK>`
- 👉 [system-coding/tokenizer.md](../system-coding/tokenizer.md)

---

## 4 级递进通用结构

```
L1 (15-20 min): 让代码跑起来，处理 happy path
L2 (15-20 min): 处理 1-2 个 obvious edge case
L3 (20-25 min): 重大功能扩展（持久化 / 并发 / 增加 API）
L4 (15-20 min): 讨论 system level trade-off（可能不写代码）
```

**面试节奏**：**早做完 L1 早赚**。L1 卡 30 min 几乎肯定挂。

---

## 评分维度

| 维度 | 权重 | 怎么得分 |
|------|------|---------|
| Problem decomposition | ⭐⭐⭐ | 把 L1-L4 拆出清晰的接口 |
| Correctness | ⭐⭐⭐ | 跑过 hidden tests |
| Edge case handling | ⭐⭐⭐ | 自己想出来，不等面试官提 |
| Performance | ⭐⭐ | 不要 O(n²) 当 O(n) 写 |
| Code clarity / modularity | ⭐⭐⭐ | 函数 < 30 行；类职责单一 |

---

## 准备策略

### 第 1 周：6 道题各做一次
- 不限时，目标是**完整通关 L1-L4**
- 自己跑测试，包括恶意 edge case

### 第 2 周：6 道题计时重做
- 90 min 内通关 L1-L3
- 录屏看自己卡在哪

### 第 3 周：变体题混练
- 不告诉自己是哪道，30 秒识别 + 立刻动手
- 找朋友 mock interview

---

## 高频陷阱

1. **第一题没问 fragment 处理** → Web Crawler 死
2. **LRU bug 没读懂题** → 题给的代码故意有 bug，要先 review 再扩展
3. **Stack Trace 没区分递归深度** → `{"a","b","a"}` 给错答案
4. **Tokenizer 假设 vocab 全覆盖** → 出现 unknown 直接崩
5. **分布式 mode 没考虑网络成本** → 把所有数据传到 Node 0 才是错的方向

---

## 给 Anthropic 加分项

- **First-principles 推理**：先不查参考，自己推导出"为什么这样设计"
- **模块化**：分类 / 接口 / 抽象基类
- **测试**：写 `assert` 或简单 unit test
- **错误处理**：用自定义异常类，不要 `raise Exception`
- **类型注解 + docstring**

## 给 Anthropic 减分项

- 一上来就写代码，没问澄清问题
- 函数名 / 变量名缩写过度
- 没 handle "vocab 不覆盖" 这种**显然的 edge case**
- LLM detect 触发：代码模式像在专门 hack test case 而非真解题

---

## CodeSignal 平台 Tips

- 必须能跑通才算"完成"
- **要点 Run 按钮**多次，每加一段就跑
- Tab 补全是关的（？），写起来慢，**减少不必要的 `import`**
- 提交后还能改，看到挂的 case 可以加判断（但留下来的 commit 历史会被看）

---

## 必读 reference

- [playbook/umpire.md](../playbook/umpire.md) — 解题流程
- [playbook/clarifying.md](../playbook/clarifying.md) — 澄清问题
- [system-coding/](../system-coding/) — 6 道题完整实现 + L1-L4 拆解
