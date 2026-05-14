# BFS 模板（易记版）

## 本质一句话
> **一层一层往外扩。第一次访问到某点的步数 = 起点到它的最短步数（边权为 1）。**

## 最简模板（按层遍历，知道当前在第几层）

```python
from collections import deque

def bfs(start):
    q = deque([start])
    visited = {start}
    step = 0

    while q:
        for _ in range(len(q)):       # 关键：先冻结这一层的大小
            node = q.popleft()
            if is_target(node):
                return step
            for nxt in neighbors(node):
                if nxt not in visited:
                    visited.add(nxt)  # 关键：入队时就标记
                    q.append(nxt)
        step += 1                     # 一层走完，步数 +1

    return -1
```

## 怎么不写错

| 易错点 | 正确做法 |
|--------|---------|
| 不需要分层 | 把 `for _ in range(len(q))` 去掉即可 |
| 重复入队导致超时 | **入队时就 `visited.add()`**，不要等出队再标 |
| 起点要不要算 step 0 | 上面模板：起点是 step 0 |
| 网格 BFS | `dirs = [(-1,0),(1,0),(0,-1),(0,1)]` 上下左右 |

## 网格 BFS 模板

```python
def shortest_path(grid):
    m, n = len(grid), len(grid[0])
    q = deque([(0, 0)])
    visited = {(0, 0)}
    step = 0
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while q:
        for _ in range(len(q)):
            r, c = q.popleft()
            if (r, c) == (m-1, n-1):
                return step
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < m and 0 <= nc < n and (nr, nc) not in visited and grid[nr][nc] == 0:
                    visited.add((nr, nc))
                    q.append((nr, nc))
        step += 1
    return -1
```

## 多源 BFS（多个起点同时扩）

把所有起点**一开始就全塞进队列**，其它代码不变。
应用：[腐烂的橘子](https://leetcode.cn/problems/rotting-oranges/)、[01 矩阵](https://leetcode.cn/problems/01-matrix/)。

## 双向 BFS（已知起点终点，优化常数）

从两端同时扩，谁的层更小就扩谁，相遇即可。适合**搜索空间巨大**的题（如单词接龙）。

## BFS vs DFS 怎么选
- **最短步数 / 最少操作** → BFS（边权 1）或 Dijkstra（边权正）
- **是否存在路径 / 连通分量** → 两个都行
- **所有路径 / 排列组合** → DFS / 回溯

## 热身题
- [102. 二叉树的层序遍历](https://leetcode.cn/problems/binary-tree-level-order-traversal/)
- [200. 岛屿数量](https://leetcode.cn/problems/number-of-islands/)
- [994. 腐烂的橘子](https://leetcode.cn/problems/rotting-oranges/)（多源 BFS）

## 进阶题
- [127. 单词接龙](https://leetcode.cn/problems/word-ladder/)（双向 BFS）
- [752. 打开转盘锁](https://leetcode.cn/problems/open-the-lock/)
- [542. 01 矩阵](https://leetcode.cn/problems/01-matrix/)（多源 BFS）
- [1293. 网格中的最短路径](https://leetcode.cn/problems/shortest-path-in-a-grid-with-obstacles-elimination/)（状态扩维）
- [847. 访问所有节点的最短路径](https://leetcode.cn/problems/shortest-path-visiting-all-nodes/)（状压 BFS）
