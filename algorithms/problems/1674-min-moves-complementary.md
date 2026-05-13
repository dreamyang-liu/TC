# 1674. Minimum Moves to Make Array Complementary

- **难度**：Medium
- **Pattern**：[差分数组](../patterns/difference-array.md)
- **链接**：https://leetcode.com/problems/minimum-moves-to-make-array-complementary/

## 题目

给数组 `nums`（偶数长度 n）和上界 `limit`。每次操作可把任一元素改成 `[1, limit]` 内的任意整数。求最少操作数，使 `nums[i] + nums[n-1-i]` 对所有 i 相等。

## 抽象

枚举目标和 T ∈ `[2, 2·limit]`：
- 对每对 `(a, b)`（设 `a ≤ b`），写出代价 `gᵢ(T)`：

```
gᵢ(T) = 0    T = a + b           （已经满足）
        1    T ∈ [a+1, b+limit]   （只改 1 个：[1+b, limit+b] ∪ [1+a, limit+a]）
        2    其他                  （得改 2 个）
```

- 求 `min_T Σ gᵢ(T)`。

## 关键陷阱：为什么不能二分 T

`f(T) = Σ gᵢ(T)` **不是单调，也不是单峰**。每对的 V 形谷底在不同 T，叠加后会出现多个局部极小。

反例 `nums = [1,1,10,10], limit = 10`：
- 对 (1,1) 谷底 T=2，1-区间 [2, 11]
- 对 (10,10) 谷底 T=20，1-区间 [11, 20]
- f(T) 在 T=2、T=11、T=20 各有一个谷 → 二分会卡死

**经验**：单调 / 凸性是「整体函数」的性质，要直接验证，不能想当然。

## 正解：差分数组

每对 (a, b) 的代价函数是分段常数，只在 4 个点跳变：

| 跳变点 | 变化 | delta |
|---|---|---|
| T = a+1 | 2 → 1 | −1 |
| T = a+b | 1 → 0 | −1 |
| T = a+b+1 | 0 → 1 | +1 |
| T = b+limit+1 | 1 → 2 | +1 |

加上基线（所有 T 默认 +2），每对贡献 5 个端点事件 → diff 数组累加 → 前缀和扫一遍。

```python
def minMoves(nums, limit):
    n = len(nums)
    diff = [0] * (2 * limit + 2)

    for i in range(n // 2):
        a, b = sorted([nums[i], nums[n-1-i]])
        diff[2]         += 2     # 基线
        diff[2*limit+1] -= 2
        diff[a+1]       -= 1     # 进入 1-区间
        diff[b+limit+1] += 1     # 离开 1-区间
        diff[a+b]       -= 1     # 进入谷底
        diff[a+b+1]     += 1     # 离开谷底

    ans, cur = n, 0
    for T in range(2, 2*limit + 1):
        cur += diff[T]
        ans = min(ans, cur)
    return ans
```

复杂度：**O(n + limit)** 时间，O(limit) 空间。

## First principles 角度

1. 每对 (a, b) 是一个分段常数子函数 `gᵢ`
2. f = Σ gᵢ 也是分段常数（线性性）
3. 每个 gᵢ 只在 4 个点跳变（局部性 + 稀疏性）
4. → 用 delta 编码每个个体（O(1) 个事件）→ 累加合并（O(n) 总事件）→ 前缀和实例化（O(limit) sweep）

详见 [patterns/difference-array.md](../patterns/difference-array.md)。

## 我最初的思路 & 为什么错

- ❌ **「两两相加看 sum 分布，取众数」**：贪心陷阱。改 1 次能覆盖一整段 T，不是只能保留原 sum。最优 T 经常不是任何对的当前 sum。
- ❌ **「对 T 二分」**：f(T) 不单调也不单峰（见上面反例）。

教训：**先看整体函数的结构**（用纸笔画几对叠加），别上来就套二分。

## 可视化

[../viz/1674.html](../viz/1674.html) —— 交互式展示每对的 V 形、f(T) 叠加多峰、差分动画（4 个 delta 如何「长」出 cost 函数）。在浏览器打开即可。
