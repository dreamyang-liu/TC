# Tokenizer — Anthropic Q6

> 两阶段题：**先 code review 找 bug，再扩展实现**。

---

## 问题

### Part 1（code review）
给一个 greedy tokenization 函数，找出 bug。

### Part 2（实现）
扩展它，处理 vocab 缺失字符的情况。

---

## 背景

**Greedy / longest-match tokenization**：
给一个 vocab（dict: token → id），把字符串切成 token 序列。每一步选**最长能匹配**的 token。

```
vocab = {"he": 0, "hello": 1, "world": 2, "o": 3, "h": 4}
"hello world" → ["hello", " ", "world"]   # 但 " " 不在 vocab！
```

---

## L1：典型有 bug 的实现

```python
def tokenize(text, vocab):
    tokens = []
    i = 0
    while i < len(text):
        # 找最长匹配
        best = None
        for tok in vocab:
            if text.startswith(tok, i) and (best is None or len(tok) > len(best)):
                best = tok
        if best is None:
            tokens.append("UNK")
            i += 1
        else:
            tokens.append(best)
            i += len(best)
    return tokens
```

### Code review：这段代码的 bug

1. **效率**：每次都遍历整个 vocab → O(n · |vocab| · max_token_len)
2. **`text.startswith(tok, i)` 时 `tok=""` 会无限循环**（如果 vocab 里有空串）
3. **"UNK" 字符串本身在 input 里就有歧义**：和 unknown 标记冲突
4. **不区分 "UNK token" 和 "字面 UNK"**

---

## L2：用 Trie 加速 + handle "UNK" 冲突

### 高效版（Trie）

```python
from typing import List, Dict, Optional

UNK = object()      # 用对象做哨兵，避免字符串歧义

class Tokenizer:
    def __init__(self, vocab: Dict[str, int]):
        if "" in vocab:
            raise ValueError("empty token not allowed")
        self.vocab = dict(vocab)
        self.trie = {}
        self._build_trie()
        self.unk_id = max(vocab.values(), default=-1) + 1   # 自动分配 UNK id
    
    def _build_trie(self):
        for tok in self.vocab:
            node = self.trie
            for c in tok:
                node = node.setdefault(c, {})
            node['$'] = tok           # 标记单词结尾
    
    def _longest_match(self, text: str, start: int) -> Optional[str]:
        node = self.trie
        last_match = None
        i = start
        while i < len(text) and text[i] in node:
            node = node[text[i]]
            i += 1
            if '$' in node:
                last_match = node['$']    # 记住最长的成功匹配
        return last_match
    
    def tokenize(self, text: str) -> List[str]:
        out = []
        i = 0
        while i < len(text):
            match = self._longest_match(text, i)
            if match is not None:
                out.append(match)
                i += len(match)
            else:
                # 用哨兵对象表示 UNK，避免和字符串歧义
                out.append(UNK)
                i += 1
        return out
    
    def encode(self, text: str) -> List[int]:
        return [self.vocab[t] if t is not UNK else self.unk_id 
                for t in self.tokenize(text)]
```

复杂度：**O(n · max_token_len)** —— Trie 把 vocab 遍历的开销变成 O(1) 转移。

---

## L3：fallback 处理（vocab 不全）

如果 vocab 没覆盖所有字符，简单 fallback 一次只跳一个 byte。

```python
def tokenize(self, text: str) -> List:
    out = []
    i = 0
    while i < len(text):
        match = self._longest_match(text, i)
        if match is not None:
            out.append(match)
            i += len(match)
        else:
            out.append(UNK)
            i += 1          # fallback: 跳 1 字符
    return out
```

### 进阶：byte-level fallback（BPE 风格）

```python
def tokenize_bytes(self, text: str) -> List:
    """如果某些字符不在 vocab，转成 byte 序列再 tokenize。"""
    out = []
    i = 0
    while i < len(text):
        match = self._longest_match(text, i)
        if match:
            out.append(match)
            i += len(match)
        else:
            # 把当前字符按 UTF-8 字节展开
            for b in text[i].encode('utf-8'):
                out.append(f"<0x{b:02X}>")
            i += 1
    return out
```

---

## L4：扩展讨论

| 问题 | 答 |
|------|---|
| 怎么训练 vocab？ | BPE、WordPiece、Unigram LM |
| 大 vocab 内存？ | Trie 节省共享前缀；DAWG / FST 进一步压缩 |
| 多种 fallback 策略？ | UNK、byte-level、character-level |
| 怎么并行？ | 按段切（注意边界 token 不能跨段切） |
| 反向 tokenize（decode）？ | 拼接 + 处理 special token |

---

## 完整测试

```python
vocab = {"he": 0, "hello": 1, "world": 2, "o": 3, "h": 4, " ": 5}
tok = Tokenizer(vocab)
assert tok.tokenize("hello world") == ["hello", " ", "world"]

# UNK 测试
vocab2 = {"a": 0, "b": 1}
tok2 = Tokenizer(vocab2)
result = tok2.tokenize("abc")
# 期望 ["a", "b", UNK]
assert result[2] is UNK

# 递归 / 多长匹配测试
vocab3 = {"ab": 0, "abc": 1, "c": 2}
tok3 = Tokenizer(vocab3)
assert tok3.tokenize("abcabc") == ["abc", "abc"]  # 不是 ["ab","c","ab","c"]
```

---

## 边界与陷阱

1. **空字符串 token** → 无限循环，必须拒绝
2. **"UNK" 字面**和 unknown 标记冲突 → **用哨兵对象**
3. **多字节字符**：`text[i]` 在 Python 是 char，没问题；但比较 byte 时要 encode
4. **最长匹配** vs **最短匹配** 题目要看清
5. **结尾匹配失败时**回退几位（greedy 没 backtrack —— 这是 longest-match 的 limitation）

## 复杂度
- Build Trie: O(总 token 字符数)
- Tokenize: O(n · max_token_len)

## 相关题
- [208. 实现 Trie](https://leetcode.cn/problems/implement-trie-prefix-tree/)
- [212. 单词搜索 II](https://leetcode.cn/problems/word-search-ii/)
- BPE 论文 (Sennrich et al. 2016) — 实际 GPT/Claude 的 tokenizer 都基于这个
