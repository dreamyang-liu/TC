# 动态规划基础模板（易记版）

## 本质一句话
> **DP = 带记忆化的递归。把"重叠的子问题"算一次存起来。**

## 四步走（写任何 DP 都按这个顺序）

1. **定义状态**：`dp[i][j]` 表示什么？（最关键！描述清楚）
2. **写转移方程**：`dp[i][j] = ?` 用更小的状态表示
3. **初始化 / 边界**：最小的子问题答案是什么？
4. **决定遍历顺序**：保证用到的状态都已经算过

## 一维 DP 模板

### 模板 A：爬楼梯型（线性递推）

```python
def climb(n):
    if n <= 2: return n
    dp = [0] * (n + 1)
    dp[1], dp[2] = 1, 2
    for i in range(3, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    return dp[n]
```

**空间优化**：只用到前两个状态 → 用两个变量代替整个数组：
```python
a, b = 1, 2
for _ in range(3, n + 1):
    a, b = b, a + b
return b
```

### 模板 B：最长递增子序列（LIS）

```python
def lis(nums):
    n = len(nums)
    dp = [1] * n                # dp[i] = 以 i 结尾的 LIS 长度
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
```

**O(n log n) 优化**：维护一个 `tails` 数组（贪心 + 二分），见 [300. 最长递增子序列](https://leetcode.cn/problems/longest-increasing-subsequence/)。

## 二维 DP 模板

### 模板 C：最长公共子序列（LCS）

```python
def lcs(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    return dp[m][n]
```

**口诀**：相等 → 看左上角加 1；不等 → 看左和上的最大值。

### 模板 D：编辑距离（72 题）

```python
def edit_distance(a, b):
    m, n = len(a), len(b)
    dp = [[0] * (n+1) for _ in range(m+1)]
    for i in range(m+1): dp[i][0] = i
    for j in range(n+1): dp[0][j] = j
    for i in range(1, m+1):
        for j in range(1, n+1):
            if a[i-1] == b[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i-1][j],     # 删
                                    dp[i][j-1],     # 插
                                    dp[i-1][j-1])   # 改
    return dp[m][n]
```

## 背包模板

### 0/1 背包（每件最多选一次）

```python
def knapsack_01(w, v, W):
    n = len(w)
    dp = [0] * (W + 1)
    for i in range(n):
        for j in range(W, w[i] - 1, -1):     # 倒序！
            dp[j] = max(dp[j], dp[j - w[i]] + v[i])
    return dp[W]
```

### 完全背包（每件可选无数次）

```python
def knapsack_full(w, v, W):
    n = len(w)
    dp = [0] * (W + 1)
    for i in range(n):
        for j in range(w[i], W + 1):         # 正序！
            dp[j] = max(dp[j], dp[j - w[i]] + v[i])
    return dp[W]
```

**口诀**：
- **0/1 背包：物品外层，容量倒序** —— 保证当轮不会用到自己更新过的值
- **完全背包：物品外层，容量正序** —— 允许重复使用，要的就是用自己更新

### 背包变形对照表

| 问题 | 转移 |
|------|------|
| 求**最大价值** | `dp[j] = max(dp[j], dp[j-w]+v)` |
| 求**方案数** | `dp[j] += dp[j-w]` |
| 求**能否装满** | `dp[j] |= dp[j-w]` |
| **排列**（顺序敏感，如爬楼梯） | 容量外层，物品内层 |
| **组合**（无序） | 物品外层，容量内层 |

## 怎么不写错
- **状态定义先写注释**：`# dp[i][j] = 前 i 个数中，和为 j 的方案数`
- **遍历顺序**：先想清楚 `dp[i][j]` 依赖谁，被依赖的要先算
- **边界 / 空集**：`dp[0]` 和 `dp[0][0]` 通常代表"空集"，仔细想初值
- 卡内存 → 滚动数组 / 一维 DP
- **记忆化 vs 迭代**：先用记忆化写出递归（直观），再翻成迭代（高效）

## 记忆化递归模板（最简单 DP 写法）

```python
from functools import cache

@cache
def f(i, j):
    if base_case: return ...
    return combine(f(i-1, j), f(i, j-1), ...)
```

写不出迭代版的题，先用记忆化递归通过！

## 热身题
- [70. 爬楼梯](https://leetcode.cn/problems/climbing-stairs/)
- [198. 打家劫舍](https://leetcode.cn/problems/house-robber/)
- [53. 最大子数组和](https://leetcode.cn/problems/maximum-subarray/)
- [300. 最长递增子序列](https://leetcode.cn/problems/longest-increasing-subsequence/)
- [322. 零钱兑换](https://leetcode.cn/problems/coin-change/)

## 进阶题
- [1143. 最长公共子序列](https://leetcode.cn/problems/longest-common-subsequence/)
- [72. 编辑距离](https://leetcode.cn/problems/edit-distance/)
- [416. 分割等和子集](https://leetcode.cn/problems/partition-equal-subset-sum/)（0/1 背包）
- [494. 目标和](https://leetcode.cn/problems/target-sum/)（背包方案数）
- [518. 零钱兑换 II](https://leetcode.cn/problems/coin-change-ii/)（完全背包方案数）
- [10. 正则表达式匹配](https://leetcode.cn/problems/regular-expression-matching/)
- 区间 DP → 见 [interval-dp.md](interval-dp.md)
- 状压 DP → [847. 访问所有节点的最短路径](https://leetcode.cn/problems/shortest-path-visiting-all-nodes/)
- 树形 DP → [337. 打家劫舍 III](https://leetcode.cn/problems/house-robber-iii/)
