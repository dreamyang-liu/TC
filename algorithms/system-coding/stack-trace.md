# Stack Trace → Events Conversion — Anthropic Q3

> Anthropic 题库里**最容易写错**的题。坑点全在"递归调用要按深度区分"。

---

## 问题

Profiler 采样数据：每个时间点抓一个 **call stack**（函数名列表，最外层在前）。

输入：
```
samples = [
    Sample(t=1.0, stack=["main"]),
    Sample(t=2.5, stack=["main", "func1"]),
    Sample(t=3.0, stack=["main", "func1", "helper"]),
    Sample(t=4.0, stack=["main", "func1"]),
    Sample(t=5.0, stack=["main"]),
]
```

输出：每个 frame 的 **(name, start_time, end_time)** 事件列表，**innermost first** 当多个同时结束。

---

## 4 级递进

- **L1**：相邻样本完全相同的 stack → 不产生新事件
- **L2**：handle 普通进出栈（按 stack 长度变化）
- **L3**：**递归调用**（`["a", "b", "a"]`，两个 a 不是同一 frame）
- **L4**：多个 frame 同时结束 → **逆序输出**（depth 大的先 end）

---

## 关键洞察

不能简单按"函数名"匹配 push/pop —— 要按 **(name, depth)** 才唯一。

把每个 frame 想成 **`(depth, name)` 二元组**：
- 同样的 `(depth, name)` = 同一个 frame
- 不同 depth 同名 = 不同 frame（递归调用）

---

## L1 + L2 实现

```python
from dataclasses import dataclass
from typing import List

@dataclass
class Sample:
    t: float
    stack: List[str]    # outermost first

@dataclass
class Event:
    name: str
    start: float
    end: float

def to_events_basic(samples: List[Sample]) -> List[Event]:
    """假设没有递归（每层名字唯一）"""
    events: List[Event] = []
    active = []          # 当前 active 的 (name, start_time)
    
    for s in samples:
        new_stack = s.stack
        # 找到公共前缀
        common = 0
        while common < len(active) and common < len(new_stack) \
              and active[common][0] == new_stack[common]:
            common += 1
        # active 中超出 common 的部分都结束了 —— 从内向外
        for i in range(len(active) - 1, common - 1, -1):
            name, start = active[i]
            events.append(Event(name, start, s.t))
        active = active[:common]
        # new_stack 中超出 common 的部分都新开始了
        for name in new_stack[common:]:
            active.append((name, s.t))
    
    # 最后一个样本时刻收尾 —— 没有更多数据，假设全部在最后一个 t 结束
    final_t = samples[-1].t
    for i in range(len(active) - 1, -1, -1):
        name, start = active[i]
        events.append(Event(name, start, final_t))
    
    return events
```

---

## L3：处理递归（depth 区分）

上面的代码**对递归会出错**：
```python
# stack 1: ["a", "b"]
# stack 2: ["a", "b", "a"]    ← 第二个 "a" 是 b 内调用的新 a
# stack 3: ["a"]              ← 全 unwind 到第一个 a
```

bug：用 "name 匹配" 会以为第二个 stack 是第一个的子集。

**修复**：比较时**只看位置 + 名字**就够（位置即 depth）：

上面的代码其实**已经按位置比较了**，所以 OK。但要确认理解：

```python
def to_events(samples):
    events = []
    active = []           # 每层一个 (name, start_t)
    for s in samples:
        new = s.stack
        # 1. 找公共前缀（按位置 + 名字）
        common = 0
        while (common < len(active) and common < len(new)
               and active[common][0] == new[common]):
            common += 1
        # 2. close 掉超出 common 的 frame，innermost first
        for i in range(len(active) - 1, common - 1, -1):
            name, start = active[i]
            events.append(Event(name, start, s.t))
        active = active[:common]
        # 3. open 新增的 frame
        for name in new[common:]:
            active.append((name, s.t))
    # 收尾
    final_t = samples[-1].t
    for i in range(len(active) - 1, -1, -1):
        name, start = active[i]
        events.append(Event(name, start, final_t))
    return events
```

**测试递归**：
```python
samples = [
    Sample(1, ["main"]),
    Sample(2, ["main", "fact"]),
    Sample(3, ["main", "fact", "fact"]),    # 递归
    Sample(4, ["main", "fact", "fact", "fact"]),
    Sample(5, ["main", "fact", "fact"]),
    Sample(6, ["main"]),
]
events = to_events(samples)
# 应该有 4 个 fact 事件（其中 3 个内层），按 depth 从深到浅依次 end
```

---

## L4：多个同时 end → innermost first

上面 `range(len(active)-1, common-1, -1)` 已经是**从内向外**了 —— 满足要求。

明确写一个测试：
```python
samples = [
    Sample(1, ["a", "b", "c"]),
    Sample(2, []),    # 全部结束
]
# 期望输出：c 先 end，然后 b，然后 a（按 start 时间相同 t=1，end 时间相同 t=2）
```

如果输出格式要求 sort，再加一道：
```python
events.sort(key=lambda e: (e.end, -e.start))
```

---

## Follow-up 题型

### A. 去除短帧（噪声过滤）
```python
def denoise(events, min_duration):
    return [e for e in events if e.end - e.start >= min_duration]
```

### B. 找出连续被采样 ≥ N 次的函数
```python
def hot_functions(samples, n):
    cnt = {}
    prev = None
    streak = 0
    for s in samples:
        # 假设只看栈顶
        top = s.stack[-1] if s.stack else None
        if top == prev:
            streak += 1
        else:
            prev, streak = top, 1
        if streak >= n:
            cnt[top] = cnt.get(top, 0) + 1
    return cnt
```

### C. 检测相同 stack 连续出现 > k 次
（用上面同样的 streak 思想）

---

## 完整测试

```python
samples = [
    Sample(1.0, ["main"]),
    Sample(2.0, ["main", "f1"]),
    Sample(3.0, ["main", "f1", "f2"]),
    Sample(4.0, ["main", "f1"]),
    Sample(5.0, ["main", "f1", "f2"]),    # f2 再次进入
    Sample(6.0, ["main"]),
]

events = to_events(samples)
for e in events:
    print(e)

# 期望（innermost first 当同时 end）:
# Event(f2, 3.0, 4.0)
# Event(f2, 5.0, 6.0)
# Event(f1, 2.0, 6.0)
# Event(main, 1.0, 6.0)
```

---

## 边界与陷阱

1. **同一个 t 出现多个 sample** → 题目说不会，问清楚
2. **空 stack** → handle，所有 active 都结束
3. **递归时只看 name 比较**（漏 depth）→ **错！** 上面已经按 position 比较
4. **innermost first 没做** → 出错
5. **last sample 之后没收尾** → 漏掉最长的 root frame

## 复杂度
- 时间：O(总 frame 数)
- 空间：O(max 栈深)

## 相关题
- 没有完全对应的 LC 题，最接近的是 [331. 验证二叉树前序序列化](https://leetcode.cn/problems/verify-preorder-serialization-of-a-binary-tree/)（思路相反但 stack 操作类似）
