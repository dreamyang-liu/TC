# LFU Cache

> LRU 的进阶版。考察"**两个键的索引同时维护**"的能力。

---

## 问题

实现 `LFUCache(capacity)` 支持：
- `get(key)` — 返回 value，并把 freq +1。不存在返回 -1
- `put(key, value)` — 满了**先驱逐最低频**，**频率并列时驱逐最久未用**

全部 **O(1)**。

---

## 关键洞察

需要：
1. **O(1) 通过 key 找 node**
2. **O(1) 找到最低 freq 的"最久未用"那一个**
3. **O(1) 把 node 从一个频率桶移到另一个**

**结构**：
- `key → node` 哈希表
- `freq → 双向链表`（同 freq 内按访问时间排序，链表头是最新）
- `min_freq` 变量随手维护

每次 `get` / `put` 命中：
- `freq → freq+1`（从 `freq` 桶移除，加到 `freq+1` 桶头部）
- 如果原 `freq` 桶空了且 `freq == min_freq`，`min_freq += 1`

每次 `put` 新 key：
- freq = 1，min_freq 重置为 1
- 满了 → 从 `freq[min_freq]` 桶**尾部**淘汰

---

## 完整实现

```python
from collections import defaultdict

class Node:
    __slots__ = ('key', 'val', 'freq', 'prev', 'next')
    def __init__(self, k=0, v=0, f=1):
        self.key, self.val, self.freq = k, v, f
        self.prev = self.next = None

class DLL:
    """双向链表 + 哨兵。头插，尾出。"""
    def __init__(self):
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def pop_back(self):
        if self.size == 0: return None
        node = self.tail.prev
        self.remove(node)
        return node


class LFUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map: dict = {}                          # key → Node
        self.freq_lists: dict = defaultdict(DLL)     # freq → DLL
        self.min_freq = 0

    def _touch(self, node):
        """命中后频率 +1，重新挂到新桶头部。"""
        old_freq = node.freq
        self.freq_lists[old_freq].remove(node)
        if self.freq_lists[old_freq].size == 0:
            del self.freq_lists[old_freq]
            if self.min_freq == old_freq:
                self.min_freq += 1
        node.freq += 1
        self.freq_lists[node.freq].add_front(node)

    def get(self, key: int) -> int:
        if key not in self.map or self.cap == 0:
            return -1
        node = self.map[key]
        self._touch(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if self.cap == 0: return
        if key in self.map:
            node = self.map[key]
            node.val = value
            self._touch(node)
            return
        # 新插入
        if len(self.map) >= self.cap:
            # 淘汰最低频里最久未用
            evict = self.freq_lists[self.min_freq].pop_back()
            del self.map[evict.key]
            if self.freq_lists[self.min_freq].size == 0:
                del self.freq_lists[self.min_freq]
        node = Node(key, value, 1)
        self.map[key] = node
        self.freq_lists[1].add_front(node)
        self.min_freq = 1
```

---

## 调试自检

```python
c = LFUCache(2)
c.put(1, 1)
c.put(2, 2)
assert c.get(1) == 1     # freq[1]=2, freq[2]=1
c.put(3, 3)              # evict key=2
assert c.get(2) == -1
assert c.get(3) == 3     # freq[1]=2, freq[3]=2
c.put(4, 4)              # tie: min_freq=2 候选 {1,3}，淘汰最久未用 → 1
assert c.get(1) == -1
assert c.get(3) == 3
assert c.get(4) == 4
print("LFU passed")
```

---

## 怎么不写错

- **min_freq 不要漏维护**：每次桶清空 + 是 min_freq 时 +1；put 新 key 时重置为 1
- **同 freq 内**：链表头部是最新，尾部是最旧 → 淘汰从尾
- **`get` 必须更新 freq**（题目隐含规则）
- 容量 0 单独 handle

---

## 复杂度
- get / put：**O(1)**
- 空间：O(capacity)

---

## 面试 follow-up

- "如果要 LRU-2"（最近 2 次访问的时间）？→ Window 内的 LRU
- "如果要 TTL"？→ 配合 expiring heap 或惰性删除
- "怎么持久化？" → 写 freq 变更日志
- "怎么测试 LRU 和 LFU 哪个更好？" → 用真实 trace 模拟 hit rate

## 相关题
- [460. LFU Cache](https://leetcode.cn/problems/lfu-cache/)
- [LRU Cache](lru-cache.md)
