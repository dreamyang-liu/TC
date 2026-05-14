# 单调栈模板（易记版）

## 本质一句话
> **栈里存「还在等下一个更大/更小元素」的下标。新元素来了就清理栈里被它"打败"的人。**

## 最简模板（下一个更大元素 → 单调递减栈）

```python
def next_greater(nums):
    n = len(nums)
    ans = [-1] * n
    stack = []  # 存下标，对应值单调递减
    for i, x in enumerate(nums):
        while stack and nums[stack[-1]] < x:
            ans[stack.pop()] = x   # x 是 stack[-1] 的下一个更大
        stack.append(i)
    return ans
```

## 四种变体只改两个地方

| 想找 | 栈内单调性 | while 条件 | 遍历方向 |
|------|-----------|-----------|---------|
| 下一个更**大** | 递减 | `nums[stack[-1]] < x` | 从左到右 |
| 下一个更**小** | 递增 | `nums[stack[-1]] > x` | 从左到右 |
| 上一个更**大** | 递减 | `nums[stack[-1]] < x` | 从右到左 |
| 上一个更**小** | 递增 | `nums[stack[-1]] > x` | 从右到左 |

**口诀**：
- 找**更大** → 栈**递减**；找**更小** → 栈**递增**（栈和目标相反）
- 找**下一个** → 从左到右；找**上一个** → 从右到左

## 怎么不写错
- **栈里存下标**，比存值灵活（值可以由下标反查）
- **严格 `<` vs 非严格 `<=`** 决定相等元素归谁 → 看题目要求
- **结尾要不要清栈**：如果栈里剩的代表"没找到"，就保持初值 `-1`
- 经典套路：**贡献法** —— 出栈时算 `(i − stack[-1] − 1)` 之类的区间贡献

## 进阶套路：贡献法（柱状图最大矩形）

```python
def largest_rectangle(heights):
    heights.append(0)         # 哨兵：强制清空栈
    stack = []
    ans = 0
    for i, h in enumerate(heights):
        while stack and heights[stack[-1]] > h:
            top = stack.pop()
            left = stack[-1] if stack else -1
            ans = max(ans, heights[top] * (i - left - 1))
        stack.append(i)
    return ans
```

**思想**：每根柱子作为高度时，向左/右能扩到的边界，恰好是单调栈里的前后位置。

## 热身题
- [496. 下一个更大元素 I](https://leetcode.cn/problems/next-greater-element-i/)
- [739. 每日温度](https://leetcode.cn/problems/daily-temperatures/)
- [503. 下一个更大元素 II](https://leetcode.cn/problems/next-greater-element-ii/)（循环数组：跑两遍）

## 进阶题
- [84. 柱状图中最大的矩形](https://leetcode.cn/problems/largest-rectangle-in-histogram/)
- [85. 最大矩形](https://leetcode.cn/problems/maximal-rectangle/)
- [42. 接雨水](https://leetcode.cn/problems/trapping-rain-water/)
- [907. 子数组的最小值之和](https://leetcode.cn/problems/sum-of-subarray-minimums/)（贡献法经典）
- [316. 去除重复字母](https://leetcode.cn/problems/remove-duplicate-letters/)
