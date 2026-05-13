# Trie / 前缀树模板（易记版）

## 本质一句话
> **每个节点代表"走到这里时的前缀"。共享前缀的字符串共享路径。**

## 最简模板（用 dict 写最快）

```python
class Trie:
    def __init__(self):
        self.root = {}

    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node:
                node[c] = {}
            node = node[c]
        node['#'] = True            # 用 '#' 标记单词结尾

    def search(self, word):
        node = self._walk(word)
        return node is not None and '#' in node

    def starts_with(self, prefix):
        return self._walk(prefix) is not None

    def _walk(self, s):
        node = self.root
        for c in s:
            if c not in node:
                return None
            node = node[c]
        return node
```

## 数组版（更快，固定字符集）

```python
class TrieNode:
    __slots__ = ('children', 'end')
    def __init__(self):
        self.children = [None] * 26   # 只支持小写字母
        self.end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for c in word:
            i = ord(c) - ord('a')
            if not node.children[i]:
                node.children[i] = TrieNode()
            node = node.children[i]
        node.end = True
```

## 怎么不写错
- **结尾标记不能省**：否则 `insert("apple")` 后 `search("app")` 会误判为真
- **`'#'` / `end` 标记和字符不冲突**：用特殊 key 或独立字段
- 通配符（`.`）匹配 → 改成 DFS 遍历所有 children
- 字符集大用 dict，字符集固定且小用数组（更快、更省内存）

## 经典套路

### 1. 单词搜索 II（Trie + 回溯）
建 Trie 装所有 word，从网格每个格子 DFS，沿 Trie 同步走 —— Trie 走不动就直接剪枝。

### 2. 最大异或对（01 Trie，按位拆）
把每个数当作 32 位二进制字符串插入。查询时**每一位都尽量选相反**的方向，结果就是异或最大。

```python
def find_max_xor(nums):
    root = {}
    # 先把所有数插入
    for x in nums:
        node = root
        for i in range(31, -1, -1):
            b = (x >> i) & 1
            if b not in node: node[b] = {}
            node = node[b]
    # 再查询每个数的最大异或
    ans = 0
    for x in nums:
        node = root
        cur = 0
        for i in range(31, -1, -1):
            b = (x >> i) & 1
            want = 1 - b
            if want in node:
                cur |= (1 << i)
                node = node[want]
            else:
                node = node[b]
        ans = max(ans, cur)
    return ans
```

## 热身题
- [208. 实现 Trie（前缀树）](https://leetcode.cn/problems/implement-trie-prefix-tree/)
- [1268. 搜索推荐系统](https://leetcode.cn/problems/search-suggestions-system/)
- [648. 单词替换](https://leetcode.cn/problems/replace-words/)

## 进阶题
- [212. 单词搜索 II](https://leetcode.cn/problems/word-search-ii/)（Trie + 回溯）
- [421. 数组中两个数的最大异或值](https://leetcode.cn/problems/maximum-xor-of-two-numbers-in-an-array/)（01 Trie）
- [336. 回文对](https://leetcode.cn/problems/palindrome-pairs/)
- [677. 键值映射](https://leetcode.cn/problems/map-sum-pairs/)
- [745. 前缀和后缀搜索](https://leetcode.cn/problems/prefix-and-suffix-search/)
