# Distributed Mode / Median — Anthropic Q4

> Anthropic 题库里最"系统"的一题。考察**网络成本意识 + 算法**。

---

## 问题

- **10 个节点**，每个有 `send(node_id, msg)` / `recv() -> (sender_id, msg)` / `barrier()` 原语
- **本地读速度**：10 bytes/s
- **网络速度**：1 byte/s（**慢 10×**）
- 数据均匀分散在 10 个节点上
- 任务：求**全局 mode**（众数）。Follow-up：求 **median**

---

## 关键约束理解

**网络是瓶颈** —— 任何"全部传给 node 0"的方案都最差。
目标：**最小化跨节点传输的字节数**。

---

## L1：Naive 全聚合

```python
# 每个节点本地计数，全部发给 node 0 聚合
def naive_mode(node_id, local_data):
    local_count = Counter(local_data)
    if node_id == 0:
        global_count = Counter()
        for _ in range(9):
            sender, msg = recv()
            global_count.update(msg)
        global_count.update(local_count)
        return global_count.most_common(1)[0][0]
    else:
        send(0, local_count)
        return None
```

**成本**：每个 worker 发整个 `local_count` 到 node 0。
如果 unique key 多 → 巨大网络成本。

**面试中可以承认这个是 baseline，但要立刻提出更优方案。**

---

## L2：基于全局值域的 Reduce

如果**值的范围已知且小**（如 1-100 的评分）：

```python
# 每个节点：算 local count
# all-reduce：每个节点都得到全局 count
# 都选 argmax，结果一致
```

**all-reduce 网络复杂度**：O(V·N)，V 是值域大小，N 是节点数。
比 naive 的 O(U·N²) 强（U 是 unique key 数，通常 U >> V）。

---

## L3：Heavy Hitter 思想（值域大时）

如果**值是任意字符串、值域巨大**，全聚合 / all-reduce 都不行。

### 思路：先 sketch，再精确确认

**阶段 1**：每个节点用 **Misra-Gries**（top-k 频繁元素近似）算法找出本地 top-k 候选。

```python
def misra_gries(data, k):
    """估计出现频率 ≥ n/k 的元素。"""
    counters = {}
    for x in data:
        if x in counters:
            counters[x] += 1
        elif len(counters) < k - 1:
            counters[x] = 1
        else:
            for key in list(counters):
                counters[key] -= 1
                if counters[key] == 0:
                    del counters[key]
    return counters
```

**阶段 2**：把每个节点的 top-k 候选汇总（小数据），求并集 → 这些是**全局 mode 的候选集**。

**阶段 3**：对候选集做一次精确 count（每个节点扫一遍本地数据，对候选 key 计数）→ all-reduce → 取 argmax。

**网络成本**：O(k·N²)，k 是 sketch size，远小于 unique key 数。

---

## L4：Median（更难）

### 思路 A：基于值域的二分

```python
def distributed_median(node_id, local_data):
    """假设值在 [0, V] 整数范围。"""
    lo, hi = 0, V
    total = global_count()      # 知道总数 N
    target = total // 2
    while lo < hi:
        mid = (lo + hi) // 2
        # 每个节点算 local 中 ≤ mid 的数量
        local_le = sum(1 for x in local_data if x <= mid)
        # all-reduce 求 global_le
        global_le = all_reduce_sum(local_le)
        if global_le < target + 1:
            lo = mid + 1
        else:
            hi = mid
    return lo
```

**网络成本**：每次 all-reduce 1 个 int，共 O(log V) 轮。完美。

### 思路 B：基于分桶的 quantile sketch

如果值是 float 或无界 → 用 **t-digest** / **GK summary** 等流式 quantile 算法。
每个节点本地 sketch，merge 得到全局近似 median。

---

## 完整伪代码（参考）

```python
class DistributedNode:
    def __init__(self, node_id, local_data, total_nodes):
        self.id = node_id
        self.data = local_data
        self.N = total_nodes

    # 这些是题目提供的 primitive
    def send(self, target_id, msg): ...
    def recv(self) -> tuple: ...
    def barrier(self): ...

    def all_reduce_sum(self, value):
        """ring all-reduce: O(N) rounds, O(N) bytes total."""
        s = value
        for step in range(self.N - 1):
            target = (self.id + 1) % self.N
            self.send(target, s)
            sender, received = self.recv()
            s += received
        return s

    def find_mode(self):
        # Phase 1: 本地 sketch
        local_top = self.misra_gries(self.data, k=20)
        # Phase 2: 广播候选集
        candidates = self.all_gather(set(local_top.keys()))
        # Phase 3: 精确计数
        local_counts = {c: 0 for c in candidates}
        for x in self.data:
            if x in local_counts:
                local_counts[x] += 1
        global_counts = self.all_reduce_dict(local_counts)
        return max(global_counts.items(), key=lambda x: x[1])[0]

    def find_median(self, V):
        lo, hi = 0, V
        while lo < hi:
            mid = (lo + hi) // 2
            local_le = sum(1 for x in self.data if x <= mid)
            global_le = self.all_reduce_sum(local_le)
            target = (self.total_count() + 1) // 2
            if global_le < target:
                lo = mid + 1
            else:
                hi = mid
        return lo
```

---

## L4 扩展讨论

| Q | A |
|---|---|
| 节点 fail 怎么办？ | 需要多副本 / heartbeat / 重新平衡 |
| 数据非常倾斜怎么办？ | 可能需要重新分片再算 |
| 怎么测试？ | 模拟器 + 不同数据分布 + 故意丢包 |
| 如果数据流式来呢？ | 用 reservoir / sliding window / t-digest |

---

## 关键洞察总结

1. **网络是瓶颈** → 设计目标是最小化传输
2. **能本地预处理就本地预处理**
3. **能传摘要就别传原始**（Misra-Gries, top-k）
4. **能值域二分就值域二分**（O(log V) > O(N²)）
5. **all-reduce 比 send-to-coord 好**：避免单点瓶颈

---

## 边界

- 数据 0 个 / 1 个 / 全相同
- 节点数 1（退化成本地算）
- mode 不唯一（题目要哪一个？）
- median 偶数个数（中间两个的平均？）

## 相关
- Misra-Gries / Boyer-Moore 多数投票
- t-digest paper (Dunning 2013)
- MapReduce 风格的分布式 aggregation
