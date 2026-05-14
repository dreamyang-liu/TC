# 拓扑排序模板（易记版）

## 本质一句话
> **每次取一个「入度为 0」的点输出，然后删掉它的出边。能输出全部 n 个 → 无环；否则有环。**

## 最简模板（Kahn / BFS 法）

```python
from collections import deque

def topo_sort(n, edges):    # edges: [u -> v]
    g = [[] for _ in range(n)]
    indeg = [0] * n
    for u, v in edges:
        g[u].append(v)
        indeg[v] += 1

    q = deque(i for i in range(n) if indeg[i] == 0)
    order = []

    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    return order if len(order) == n else []   # [] 表示有环
```

## 怎么不写错
- **建图方向**：「先 a 后 b」是 `a → b`，`indeg[b] += 1`
- **入度数组别忘初始化**
- **判环**：最后看输出长度是否等于 n
- **字典序最小拓扑序**：把 `deque` 换成 `heapq`

## DFS 法（三色标记，找环 + 拓扑序）

```python
def topo_sort_dfs(n, g):
    color = [0] * n           # 0 白未访问, 1 灰在栈, 2 黑已完成
    order = []

    def dfs(u):
        color[u] = 1
        for v in g[u]:
            if color[v] == 1: return False   # 灰→灰 = 有环
            if color[v] == 0 and not dfs(v): return False
        color[u] = 2
        order.append(u)           # 后序入栈
        return True

    for i in range(n):
        if color[i] == 0 and not dfs(i):
            return []
    return order[::-1]            # 后序反转 = 拓扑序
```

**口诀**：**灰碰灰就是环**。

## 应用模式

| 题目类型 | 套路 |
|---------|------|
| 课程能否修完 | 检查能否输出全部节点 |
| 给出修课顺序 | 直接输出拓扑序 |
| 字典序最小 | Kahn + 最小堆 |
| 多源 BFS 类似题 | 入度为 0 全塞进队列 |
| DAG 上 DP | 按拓扑序更新（保证依赖先算完） |

## 热身题
- [207. 课程表](https://leetcode.cn/problems/course-schedule/)
- [210. 课程表 II](https://leetcode.cn/problems/course-schedule-ii/)
- [802. 找到最终的安全状态](https://leetcode.cn/problems/find-eventual-safe-states/)（反图拓扑）

## 进阶题
- [269. 火星词典](https://leetcode.cn/problems/alien-dictionary/)
- [310. 最小高度树](https://leetcode.cn/problems/minimum-height-trees/)（从叶子向内剥）
- [329. 矩阵中的最长递增路径](https://leetcode.cn/problems/longest-increasing-path-in-a-matrix/)（拓扑序 + DP）
- [2192. 有向无环图中一个节点的所有祖先](https://leetcode.cn/problems/all-ancestors-of-a-node-in-a-directed-acyclic-graph/)
- [1857. 有向图中最大颜色值](https://leetcode.cn/problems/largest-color-value-in-a-directed-graph/)
