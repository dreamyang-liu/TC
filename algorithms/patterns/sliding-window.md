# 滑动窗口模板（易记版）

## 本质一句话
> **右指针扩张，左指针在窗口「不合法」时收缩。**

## 最简模板（最长合法窗口）

```python
def sliding_window(s):
    from collections import Counter
    window = Counter()
    left = 0
    ans = 0

    for right, c in enumerate(s):
        window[c] += 1                  # 1. 扩张

        while not_valid(window):        # 2. 不合法就缩
            window[s[left]] -= 1
            if window[s[left]] == 0:
                del window[s[left]]
            left += 1

        ans = max(ans, right - left + 1)   # 3. 此时合法，更新答案

    return ans
```

## 两种变体（只差答案更新的位置）

| 类型 | 收缩条件 | 答案更新位置 |
|------|---------|------------|
| **最长**合法窗口 | `while 不合法` | while **外**（while 出来后窗口合法） |
| **最短**合法窗口 | `while 合法`（并在 while 内更新） | while **内** |

```python
# 最短合法窗口
while valid(window):
    ans = min(ans, right - left + 1)   # 在 while 内更新
    # 然后缩 left
```

## 怎么不写错
- **想清楚窗口状态**：计数 / 和 / 不同字符数 / 最大值 → 写在注释里
- **进出对称**：进入做什么，离开就反着做一遍
- **`right` 每轮 +1，`left` 只在 while 里动**
- "恰好 K" = "至多 K" − "至多 K-1"（两个滑窗相减）

## 热身题
- [3. 无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/)
- [209. 长度最小的子数组](https://leetcode.cn/problems/minimum-size-subarray-sum/)
- [438. 找到字符串中所有字母异位词](https://leetcode.cn/problems/find-all-anagrams-in-a-string/)
- [1004. 最大连续 1 的个数 III](https://leetcode.cn/problems/max-consecutive-ones-iii/)

## 进阶题
- [76. 最小覆盖子串](https://leetcode.cn/problems/minimum-window-substring/)
- [992. K 个不同整数的子数组](https://leetcode.cn/problems/subarrays-with-k-different-integers/)
- [395. 至少有 K 个重复字符的最长子串](https://leetcode.cn/problems/longest-substring-with-at-least-k-repeating-characters/)
- [239. 滑动窗口最大值](https://leetcode.cn/problems/sliding-window-maximum/)（配合单调队列）
