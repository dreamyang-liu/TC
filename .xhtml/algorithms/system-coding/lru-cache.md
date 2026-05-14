# LRU Cache — Anthropic Q2

> 经典中的经典。Anthropic 面试中作为 **bug-finding + 扩展持久化** 的题目出现。

## 问题（4 级递进）

- **L1**：实现 `LRUCache(capacity)` 支持 `get(key)`, `put(key, value)`，全部 O(1)
- **L2**：给定一段有 bug 的 LRU 代码，**找出并修复**（典型坑：`kwargs` hashing）
- **L3**：加上**持久化到磁盘** —— 进程重启数据不丢
- **L4**：分布式环境，多节点 LRU 一致性怎么搞？CPU-bound vs I/O-bound 怎么影响选型？

---

## 澄清问题

- `capacity` 一定 > 0 吗？
- key / value 类型？必须 hashable？
- get 不存在的 key：返回 `-1`、`None`、还是抛异常？
- 重复 put 同 key 算不算"使用"？（要 move-to-end 吗？）
- 单线程还是多线程？

---

## 数据结构选择

**O(1) get + O(1) put + O(1) evict-LRU** = **哈希表 + 双向链表**

Python 偷懒可以用 `collections.OrderedDict`（内部就是这套）。

---

## L1 实现（标准答案）

### 方法 A：OrderedDict（推荐写法）

```python
from collections import OrderedDict
from typing import Any

class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.cap = capacity
        self.d: OrderedDict = OrderedDict()

    def get(self, key: Any) -> Any:
        if key not in self.d:
            return -1
        self.d.move_to_end(key)        # 标记为最近用
        return self.d[key]

    def put(self, key: Any, value: Any) -> None:
        if key in self.d:
            self.d.move_to_end(key)
        self.d[key] = value
        if len(self.d) > self.cap:
            self.d.popitem(last=False) # 弹出 LRU
```

### 方法 B：手写双向链表（面试更显技术）

```python
class Node:
    __slots__ = ('key', 'val', 'prev', 'next')
    def __init__(self, k=None, v=None):
        self.key, self.val = k, v
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: dict = {}
        # 哨兵节点，简化边界
        self.head = Node()   # 最新
        self.tail = Node()   # 最旧
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_front(node)
        return node.val

    def put(self, key, value):
        if key in self.map:
            node = self.map[key]
            node.val = value
            self._remove(node)
            self._add_front(node)
        else:
            if len(self.map) >= self.cap:
                lru = self.tail.prev
                self._remove(lru)
                del self.map[lru.key]
            node = Node(key, value)
            self.map[key] = node
            self._add_front(node)
```

**面试时讲清楚**：
- 哨兵 head/tail 让 add/remove 不用判 None
- map 存 key → node，O(1) 找到节点然后 O(1) 移动

---

## L2：找 bug

Anthropic 给的代码通常长这样（人造 bug）：

```python
class BuggyCache:
    def __init__(self, capacity):
        self.cap = capacity
        self.d = {}
    
    def cached(self, func):
        def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)   # BUG!
            if key in self.d:
                return self.d[key]
            result = func(*args, **kwargs)
            self.d[key] = result
            return result
        return wrapper
```

### 常见 bug
1. **`str(kwargs)` 字典顺序不稳定**（虽然 3.7+ 保证插入顺序，但 `{'a':1,'b':2}` 和 `{'b':2,'a':1}` 字符串不同 → cache miss）
2. **没有淘汰**（不是 LRU，是普通 memoize）
3. **可变参数 hashable？** list 不能直接 hash

### 修复
```python
def make_key(args, kwargs):
    # kwargs 排序保证确定性
    return (args, tuple(sorted(kwargs.items())))
```

更稳：先 freeze 不可变化：
```python
def freeze(x):
    if isinstance(x, dict):
        return tuple(sorted((k, freeze(v)) for k, v in x.items()))
    if isinstance(x, list):
        return tuple(freeze(i) for i in x)
    return x
```

---

## L3：持久化

### 策略 1：Write-Through to Disk
每次 put 立刻写文件 —— 慢但安全。

```python
import json, os

class DurableLRU(LRUCache):
    def __init__(self, capacity, path):
        super().__init__(capacity)
        self.path = path
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                for line in f:
                    k, v = json.loads(line)
                    self.put(k, v)

    def put(self, key, value):
        super().put(key, value)
        with open(self.path, 'a') as f:
            f.write(json.dumps([key, value]) + '\n')
```

⚠️ append-only log 会无限增长 → 定期 compact。

### 策略 2：Write-Back（异步）
内存优先，**后台线程 flush 到磁盘**。性能好但 crash 可能丢数据。

```python
import threading, queue
class WriteBackLRU(LRUCache):
    def __init__(self, capacity, path):
        super().__init__(capacity)
        self.q = queue.Queue()
        self.path = path
        threading.Thread(target=self._writer, daemon=True).start()

    def _writer(self):
        while True:
            k, v = self.q.get()
            with open(self.path, 'a') as f:
                f.write(f"{k},{v}\n")

    def put(self, key, value):
        super().put(key, value)
        self.q.put((key, value))
```

### 真生产环境：用 WAL（Write-Ahead Log）+ 定期 snapshot

---

## L4：分布式 / 大局观讨论

| 问题 | 答 |
|------|---|
| 多节点 LRU 一致性？ | 通常**不强一致** —— 每个节点本地 LRU + 一致性哈希分片 |
| Read-through / Write-through？ | 看用例。读多用 read-through，写少 |
| Cache stampede？ | mutex + soft expiry 或 probabilistic early expiration |
| 大对象 vs 小对象？ | 小对象进 memory cache；大对象写本地 SSD |

---

## 边界 / 陷阱
- `capacity=0` → 抛异常或永远 evict
- 单线程 `OrderedDict` 是安全的；多线程要加 `RLock`
- get 不存在的 key 别报错
- value 是 None 时怎么和 "not found" 区分？→ 用 sentinel 或抛 `KeyError`

## 复杂度
- get / put：**O(1) 平均**
- 空间：O(capacity)

## 相关题
- [LFU Cache](lfu-cache.md) — 自然延伸
- [146. LRU Cache](https://leetcode.cn/problems/lru-cache/)
- [460. LFU Cache](https://leetcode.cn/problems/lfu-cache/)
