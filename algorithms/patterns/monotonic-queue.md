# 单调队列模板（易记版）

## 本质一句话
> **滑动窗口 + 单调栈**。队尾入队时清理被打败的元素，队头出队时清理过期元素。

## 最简模板（滑动窗口最大值）

```python
from collections import deque

def max_sliding_window(nums, k):
    q = deque()    # 存下标，对应值单调递减
    ans = []
    for i, x in enumerate(nums):
        # 1. 队尾入：清掉打不过 x 的
        while q and nums[q[-1]] <= x:
            q.pop()
        q.append(i)

        # 2. 队头：清掉滑出窗口的（左边界 = i - k + 1）
        if q[0] <= i - k:
            q.popleft()

        # 3. 窗口形成后记录答案
        if i >= k - 1:
            ans.append(nums[q[0]])
    return ans
```

## 三步走（每步独立、顺序固定）

1. **队尾维护单调性**：新元素来了，把队尾比它「弱」的都弹掉
2. **队头维护窗口**：超出窗口范围的下标从队头弹出
3. **取答案**：队头就是当前窗口的最值

## 单调栈 vs 单调队列

| | 单调栈 | 单调队列 |
|---|---|---|
| 操作端 | 一端进出 | **两端都动**（队尾进，队头也可能出） |
| 关注 | 「下一个/上一个 更大/更小」 | 「**窗口内**的最值」 |
| 数据结构 | `list`（append/pop） | `deque`（append/pop/popleft） |

记忆：**队列多一个"过期"概念**（窗口有左边界）。

## 怎么不写错
- **存下标，不存值**（要靠下标判过期）
- **三步顺序：队尾 → 队头 → 取答案**
- **`<=` 还是 `<`**：相等时也弹掉旧的（用 `<=`），队列更短更高效
- 想找**最小值** → 把 `<=` 改成 `>=`（队列改成单调递增）

## 热身题
- [239. 滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum/)
- [1438. 绝对差不超过限制的最长连续子数组](https://leetcode.cn/problems/longest-continuous-subarray-with-absolute-diff-less-than-or-equal-to-limit/)（同时维护 max 和 min 两个单调队列）

## 进阶题
- [862. 和至少为 K 的最短子数组](https://leetcode.cn/problems/shortest-subarray-with-sum-at-least-k/)（前缀和 + 单调队列）
- [918. 环形子数组的最大和](https://leetcode.cn/problems/maximum-sum-circular-subarray/)
- [1696. 跳跃游戏 VI](https://leetcode.cn/problems/jump-game-vi/)（DP + 单调队列优化）
- [LCP 40. 心算挑战](https://leetcode.cn/problems/uOAnQW/)
