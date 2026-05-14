# 回溯模板（易记版）

## 本质一句话
> **决策树 DFS：选 → 递归 → 撤销。** 路径是"做过的选择"，选择列表是"当前能做的选择"。

## 万能三件套

```python
def backtrack(path, choices):
    if 满足结束条件:
        ans.append(path[:])         # 注意 path[:] 拷贝！
        return
    for c in choices:
        if not_valid(c): continue   # 剪枝
        path.append(c)              # 1. 选
        backtrack(path, new_choices)# 2. 递归
        path.pop()                  # 3. 撤销
```

**核心**：进入 for 之前的状态 == 这一层 for 结束后的状态（撤销保证状态对称）。

## 三大问题族

### 1. 子集（每个元素选 / 不选）

```python
def subsets(nums):
    ans = []
    def dfs(i, path):
        if i == len(nums):
            ans.append(path[:])
            return
        dfs(i + 1, path)              # 不选
        path.append(nums[i])
        dfs(i + 1, path)              # 选
        path.pop()
    dfs(0, [])
    return ans
```

或者**枚举起点**版（更通用）：

```python
def subsets(nums):
    ans = []
    def dfs(start, path):
        ans.append(path[:])           # 每个节点都是答案
        for i in range(start, len(nums)):
            path.append(nums[i])
            dfs(i + 1, path)
            path.pop()
    dfs(0, [])
    return ans
```

### 2. 排列（顺序敏感，需 used[]）

```python
def permute(nums):
    ans = []
    used = [False] * len(nums)
    def dfs(path):
        if len(path) == len(nums):
            ans.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]: continue
            used[i] = True
            path.append(nums[i])
            dfs(path)
            path.pop()
            used[i] = False
    dfs([])
    return ans
```

### 3. 组合（固定长度，从 start 开始避免重复）

```python
def combine(n, k):
    ans = []
    def dfs(start, path):
        if len(path) == k:
            ans.append(path[:])
            return
        for i in range(start, n + 1):
            path.append(i)
            dfs(i + 1, path)          # i+1 而不是 start+1
            path.pop()
    dfs(1, [])
    return ans
```

## 去重套路（有重复元素时）

**先排序**，然后在 for 里：
```python
if i > start and nums[i] == nums[i-1]: continue   # 同一层跳过
```

**口诀**：同一**层**不能选相同的值（兄弟去重），同一**路径**可以（父子可同）。

## 怎么不写错
- **`ans.append(path[:])`** 不是 `path` —— 必须拷贝，否则后续 pop 会改答案
- **状态恢复要对称**：选什么就撤销什么（包括 used、path、visited 等）
- 剪枝有两种：**可行性剪枝**（违反约束）+ **最优性剪枝**（已比答案差）
- 排列用 `used[]`，组合 / 子集用 `start` 索引

## 热身题
- [78. 子集](https://leetcode.cn/problems/subsets/)
- [46. 全排列](https://leetcode.cn/problems/permutations/)
- [77. 组合](https://leetcode.cn/problems/combinations/)
- [17. 电话号码的字母组合](https://leetcode.cn/problems/letter-combinations-of-a-phone-number/)

## 进阶题
- [90. 子集 II](https://leetcode.cn/problems/subsets-ii/)（去重）
- [47. 全排列 II](https://leetcode.cn/problems/permutations-ii/)（去重）
- [39. 组合总和](https://leetcode.cn/problems/combination-sum/)（可重复使用）
- [51. N 皇后](https://leetcode.cn/problems/n-queens/)
- [37. 解数独](https://leetcode.cn/problems/sudoku-solver/)
- [131. 分割回文串](https://leetcode.cn/problems/palindrome-partitioning/)
- [212. 单词搜索 II](https://leetcode.cn/problems/word-search-ii/)（Trie + 回溯）
