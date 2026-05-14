# 二分查找模板（易记版）

```python
def binary_search(nums, target):
    lo, hi = 0, len(nums)  # [lo, hi) — 左闭右开

    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] < target:      # ← 只改这个条件
            lo = mid + 1
        else:
            hi = mid

    return lo  # 第一个让条件不成立的位置
```

## 唯一要改的地方：`if` 条件

| 目标 | 条件 | 返回值 |
|------|------|--------|
| **左边界**（第一个 `x >= target`） | `nums[mid] < target` | 第一个 `nums[i] >= target` 的下标 |
| **右边界**（第一个 `x > target`）  | `nums[mid] <= target` | 第一个 `nums[i] > target` 的下标 |

**口诀：** `<` 找左，`<=` 找右。（加个 `=` → 往右推一格）

## 怎么用返回值

```python
left  = binary_search(nums, target)        # 用 <
right = binary_search(nums, target) - 1    # 用 <=，再减 1

# 是否存在？
found = left < len(nums) and nums[left] == target

# target 出现次数
count = right_bound - left_bound           # 右用 <=，左用 <
```

## 为什么这个模板不会错

- **左闭右开 `[lo, hi)`** → `hi = len(nums)`，没有 off-by-one。
- **`lo < hi`** 循环 → 干净终止，结束时 `lo == hi`。
- **`hi = mid`**（不是 `mid - 1`）→ 符合左闭右开，不会漏元素。
- **`lo = mid + 1`** → 一定有进展，不会死循环。
- 空数组也能用（返回 `0`）。

## 小例子

```
nums = [1, 2, 2, 2, 3], target = 2
left  （用 <）  → 1   # 第一个 >= 2 的位置
right （用 <=） → 4   # 第一个 > 2 的位置
count = 4 - 1 = 3 ✓
```

记住一个模板，`<` ↔ `<=` 一切换，左右边界都搞定。
