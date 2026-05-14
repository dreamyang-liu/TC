# 树形 DP 模板（易记版）

## 本质一句话
> **后序遍历 + 在每个节点返回一个 / 几个状态，让父节点用来组合答案。**

通常状态是「**以当前节点为根的子树**」的某种聚合。

---

## 单状态模板（最简单）

```python
def tree_dp(root):
    def dfs(node):
        if not node: return 0
        l = dfs(node.left)
        r = dfs(node.right)
        return combine(node.val, l, r)   # 用左右子树的结果组合
    return dfs(root)
```

例：**最大深度** `combine = lambda v, l, r: 1 + max(l, r)`

---

## 两个返回值的诀窍（最常考）

**核心思想**：节点要给父亲返回**自己**的某种值，但全局答案是**"经过当前节点"**的另一种值。

```python
def diameter(root):
    ans = 0
    def depth(node):
        nonlocal ans
        if not node: return 0
        l = depth(node.left)
        r = depth(node.right)
        ans = max(ans, l + r)       # ← 经过 node 的最长（不传给父）
        return 1 + max(l, r)        # ← 给父亲用的"深度"
    depth(root)
    return ans
```

**两种返回值区分清楚：**
- **传给父节点的**：能继续拼接的"链状"信息
- **更新全局答案的**：可以"分叉"的整条路径

---

## 经典题：二叉树最大路径和（124）

```python
def max_path_sum(root):
    ans = float('-inf')
    def dfs(node):
        nonlocal ans
        if not node: return 0
        l = max(0, dfs(node.left))      # 负贡献不要
        r = max(0, dfs(node.right))
        ans = max(ans, node.val + l + r)
        return node.val + max(l, r)     # 链状返回
    dfs(root)
    return ans
```

⚠️ **关键**：`max(0, ...)` —— 子树负贡献直接抛弃。

---

## 选 / 不选模板（打家劫舍 III）

每个节点有**两种状态**：选 / 不选。返回 `(选, 不选)` 元组。

```python
def rob(root):
    def dfs(node):
        if not node: return (0, 0)     # (rob, not_rob)
        lr, lnr = dfs(node.left)
        rr, rnr = dfs(node.right)
        return (node.val + lnr + rnr,        # 选 node → 子节点不能选
                max(lr, lnr) + max(rr, rnr)) # 不选 node → 子节点随意
    return max(dfs(root))
```

**口诀**：**选当前 → 子不能选；不选当前 → 子取最大**。

---

## 树的重心 / 直径 / 中心（n-ary 树版）

```python
def diameter_nary(root):
    ans = 0
    def dfs(node):
        nonlocal ans
        depths = []
        for child in node.children:
            depths.append(dfs(child))
        depths.sort(reverse=True)
        # 经过 node 的最长 = 两条最深的链
        top2 = sum(depths[:2])
        ans = max(ans, top2)
        return 1 + (depths[0] if depths else 0)
    dfs(root)
    return ans
```

---

## 换根 DP（最难的树形 DP）

**问题**：要求每个节点为根时的某个值（不能 N 次 DFS，太慢）。

**思路**：
1. 第 1 次 DFS：求出**以 0 为根**时每个节点的值（普通树形 DP）
2. 第 2 次 DFS：从根开始往下走，**根据父子关系增量更新**

例：[834. 树中距离之和](https://leetcode.cn/problems/sum-of-distances-in-tree/)
```python
def sum_of_distances(n, edges):
    g = [[] for _ in range(n)]
    for u, v in edges:
        g[u].append(v); g[v].append(u)

    size = [1] * n      # 子树大小
    ans = [0] * n       # 答案

    # 第 1 次 DFS：算出 ans[0]
    def dfs1(u, p):
        for v in g[u]:
            if v == p: continue
            dfs1(v, u)
            size[u] += size[v]
            ans[0] += ans[0]      # 这里需要更细致的累加，见原题解
    # ...（详见原题）
```

换根 DP 的核心：**从父亲推到儿子时的 +/- 修正项**。

---

## 怎么不写错

- **base case**：空节点返回 **0 / None / 哨兵元组**（看题）
- **后序遍历**：先递归子，再处理自己
- **"经过当前节点"和"延伸到当前节点"分开**
- 多个状态用 **元组返回**，比改全局变量清晰

---

## 热身题
- [104. 二叉树的最大深度](https://leetcode.cn/problems/maximum-depth-of-binary-tree/)
- [543. 二叉树的直径](https://leetcode.cn/problems/diameter-of-binary-tree/)
- [110. 平衡二叉树](https://leetcode.cn/problems/balanced-binary-tree/)
- [687. 最长同值路径](https://leetcode.cn/problems/longest-univalue-path/)

## 进阶题
- [124. 二叉树中的最大路径和](https://leetcode.cn/problems/binary-tree-maximum-path-sum/)
- [337. 打家劫舍 III](https://leetcode.cn/problems/house-robber-iii/)（选 / 不选）
- [968. 监控二叉树](https://leetcode.cn/problems/binary-tree-cameras/)（三状态：装 / 被覆盖 / 没覆盖）
- [834. 树中距离之和](https://leetcode.cn/problems/sum-of-distances-in-tree/)（换根 DP）
- [310. 最小高度树](https://leetcode.cn/problems/minimum-height-trees/)
- [1245. 树的直径（n-ary）](https://leetcode.cn/problems/tree-diameter/)
