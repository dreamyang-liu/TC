# 并查集模板（易记版）

## 本质一句话
> **每个集合用一棵树表示，根节点代表整个集合。`find` 找根，`union` 让一棵树挂到另一棵下。**

## 最简模板（路径压缩，足够通过 99% 的题）

```python
class UnionFind:
    def __init__(self, n):
        self.p = list(range(n))   # p[i] = i 的父节点（初始指向自己）
        self.cnt = n              # 连通分量数

    def find(self, x):
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])   # 路径压缩
        return self.p[x]

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False          # 已经在一组
        self.p[rx] = ry           # 简单合并：直接挂上
        self.cnt -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)
```

## 进阶模板（按秩合并，最坏 O(α(n)) ≈ O(1)）

只在 `union` 改一点：
```python
def __init__(self, n):
    self.p = list(range(n))
    self.size = [1] * n           # 集合大小
    self.cnt = n

def union(self, x, y):
    rx, ry = self.find(x), self.find(y)
    if rx == ry: return False
    if self.size[rx] < self.size[ry]:
        rx, ry = ry, rx           # 让 rx 是大的
    self.p[ry] = rx               # 小挂大
    self.size[rx] += self.size[ry]
    self.cnt -= 1
    return True
```

## 怎么不写错
- **`find` 一定要带路径压缩**：`self.p[x] = self.find(self.p[x])`
- **`union` 一定要先 `find`** 两个根再合并，不要直接 `self.p[x] = y`
- 比较两个元素是否同组用 `find(x) == find(y)`，不是 `p[x] == p[y]`
- 想动态查询集合大小 → 多维护一个 `size[]`

## 三大应用场景

1. **判连通**：图里有没有路径？两个点同组？
2. **数连通分量**：维护 `cnt`，每次 union 成功就 `cnt -= 1`
3. **离线处理 / 时光倒流**：从删边变成加边（因为并查集只支持合并，不支持拆分）

## 带权并查集（进阶）

每条边带权（如比例、距离）。维护 `w[x] = x 到父节点的权值`，路径压缩时也要更新权值。
适用：[399. 除法求值](https://leetcode.cn/problems/evaluate-division/)。

## 热身题
- [547. 省份数量](https://leetcode.cn/problems/number-of-provinces/)
- [200. 岛屿数量](https://leetcode.cn/problems/number-of-islands/)
- [684. 冗余连接](https://leetcode.cn/problems/redundant-connection/)
- [990. 等式方程的可满足性](https://leetcode.cn/problems/satisfiability-of-equality-equations/)

## 进阶题
- [128. 最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/)
- [399. 除法求值](https://leetcode.cn/problems/evaluate-division/)（带权并查集）
- [721. 账户合并](https://leetcode.cn/problems/accounts-merge/)
- [803. 打砖块](https://leetcode.cn/problems/bricks-falling-when-hit/)（时光倒流）
- [1697. 检查边长度限制的路径是否存在](https://leetcode.cn/problems/checking-existence-of-edge-length-limited-paths/)（离线 + 排序）
- [685. 冗余连接 II](https://leetcode.cn/problems/redundant-connection-ii/)
