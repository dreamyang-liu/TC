# Time-Based Key-Value Store — OpenAI 经典

> LC 981 的"L5 版"。基础题 + 多个 follow-up。

---

## 问题

```python
class TimeMap:
    def set(self, key: str, value: str, timestamp: int) -> None: ...
    def get(self, key: str, timestamp: int) -> str:
        """返回 timestamp 时刻或之前最近的 set 的 value；不存在返回 ''。"""
```

约束：`set` 时 timestamp **严格递增**。

---

## 澄清问题

1. 同 key 同 timestamp 多次 set 怎么办？（题目假设不会，确认）
2. timestamp 不严格递增呢？（基础题不需要 handle，follow-up 才有）
3. `get` 时刻不存在任何 ≤ 的 set → 返回 ""？None？
4. 单线程？预期 QPS？
5. 范围查询？时间窗口的所有 value？

---

## L1：基础实现（二分）

```python
from collections import defaultdict
from bisect import bisect_right

class TimeMap:
    def __init__(self):
        self.store = defaultdict(list)   # key -> List[(ts, value)]

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.store[key].append((timestamp, value))

    def get(self, key: str, timestamp: int) -> str:
        if key not in self.store:
            return ''
        ts_list = self.store[key]
        # bisect 找第一个 > timestamp 的位置 - 1 = 最后一个 ≤ timestamp
        idx = bisect_right(ts_list, (timestamp, chr(127)*10)) - 1
        return ts_list[idx][1] if idx >= 0 else ''
```

**复杂度**：set O(1)，get **O(log n)** 二分。

### 为什么 `bisect_right` + `chr(127)*10`？
要按**只看 timestamp** 二分，但元组比较会先比 ts 再比 value。
用 `chr(127)*10` 做哨兵，保证 `(ts, sentinel)` 排在所有真实 `(ts, value)` 后面。

更干净的写法：自己写二分。

```python
def get(self, key, timestamp):
    if key not in self.store: return ''
    arr = self.store[key]
    lo, hi = 0, len(arr)
    while lo < hi:
        mid = (lo + hi) // 2
        if arr[mid][0] <= timestamp:
            lo = mid + 1
        else:
            hi = mid
    # lo = 第一个 > timestamp 的位置
    return arr[lo - 1][1] if lo > 0 else ''
```

---

## L2：timestamp 乱序 set

如果 set 的 timestamp **不保证递增**，每次 set 都要插入到有序位置。

```python
from bisect import insort

def set(self, key, value, timestamp):
    arr = self.store[key]
    # 找插入位置
    idx = bisect_right(arr, (timestamp, chr(127)*10))
    # 如果已经有 (timestamp, _)，决定是更新还是报错（澄清）
    if idx > 0 and arr[idx-1][0] == timestamp:
        arr[idx-1] = (timestamp, value)   # 覆盖
    else:
        arr.insert(idx, (timestamp, value))
```

set 变成 O(log n + n) 因为 insert 要移动后面元素。
真严肃的话改用 `SortedList` from `sortedcontainers`，set 也是 O(log n)。

---

## L3：范围查询（区间内所有 value）

```python
def get_range(self, key, t_start, t_end):
    """返回 [t_start, t_end] 范围内所有 (ts, value)。"""
    arr = self.store.get(key, [])
    lo = bisect_left(arr, (t_start, ''))
    hi = bisect_right(arr, (t_end, chr(127)*10))
    return arr[lo:hi]
```

---

## L4：持久化 + 压缩

### 持久化
每次 set 写 WAL（append-only log）：
```
key1,1,val1
key1,5,val5
key2,3,val3
```

启动时 replay。

### Compaction
旧版本的 value 可以被淘汰（如果只 query 最近 N 天）：

```python
def gc(self, retention: int):
    """删除每个 key 中 ts < now - retention 的记录。"""
    now = time.time()
    cutoff = now - retention
    for key in list(self.store):
        arr = self.store[key]
        # 保留所有 ts >= cutoff 的，加上 ts < cutoff 中最大的一个
        keep_from = bisect_left(arr, (cutoff, ''))
        if keep_from > 0:
            keep_from -= 1     # 保留紧邻 cutoff 之前的，作为"最旧 active"
        self.store[key] = arr[keep_from:]
```

### Snapshot + WAL
- 定期 dump 全量 snapshot
- 每次 set 写 WAL
- 重启 = load snapshot + replay WAL

---

## L4 扩展讨论

| Q | A |
|---|---|
| 并发 set + get？ | 每 key 一把 RLock；或读写分离 |
| 内存放不下？ | 冷 key 落盘（LSM-tree 思路） |
| 分布式？ | 一致性哈希分片，每分片独立 TimeMap |
| 删除操作？ | "tombstone" 写入；后续 query 看到 tombstone 返回空 |
| range scan？ | 二分 + 切片 |

---

## 完整测试

```python
def test():
    tm = TimeMap()
    tm.set("foo", "bar", 1)
    assert tm.get("foo", 1) == "bar"
    assert tm.get("foo", 3) == "bar"     # 还是 bar
    tm.set("foo", "bar2", 4)
    assert tm.get("foo", 4) == "bar2"
    assert tm.get("foo", 5) == "bar2"
    assert tm.get("foo", 3) == "bar"     # 旧值还在
    assert tm.get("foo", 0) == ""        # 早于任何 set
    assert tm.get("nonexistent", 100) == ""
    print("All passed")

test()
```

---

## 边界与陷阱

1. **空 key 没 set 过** → 返回 ''（不要 KeyError）
2. **timestamp 比所有 set 都早** → 返回 ''
3. **完全等于某个 set 的 timestamp** → 返回那个 value
4. **同 key 不同 ts 大量并发** → 锁粒度按 key 还是全局？
5. **删除语义** → 用 tombstone（特殊 value）还是真删？

## 复杂度

| 操作 | L1 | L2（乱序 set） | L3+L4 |
|------|-----|---------------|-------|
| set | O(1) | O(log n + n) 或 O(log n) | + WAL O(1) |
| get | O(log n) | O(log n) | 同上 |
| gc | — | — | O(n) per key |

## 相关
- [981. Time Based Key-Value Store](https://leetcode.cn/problems/time-based-key-value-store/)
- LSM-tree（生产 timeseries DB 的基础）
- HBase / Cassandra 的 wide column 模型
