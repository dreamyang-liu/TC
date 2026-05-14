# Dijkstra 最短路模板（易记版）

## 本质一句话
> **带优先队列的 BFS：每次取「当前已知距离最小」的未确定节点，用它去松弛邻居。** 只适用于**非负边权**。

## 最简模板（堆优化版）

```python
import heapq

def dijkstra(n, edges, src):    # edges: [(u, v, w)] 有向带权
    g = [[] for _ in range(n)]
    for u, v, w in edges:
        g[u].append((v, w))

    dist = [float('inf')] * n
    dist[src] = 0
    pq = [(0, src)]              # (dist, node)

    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:           # 已经被更短的路径松弛过，跳过
            continue
        for v, w in g[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(pq, (nd, v))

    return dist
```

复杂度：**O((V + E) log V)**。

## 三个关键点（一行都别少）

1. **`pq` 里存 `(距离, 节点)`** —— 距离放第一位，自动按距离排序
2. **弹出时检查 `d > dist[u]`** —— 跳过过期节点（懒删除，比 `visited` 更简洁）
3. **松弛后再 push** —— 不要预先把所有节点放进堆

## 怎么不写错
- **不能有负权边**！有负权 → 用 Bellman-Ford / SPFA
- 堆里允许有过期记录，**靠 `d > dist[u]` 跳过**，不要试图删除
- 想还原**路径** → 维护 `parent[v] = u`，再从终点回溯
- **无向图** → 建图时双向加边

## 变体 1：A* 搜索

把 `pq` 的 key 从 `dist[v]` 换成 `dist[v] + h(v)`，`h(v)` 是终点的估计距离（启发函数）。其它一模一样。

## 变体 2：分层图 / 状态扩维

例：[787. K 站中转最便宜机票](https://leetcode.cn/problems/cheapest-flights-within-k-stops/)。
把节点扩成 `(city, k)`，剩余中转次数也变成状态的一部分。

## 何时不用 Dijkstra
- **边权全为 1** → 直接 BFS，O(V+E)
- **边权只有 0/1** → 0-1 BFS（双端队列：0 边塞队首，1 边塞队尾）
- **有负权** → Bellman-Ford / SPFA
- **找所有点对最短路** → Floyd-Warshall（V³）

## 0-1 BFS（双端队列版 Dijkstra）

```python
from collections import deque

def zero_one_bfs(n, g, src):
    dist = [float('inf')] * n
    dist[src] = 0
    dq = deque([src])
    while dq:
        u = dq.popleft()
        for v, w in g[u]:        # w 只能是 0 或 1
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                if w == 0: dq.appendleft(v)
                else:      dq.append(v)
    return dist
```

## 热身题
- [743. 网络延迟时间](https://leetcode.cn/problems/network-delay-time/)
- [1631. 最小体力消耗路径](https://leetcode.cn/problems/path-with-minimum-effort/)（最大化最小 → 改成 max 松弛）
- [787. K 站中转内最便宜的航班](https://leetcode.cn/problems/cheapest-flights-within-k-stops/)（扩维）

## 进阶题
- [1514. 概率最大的路径](https://leetcode.cn/problems/path-with-maximum-probability/)（最大堆 + 乘法）
- [1928. 规定时间内到达终点的最小花费](https://leetcode.cn/problems/minimum-cost-to-reach-destination-in-time/)
- [2045. 到达目的地的第二短时间](https://leetcode.cn/problems/second-minimum-time-to-reach-destination/)
- [1976. 到达目的地的方案数](https://leetcode.cn/problems/number-of-ways-to-arrive-at-destination/)（Dijkstra + DP 计数）
- [407. 接雨水 II](https://leetcode.cn/problems/trapping-rain-water-ii/)（最小堆 + BFS）
