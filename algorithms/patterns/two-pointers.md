# 双指针模板（易记版）

双指针有两种完全不同的形态：**对撞指针** 和 **快慢指针**。

---

## 形态 1：对撞指针（数组有序 / 两端逼近）

### 本质一句话
> **两端向中间走，每一步根据当前和（或条件）决定移动哪一边。**

### 最简模板（两数之和 II）

```python
def two_sum(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        elif s < target:
            left += 1     # 偏小 → 左指针往右
        else:
            right -= 1    # 偏大 → 右指针往左
    return [-1, -1]
```

### 为什么不会错
- **`while left < right`** → 一定终止
- **必须排序**（或自然有序）
- 每步**至少有一根**指针动 → 不会死循环

---

## 形态 2：快慢指针（链表 / 找环 / 原地去重）

### 本质一句话
> **两指针速度不同，相对位移 = 它们之间的距离差。**

### 模板 A：找链表中点

```python
def middle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow   # 偶数节点时是「右中点」
```

### 模板 B：判环 + 找环入口（Floyd）

```python
def detect_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:           # 1. 相遇 → 有环
            p = head
            while p != slow:       # 2. 头和相遇点同速走
                p = p.next
                slow = slow.next
            return p               # 3. 环入口
    return None
```

**为什么相遇后从头同速走会到入口**：设头到入口距 a，入口到相遇点距 b，环长 L。相遇时 slow 走了 a+b，fast 走了 a+b+kL。fast = 2·slow → a+b = kL → a = kL−b = 从相遇点走 (kL−b) 步回到入口。

### 模板 C：原地去重 / 原地覆盖

```python
def remove_duplicates(nums):
    slow = 0
    for fast in range(len(nums)):
        if fast == 0 or nums[fast] != nums[fast - 1]:
            nums[slow] = nums[fast]
            slow += 1
    return slow
```

**口诀**：`slow` 指向**下一个要写入的位置**，`fast` 扫描所有元素。

---

## 热身题
- [167. 两数之和 II](https://leetcode.cn/problems/two-sum-ii-input-array-is-sorted/)
- [11. 盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/)
- [283. 移动零](https://leetcode.cn/problems/move-zeroes/)
- [876. 链表的中间结点](https://leetcode.cn/problems/middle-of-the-linked-list/)
- [141. 环形链表](https://leetcode.cn/problems/linked-list-cycle/)

## 进阶题
- [15. 三数之和](https://leetcode.cn/problems/3sum/)（排序 + 对撞）
- [42. 接雨水](https://leetcode.cn/problems/trapping-rain-water/)
- [142. 环形链表 II](https://leetcode.cn/problems/linked-list-cycle-ii/)
- [287. 寻找重复数](https://leetcode.cn/problems/find-the-duplicate-number/)（Floyd 巧用）
- [75. 颜色分类](https://leetcode.cn/problems/sort-colors/)（三指针 / 荷兰国旗）
