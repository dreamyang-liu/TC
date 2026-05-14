# 区间 DP / 二维 DP 模板（易记版）

## 本质一句话
> **`dp[i][j]` 表示区间 `[i, j]` 上的答案。枚举区间长度从小到大，因为大区间依赖小区间。**

## 区间 DP 模板（最关键的遍历顺序）

```python
def interval_dp(nums):
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    
    # 长度从小到大 ← 关键！
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            # 枚举分割点 k
            for k in range(i, j):
                dp[i][j] = max(dp[i][j], dp[i][k] + dp[k+1][j] + cost(i, k, j))
    
    return dp[0][n-1]
```

## 三种遍历顺序（任选一种，效果等价）

### A. 按长度（最直观）
```python
for length in range(2, n+1):
    for i in range(n - length + 1):
        j = i + length - 1
        ...
```

### B. i 倒序 + j 正序
```python
for i in range(n-1, -1, -1):
    for j in range(i+1, n):
        ...
```

**为什么**：`dp[i][j]` 依赖 `dp[i+1][...]`（更大的 i）和 `dp[...][j-1]`（更小的 j），所以 i 倒序、j 正序。

### C. 记忆化递归（最不容易写错）
```python
from functools import cache

@cache
def dp(i, j):
    if i >= j: return 0
    return max(dp(i, k) + dp(k+1, j) + cost(i, k, j) for k in range(i, j))
```

## 怎么不写错
- **长度从 2 开始**（长度 1 是边界，通常是 0）
- **`j = i + length - 1`**：别写成 `i + length`
- **分割点 k 的范围**：`[i, j-1]` 还是 `[i, j]` 取决于题意（合并 vs 选择）
- **依赖方向**：`dp[i][j]` 依赖 `dp[小][大]` 还是 `dp[大][小]`，先想清楚
- 卡时记忆化最稳：`@cache` 一加，转移直接写

## 三大类区间 DP

### 1. 合并 / 切分类（石子合并、戳气球）

```python
def stone_game(stones):
    n = len(stones)
    # 前缀和加速 cost
    pre = [0]
    for x in stones: pre.append(pre[-1] + x)
    
    dp = [[float('inf')] * n for _ in range(n)]
    for i in range(n): dp[i][i] = 0
    
    for length in range(2, n+1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k+1][j] + pre[j+1] - pre[i])
    return dp[0][n-1]
```

### 2. 回文 / 对称类（最长回文子序列）

```python
def longest_palindrome_subseq(s):
    n = len(s)
    dp = [[0] * n for _ in range(n)]
    for i in range(n): dp[i][i] = 1
    
    for length in range(2, n+1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i+1][j-1] + 2
            else:
                dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    return dp[0][n-1]
```

### 3. 戳气球 / 反向枚举（最后一个操作的）

```python
def max_coins(nums):
    nums = [1] + nums + [1]      # 加哨兵
    n = len(nums)
    dp = [[0] * n for _ in range(n)]
    
    for length in range(2, n):
        for i in range(n - length):
            j = i + length
            # k 是"最后戳破的气球"
            for k in range(i+1, j):
                dp[i][j] = max(dp[i][j], dp[i][k] + dp[k][j] + nums[i]*nums[k]*nums[j])
    return dp[0][n-1]
```

**戳气球的精髓**：正着想"先戳哪个"会让剩下的状态混乱；**倒着想"最后戳哪个"** —— 此时左右两边都还在，状态独立。

## 热身题
- [5. 最长回文子串](https://leetcode.cn/problems/longest-palindromic-substring/)
- [516. 最长回文子序列](https://leetcode.cn/problems/longest-palindromic-subsequence/)
- [647. 回文子串](https://leetcode.cn/problems/palindromic-substrings/)

## 进阶题
- [312. 戳气球](https://leetcode.cn/problems/burst-balloons/)（反向枚举）
- [1000. 合并石头的最低成本](https://leetcode.cn/problems/minimum-cost-to-merge-stones/)
- [664. 奇怪的打印机](https://leetcode.cn/problems/strange-printer/)
- [546. 移除盒子](https://leetcode.cn/problems/remove-boxes/)（三维区间 DP）
- [87. 扰乱字符串](https://leetcode.cn/problems/scramble-string/)
