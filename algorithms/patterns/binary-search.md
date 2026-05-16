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

---

## 闭区间统一模板

当题目搜索空间是闭区间 `[left, right]` 时（如旋转数组、求平方根等），用这个模板：

```python
left, right = 0, len(nums) - 1
while left < right:
    mid = (left + right) // 2
    if condition(mid):
        right = mid      # mid 可能是答案，保留
    else:
        left = mid + 1   # mid 不可能是答案，排除
return left
```

### 核心原则

**这个模板找的是：满足 `condition` 的最左位置。**

每道题只需想清楚一件事：**什么 condition 能让我排除一半？**

### 为什么不会出错

1. **不会死循环**：向下取整时 `mid < right`，所以 `right = mid` 一定缩小范围；`left = mid + 1` 也一定缩小。
2. **不会跳过答案**：`right = mid` 保留了 mid，答案永远在 `[left, right]` 内。
3. **结束有确定结果**：`left == right` 时退出，搜索范围只剩一个元素。

### 所有情况的统一套法

| 你想找 | condition(mid) | 返回 |
|--------|---------------|------|
| 最左的满足 X | X | `left` |
| 最右的满足 X | NOT X（反转条件） | `left - 1` |

**"找最右" = "找最左的不满足条件的位置" - 1。**

### 常见题目示例

| 题目 | condition(mid) | 含义 |
|------|---------------|------|
| 旋转数组最小值 | `nums[mid] <= nums[right]` | mid 在最小值右侧或就是最小值 |
| 第一个 >= target | `nums[mid] >= target` | mid 在答案位置右侧或就是 |
| 第一个 > target | `nums[mid] > target` | mid 在答案位置右侧或就是 |
| 最右的 <= target | `nums[mid] > target`（反转） | 返回 `left - 1` |
| 求 sqrt(x) | `mid * mid >= x` | mid >= 真实答案 |

### 取整方向的唯一规则

**`mid` 的取整方向必须远离你保留的那一端。**

- 保留右边（`right = mid`）→ 向下取整 `(left + right) // 2` ← 就是本模板
- 保留左边（`left = mid`）→ 向上取整 `(left + right + 1) // 2`

但你不需要记第二种——所有"找最右"的题都可以反转条件后用模板一，永远向下取整。

### 做题决策流程

1. **我在找什么？** → 确定搜索空间的左右边界
2. **什么条件能让我排除一半？** → 写出 `condition(mid)`
3. **我找的是最左还是最右？** → 最左直接用，最右反转条件后 `left - 1`
4. **结束后是否需要检查合法性？** → 答案可能不存在时，验证 `nums[left]`
