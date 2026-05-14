# 链表操作模板（易记版）

## 三个救命法宝
1. **虚拟头节点 `dummy`**：消除"头节点要不要改"的边界
2. **画图**：3 个节点 + 4 根箭头，从来不靠想象
3. **改指针前先存好下一个**：`nxt = cur.next`

---

## 1. 反转链表（最经典）

```python
def reverse(head):
    prev, cur = None, head
    while cur:
        nxt = cur.next        # 1. 先存住下一个
        cur.next = prev       # 2. 反转
        prev = cur            # 3. prev 前进
        cur = nxt             # 4. cur 前进
    return prev               # 新头
```

**口诀**：**存 → 转 → 移**（移两根指针）。

### 反转前 N 个 / 反转一段

只要把上面的 while 改成走 N 步，然后把"反转后的尾"接到剩余部分即可。

---

## 2. 找中点（快慢指针）

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # 偶数节点时是右中点
```

想要**左中点**：把 `while` 改成 `while fast.next and fast.next.next`。

---

## 3. 判环 + 找入口（Floyd）

```python
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow, fast = slow.next, fast.next.next
        if slow == fast:                # 相遇
            p = head
            while p != slow:
                p, slow = p.next, slow.next
            return p
    return None
```

---

## 4. 合并两个有序链表

```python
def merge(l1, l2):
    dummy = tail = ListNode()
    while l1 and l2:
        if l1.val <= l2.val:
            tail.next = l1
            l1 = l1.next
        else:
            tail.next = l2
            l2 = l2.next
        tail = tail.next
    tail.next = l1 or l2        # 接剩余
    return dummy.next
```

---

## 5. 删除节点（dummy 模板）

```python
def remove_nth_from_end(head, n):
    dummy = ListNode(0, head)
    fast = slow = dummy
    for _ in range(n):
        fast = fast.next        # 拉开 n 步
    while fast.next:
        fast, slow = fast.next, slow.next
    slow.next = slow.next.next  # 跳过目标
    return dummy.next
```

**为什么要 dummy**：如果删的是头节点，没有 dummy 就要特判。

---

## 6. K 个一组反转（综合）

```python
def reverse_k_group(head, k):
    dummy = ListNode(0, head)
    pre_group_tail = dummy
    while True:
        # 1. 检查后续是否还有 k 个
        kth = pre_group_tail
        for _ in range(k):
            kth = kth.next
            if not kth: return dummy.next
        # 2. 反转 [pre_group_tail.next ... kth]
        group_start = pre_group_tail.next
        next_group_head = kth.next
        kth.next = None
        new_head = reverse(group_start)
        # 3. 拼接
        pre_group_tail.next = new_head
        group_start.next = next_group_head
        pre_group_tail = group_start
```

---

## 怎么不写错
- **dummy 是链表题的金科玉律**：只要可能改头节点 → dummy
- **画图，画图，画图**：3 个箭头都画清楚再改代码
- **空指针检查**：`while fast and fast.next` 这种条件顺序不能颠倒
- 改 `cur.next` 前永远先存 `cur.next`

## 热身题
- [206. 反转链表](https://leetcode.cn/problems/reverse-linked-list/)
- [21. 合并两个有序链表](https://leetcode.cn/problems/merge-two-sorted-lists/)
- [876. 链表的中间结点](https://leetcode.cn/problems/middle-of-the-linked-list/)
- [141. 环形链表](https://leetcode.cn/problems/linked-list-cycle/)
- [83. 删除排序链表中的重复元素](https://leetcode.cn/problems/remove-duplicates-from-sorted-list/)

## 进阶题
- [25. K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)
- [92. 反转链表 II](https://leetcode.cn/problems/reverse-linked-list-ii/)
- [142. 环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/)
- [143. 重排链表](https://leetcode.cn/problems/reorder-list/)（中点 + 反转 + 合并三连）
- [148. 排序链表](https://leetcode.cn/problems/sort-list/)（归并）
- [146. LRU 缓存](https://leetcode.cn/problems/lru-cache/)（双向链表 + 哈希）
