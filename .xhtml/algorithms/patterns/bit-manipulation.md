# 位运算速查（易记版）

> 面试出现率不高但**一旦出现就完全靠是否记得这些技巧**。

---

## 5 个必会操作

```python
n & 1            # 最低位是否为 1（判奇偶）
n >> 1           # 右移一位（除 2）
n & (n - 1)      # 清掉最低位的 1
n & -n           # 取出最低位的 1（lowbit）
n ^ n == 0       # 自己和自己异或为 0
```

---

## 异或的 3 个性质（一定记住）

1. `a ^ 0 = a`
2. `a ^ a = 0`
3. `a ^ b ^ a = b`（**可交换、可结合**）

**应用**：[136. 只出现一次的数字](https://leetcode.cn/problems/single-number/) — 全部异或，配对的会消掉。

---

## 6 个常用 trick

### 1. 判断是否为 2 的幂
```python
n > 0 and (n & (n - 1)) == 0
```

### 2. 数 1 的个数（popcount）
```python
def popcount(n):
    cnt = 0
    while n:
        n &= n - 1     # 每次消掉最低位的 1
        cnt += 1
    return cnt
```
或 Python 内置：`bin(n).count('1')` 或 `n.bit_count()` (3.10+)。

### 3. 求子集（枚举所有子集）
```python
def all_subsets(n):
    for mask in range(1 << n):
        subset = [i for i in range(n) if mask & (1 << i)]
        yield subset
```

### 4. 枚举子集的子集（状压 DP 经典）
```python
sub = mask
while sub:
    # 处理 sub
    sub = (sub - 1) & mask
```

### 5. 交换两数不用临时变量
```python
a ^= b
b ^= a
a ^= b
```
面试**别这么写**，不可读。仅 trivia。

### 6. 找两个只出现一次的数
```python
def two_singles(nums):
    xor_all = 0
    for x in nums: xor_all ^= x
    diff = xor_all & -xor_all     # 找到 a, b 不同的最低位
    a = b = 0
    for x in nums:
        if x & diff: a ^= x
        else:        b ^= x
    return a, b
```

---

## 状态压缩 DP 模板

> 把"已经访问过哪些"用一个 int 的二进制位表示。**只适用于 n ≤ 20** 左右。

```python
def tsp(graph, n):
    dp = [[float('inf')] * n for _ in range(1 << n)]
    dp[1][0] = 0                          # 起点是 0，mask 只有 bit 0
    for mask in range(1 << n):
        for u in range(n):
            if not (mask & (1 << u)): continue
            if dp[mask][u] == float('inf'): continue
            for v in range(n):
                if mask & (1 << v): continue   # 已访问
                new_mask = mask | (1 << v)
                dp[new_mask][v] = min(dp[new_mask][v], dp[mask][u] + graph[u][v])
    return min(dp[(1 << n) - 1][i] + graph[i][0] for i in range(n))
```

---

## 位运算面试常见题

### A. 计数 / 单一元素
- [136. 只出现一次的数字](https://leetcode.cn/problems/single-number/)
- [137. 只出现一次的数字 II](https://leetcode.cn/problems/single-number-ii/)（三进制思维）
- [260. 只出现一次的数字 III](https://leetcode.cn/problems/single-number-iii/)

### B. 子集与状态压缩
- [78. 子集](https://leetcode.cn/problems/subsets/)（位运算版）
- [847. 访问所有节点的最短路径](https://leetcode.cn/problems/shortest-path-visiting-all-nodes/)
- [1125. 最小的必要团队](https://leetcode.cn/problems/smallest-sufficient-team/)
- [698. 划分为 k 个相等的子集](https://leetcode.cn/problems/partition-to-k-equal-sum-subsets/)

### C. 二进制操作
- [191. 位 1 的个数](https://leetcode.cn/problems/number-of-1-bits/)
- [338. 比特位计数](https://leetcode.cn/problems/counting-bits/)（`dp[i] = dp[i>>1] + (i&1)`）
- [201. 数字范围按位与](https://leetcode.cn/problems/bitwise-and-of-numbers-range/)（公共前缀）

### D. XOR 性质
- [421. 数组中两个数的最大异或值](https://leetcode.cn/problems/maximum-xor-of-two-numbers-in-an-array/)（配合 Trie）

---

## 怎么不写错

- **优先级低**：`n & 1 == 0` 实际是 `n & (1 == 0)`，所以一定**加括号**：`(n & 1) == 0`
- **负数位运算**在 Python 是无限位（补码），跟 C++/Java 不同。面试 Python 题不影响，跨语言要小心
- **`1 << n` 不是 `2 ** n`** —— 实际上数值相等，但位运算更快
- **bitmask 状压**只在 n 很小（≤ 20）时用，再大内存炸了

---

## 一句话总结

> **位运算是"用整数当 set 或多个 bool 的紧凑表示"。面试遇到 n ≤ 20 + "枚举子集"型题立刻想状压。**
