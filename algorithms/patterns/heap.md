# 堆 / 优先队列模板（易记版）

## 本质一句话
> **每次 O(log n) 拿到当前最值。Python 的 `heapq` 是最小堆。**

## 三句话用法

```python
import heapq

heap = []
heapq.heappush(heap, x)        # 入堆 O(log n)
top = heapq.heappop(heap)      # 弹最小 O(log n)
top = heap[0]                  # 偷看最小 O(1)，不弹出
```

**最大堆**：存 `-x` 即可（或用 `heapq._heappush_max`，但不推荐）。

## 经典套路

### 1. Top K：第 K 大用「大小为 K 的最小堆」

```python
def find_kth_largest(nums, k):
    heap = []
    for x in nums:
        heapq.heappush(heap, x)
        if len(heap) > k:
            heapq.heappop(heap)     # 顶（最小）被踢出
    return heap[0]                  # 堆顶 = 第 K 大
```

**为什么不直接取整个数组排序？** 这是 O(n log k)，比 O(n log n) 快，且支持流式数据。

### 2. 合并 K 个有序链表

```python
def merge_k_lists(lists):
    heap = []
    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))   # i 防止 val 相等时比较 node
    dummy = tail = ListNode()
    while heap:
        _, i, node = heapq.heappop(heap)
        tail.next = node
        tail = node
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))
    return dummy.next
```

**关键**：堆元素是元组时，第二个字段（这里是 `i`）用来打破第一个相等时的 tie，避免比较不可比对象。

### 3. 双堆求中位数

```python
class MedianFinder:
    def __init__(self):
        self.lo = []   # 最大堆（存负数），存较小的一半
        self.hi = []   # 最小堆，存较大的一半

    def add(self, x):
        heapq.heappush(self.lo, -x)
        heapq.heappush(self.hi, -heapq.heappop(self.lo))   # 倒一手保证 lo ≤ hi
        if len(self.hi) > len(self.lo):
            heapq.heappush(self.lo, -heapq.heappop(self.hi))

    def median(self):
        if len(self.lo) > len(self.hi):
            return -self.lo[0]
        return (-self.lo[0] + self.hi[0]) / 2
```

**口诀**：**先放 lo，再倒到 hi**，保证 `lo ≤ hi` 自动成立。

## 怎么不写错
- Python 默认**最小堆**。要最大堆 → 推 `-x`，取的时候再取负
- 堆里放元组时，**带上唯一 id**（比如下标）打破 tie
- **删除任意元素**：堆不支持 O(log n) 删除 → 用「**懒删除**」（弹出时检查是否已无效）
- 长度变化：取最值 + 删除用 `pop`，只看不删用 `[0]`

## 懒删除模板

```python
heap = []
deleted = Counter()

def push(x): heapq.heappush(heap, x)
def remove(x): deleted[x] += 1
def top():
    while heap and deleted[heap[0]] > 0:
        deleted[heap[0]] -= 1
        heapq.heappop(heap)
    return heap[0]
```

## 热身题
- [215. 数组中的第 K 个最大元素](https://leetcode.cn/problems/kth-largest-element-in-an-array/)
- [703. 数据流中的第 K 大元素](https://leetcode.cn/problems/kth-largest-element-in-a-stream/)
- [347. 前 K 个高频元素](https://leetcode.cn/problems/top-k-frequent-elements/)
- [1046. 最后一块石头的重量](https://leetcode.cn/problems/last-stone-weight/)

## 进阶题
- [23. 合并 K 个升序链表](https://leetcode.cn/problems/merge-k-sorted-lists/)
- [295. 数据流的中位数](https://leetcode.cn/problems/find-median-from-data-stream/)
- [378. 有序矩阵中第 K 小的元素](https://leetcode.cn/problems/kth-smallest-element-in-a-sorted-matrix/)
- [502. IPO](https://leetcode.cn/problems/ipo/)（双堆调度）
- [1825. 求出 MK 平均值](https://leetcode.cn/problems/finding-mk-average/)（懒删除 + 多堆）
- [857. 雇佣 K 名工人的最低成本](https://leetcode.cn/problems/minimum-cost-to-hire-k-workers/)
