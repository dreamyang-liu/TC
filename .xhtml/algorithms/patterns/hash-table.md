# 哈希表套路（易记版）

## 本质一句话
> **用空间换时间：把"找过的东西"存起来，下次 O(1) 查。**

## 三大常用模式

### 模式 1：两数之和（一边遍历一边查）

```python
def two_sum(nums, target):
    seen = {}
    for i, x in enumerate(nums):
        if target - x in seen:
            return [seen[target - x], i]
        seen[x] = i        # 注意：先查后存（避免 x 自己用自己）
```

**口诀**：**先查后存** —— 防止元素和自己配对。

### 模式 2：前缀和 + 哈希表（找和为 K 的子数组）

```python
def subarray_sum(nums, k):
    cnt = {0: 1}              # 前缀和为 0 出现 1 次（空前缀）
    pre = ans = 0
    for x in nums:
        pre += x
        ans += cnt.get(pre - k, 0)    # 找之前是否有 pre - k
        cnt[pre] = cnt.get(pre, 0) + 1
    return ans
```

**核心**：子数组 `(j, i]` 的和 = `pre[i] - pre[j]`。问"有几个 j 使差等于 k" → 在哈希表里查 `pre - k`。

**口诀**：**初始化 `{0: 1}` 是为空前缀** —— 否则会漏掉 `nums[0..i]` 这种从头开始的子数组。

### 模式 3：分组 / 计数 / 异位词

```python
from collections import Counter, defaultdict

def group_anagrams(strs):
    groups = defaultdict(list)
    for s in strs:
        key = tuple(sorted(s))      # 或 tuple(Counter(s).items())
        groups[key].append(s)
    return list(groups.values())
```

**选 key 的技巧**：
- 字符串异位词 → 排序后的串 / 字符计数元组
- 数对 → `tuple(sorted([a, b]))`
- 复杂状态 → `frozenset` 或 tuple

## Python 哈希表速查

```python
d = {}
d.get(k, default)              # 不存在返回默认
d.setdefault(k, []).append(x)  # 不存在初始化为 []，再 append

from collections import defaultdict, Counter
dd = defaultdict(int)          # 缺失自动 0
dd = defaultdict(list)         # 缺失自动 []

c = Counter("abca")            # {'a': 2, 'b': 1, 'c': 1}
c.most_common(2)               # [('a', 2), ('b', 1)]
c1 - c2                        # 只保留正数差（Counter 减法）
```

## 怎么不写错
- **两数之和：先查后存**，否则会用自己匹配自己
- **前缀和：初始 `{0: 1}`**，覆盖"从头开始"的子数组
- **哈希 key 必须可哈希**：list 不行，要转 tuple
- 自定义对象做 key → 实现 `__hash__` 和 `__eq__`

## 进阶套路：滚动哈希（Rabin-Karp）

字符串子串匹配 → 把子串当数字看，滑窗时 O(1) 更新哈希值。
适用：[1044. 最长重复子串](https://leetcode.cn/problems/longest-duplicate-substring/)。

## 热身题
- [1. 两数之和](https://leetcode.cn/problems/two-sum/)
- [49. 字母异位词分组](https://leetcode.cn/problems/group-anagrams/)
- [560. 和为 K 的子数组](https://leetcode.cn/problems/subarray-sum-equals-k/)
- [128. 最长连续序列](https://leetcode.cn/problems/longest-consecutive-sequence/)
- [217. 存在重复元素](https://leetcode.cn/problems/contains-duplicate/)

## 进阶题
- [454. 四数相加 II](https://leetcode.cn/problems/4sum-ii/)（两两预存）
- [974. 和可被 K 整除的子数组](https://leetcode.cn/problems/subarray-sums-divisible-by-k/)
- [437. 路径总和 III](https://leetcode.cn/problems/path-sum-iii/)（树上前缀和 + 哈希）
- [146. LRU 缓存](https://leetcode.cn/problems/lru-cache/)（哈希 + 双向链表）
- [355. 设计推特](https://leetcode.cn/problems/design-twitter/)
