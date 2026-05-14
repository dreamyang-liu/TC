# 快速选择模板（易记版）

## 本质一句话
> **快排只递归 K 所在的那一半**。期望 O(n)，最坏 O(n²)（随机化后几乎不会触发）。

## 最简模板（找第 K 小，0-indexed）

```python
import random

def quickselect(nums, k):
    def partition(lo, hi):
        # 随机化避免最坏情况
        p = random.randint(lo, hi)
        nums[p], nums[hi] = nums[hi], nums[p]
        pivot = nums[hi]
        i = lo
        for j in range(lo, hi):
            if nums[j] < pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1
        nums[i], nums[hi] = nums[hi], nums[i]
        return i             # pivot 最终位置

    lo, hi = 0, len(nums) - 1
    while True:
        p = partition(lo, hi)
        if p == k:    return nums[p]
        elif p < k:   lo = p + 1
        else:         hi = p - 1
```

调用：
```python
# 第 K 小（k 从 1 开始）→ quickselect(nums, k-1)
# 第 K 大           → quickselect(nums, len(nums) - k)
```

## 三路划分版（应对大量重复元素）

```python
def quickselect3(nums, k):
    def helper(lo, hi):
        if lo == hi: return nums[lo]
        pivot = nums[random.randint(lo, hi)]
        lt, gt, i = lo, hi, lo
        while i <= gt:
            if   nums[i] < pivot: nums[lt], nums[i] = nums[i], nums[lt]; lt += 1; i += 1
            elif nums[i] > pivot: nums[gt], nums[i] = nums[i], nums[gt]; gt -= 1
            else: i += 1
        if k < lt:   return helper(lo, lt - 1)
        elif k > gt: return helper(gt + 1, hi)
        else:        return pivot
    return helper(0, len(nums) - 1)
```

**为什么三路更好**：当数组很多相等元素时，普通 partition 会退化；三路把等于 pivot 的元素聚成一块，避免无效划分。

## 怎么不写错
- **一定要随机化 pivot**，否则有序数组会退化到 O(n²)
- **第 K 大 / 第 K 小**搞清楚：转换成 0-indexed 比较
- 返回的是**值**还是**下标**：题目读清楚
- 用 `heapq.nlargest(k, nums)` 也能做，但快选 O(n) 比堆 O(n log k) 渐进更优

## 快速选择 vs 堆

| | 快选 | 堆 |
|---|---|---|
| 复杂度 | 期望 O(n) | O(n log k) |
| 原地修改 | 是 | 否 |
| 支持流式数据 | 否（要一次性看全部） | 是 |
| 实现难度 | 中 | 低 |

## 热身题
- [215. 数组中的第 K 个最大元素](https://leetcode.cn/problems/kth-largest-element-in-an-array/)
- [347. 前 K 个高频元素](https://leetcode.cn/problems/top-k-frequent-elements/)

## 进阶题
- [973. 最接近原点的 K 个点](https://leetcode.cn/problems/k-closest-points-to-origin/)
- [324. 摆动排序 II](https://leetcode.cn/problems/wiggle-sort-ii/)（快选找中位数 + 三路划分）
- [462. 最小操作次数使数组元素相等 II](https://leetcode.cn/problems/minimum-moves-to-equal-array-elements-ii/)
