# 贪心模板（易记版）

## 本质一句话
> **每步都做"局部最优"的选择，且能证明它通向全局最优。**

⚠️ 难点不在写代码，**难在判断"能不能贪心"**。如果不能严格证明，那就回 DP。

---

## 两种最常见的证明方式

### A. Exchange Argument（交换论证）
**假设**最优解和贪心解不同 → 把它们 differ 的第一处交换 → 证明不变差 → 矛盾。

> 例：[455. 分发饼干](https://leetcode.cn/problems/assign-cookies/) — 把最大饼干给胃口最大的小孩。如果有更优解先给胃口小的，可以交换不变差。

### B. Greedy Stays Ahead（贪心始终领先）
**归纳**地证明贪心在每一步都不比最优解差。

> 例：[435. 无重叠区间](https://leetcode.cn/problems/non-overlapping-intervals/) — 按右端点排序，每次选最早结束的。每步选完后，剩余可选空间 ≥ 任何最优解的剩余空间。

---

## 5 个常见套路

### 1. 按某 key 排序后扫一遍
- 区间问题 → 按 **右端点**或 **左端点**排序
- 任务调度 → 按 **deadline** 或 **profit/time** 排序
- 跳跃问题 → 维护**当前能到的最远**

### 2. 双堆 / 优先队列
- 每次取局部最优 → 堆顶
- 例：[857. 雇佣 K 名工人](https://leetcode.cn/problems/minimum-cost-to-hire-k-workers/)

### 3. 抵消 / cancel
- 每次相邻两个出现就抵消（如多数元素 Boyer-Moore）
- 例：[169. 多数元素](https://leetcode.cn/problems/majority-element/)

### 4. 反悔贪心
- 先贪心选，**遇到更好的就反悔**（替换前面选的）
- 用堆维护可反悔的集合
- 例：[630. 课程表 III](https://leetcode.cn/problems/course-schedule-iii/)

### 5. 双指针贪心
- 两端逼近，每步移动**让答案更可能优**的那端
- 例：[11. 盛最多水的容器](https://leetcode.cn/problems/container-with-most-water/)

---

## 反悔贪心模板（最不容易想到的那种）

```python
import heapq

def schedule_courses(courses):
    courses.sort(key=lambda c: c[1])      # 按 deadline 排序
    total = 0
    heap = []                              # 最大堆（存 -duration）
    for duration, deadline in courses:
        total += duration
        heapq.heappush(heap, -duration)
        if total > deadline:               # 装不下
            total += heapq.heappop(heap)   # 反悔：扔掉最长的
    return len(heap)
```

**口诀**：**先贪婪装，装不下就扔最贵的**。

---

## 怎么不写错

- **永远问自己一句**："我能证明贪心正确吗？"
- 不能立刻证明 → 至少举 3 个反例试一下
- **反例没找到 ≠ 一定对**，但是个信号
- 排序题一定要确定**按什么排**，往往题面没说

---

## 贪心 vs DP

| 特征 | 贪心 | DP |
|------|------|-----|
| 子问题 | 局部决策**不回头** | **保留所有选择**，最后挑最优 |
| 复杂度 | 通常 O(n log n) | 通常 O(n²) 或更高 |
| 适用 | 有"matroid"结构，最优子结构 | 重叠子问题 + 最优子结构 |
| 不确定能用就 | **回退用 DP** | 暴力 DP 永远兜底 |

---

## 热身题
- [455. 分发饼干](https://leetcode.cn/problems/assign-cookies/)
- [122. 买卖股票的最佳时机 II](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock-ii/)
- [435. 无重叠区间](https://leetcode.cn/problems/non-overlapping-intervals/)
- [55. 跳跃游戏](https://leetcode.cn/problems/jump-game/)
- [134. 加油站](https://leetcode.cn/problems/gas-station/)

## 进阶题
- [630. 课程表 III](https://leetcode.cn/problems/course-schedule-iii/)（反悔贪心）
- [1024. 视频拼接](https://leetcode.cn/problems/video-stitching/)
- [763. 划分字母区间](https://leetcode.cn/problems/partition-labels/)
- [502. IPO](https://leetcode.cn/problems/ipo/)（双堆）
- [857. 雇佣 K 名工人的最低成本](https://leetcode.cn/problems/minimum-cost-to-hire-k-workers/)
- [871. 最低加油次数](https://leetcode.cn/problems/minimum-number-of-refueling-stops/)
