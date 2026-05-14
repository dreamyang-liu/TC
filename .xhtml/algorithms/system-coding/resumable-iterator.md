# Resumable / Pausable Iterator — OpenAI

> 看似简单但藏了**状态机设计**和**嵌套结构**两个考点。

---

## 问题

实现一个 iterator，支持：
- `next() -> Any`
- `has_next() -> bool`
- `pause()` / `resume()`
- `skip(n)` — 跳过 n 个元素
- `reset()` — 回到起点
- **嵌套**：iterable 里包含 iterable，要展平后逐个 yield

---

## L1：基础 + flatten

```python
from typing import Any, List, Iterable

class ResumableIterator:
    def __init__(self, items: List[Any]):
        self.items = items
        self._reset_state()

    def _reset_state(self):
        self.stack = [(self.items, 0)]   # (current_list, index)
        self.paused = False
        self._peek = None

    def reset(self):
        self._reset_state()

    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def has_next(self) -> bool:
        if self.paused:
            return False
        return self._peek_next() is not None

    def next(self) -> Any:
        if self.paused:
            raise StopIteration("iterator is paused")
        val = self._peek_next()
        if val is None:
            raise StopIteration()
        self._advance()
        return val

    def skip(self, n: int):
        for _ in range(n):
            if not self.has_next():
                return
            self.next()

    def _peek_next(self):
        """Look at next leaf value without consuming it (for has_next)."""
        # walk stack to find next leaf
        while self.stack:
            cur, i = self.stack[-1]
            if i >= len(cur):
                self.stack.pop()
                continue
            item = cur[i]
            if isinstance(item, list):
                self.stack[-1] = (cur, i + 1)
                self.stack.append((item, 0))
                continue
            return item
        return None

    def _advance(self):
        """Move past the current leaf."""
        cur, i = self.stack[-1]
        self.stack[-1] = (cur, i + 1)
```

⚠️ **细节**：`_peek_next` 会**修改 stack**（跳过空 list、下钻到子 list）。这是 OK 的因为再次调用还是同样的 leaf。

---

## L2：边界 / 嵌套验证

```python
def test():
    it = ResumableIterator([1, [2, 3], [4, [5, 6]], 7])
    assert [it.next() for _ in range(7)] == [1, 2, 3, 4, 5, 6, 7]
    assert not it.has_next()

    # reset
    it.reset()
    assert it.next() == 1

    # pause/resume
    it.pause()
    assert not it.has_next()
    try:
        it.next()
        assert False, "should raise"
    except StopIteration:
        pass
    it.resume()
    assert it.next() == 2

    # skip
    it.reset()
    it.skip(3)
    assert it.next() == 4

    # 空 list
    it2 = ResumableIterator([])
    assert not it2.has_next()

    # 嵌套空 list
    it3 = ResumableIterator([[], [[]], [1]])
    assert it3.next() == 1
    assert not it3.has_next()
```

---

## L3：序列化状态（断点续传）

```python
def snapshot(self) -> dict:
    """Serialize position. Re-create with .restore() later."""
    # stack 里存的是引用，要存"路径"才能跨重启
    path = []
    cur = self.items
    for level, (lst, idx) in enumerate(self.stack):
        if level == 0:
            path.append(idx)
        else:
            # 找到 lst 在父 list 中的位置
            parent = self.stack[level - 1][0]
            parent_idx = self.stack[level - 1][1] - 1
            assert parent[parent_idx] is lst
            path.append(idx)
    return {"path": path, "paused": self.paused}

def restore(self, snapshot: dict):
    self.stack = []
    cur = self.items
    for i, idx in enumerate(snapshot["path"]):
        self.stack.append((cur, idx))
        if i < len(snapshot["path"]) - 1:
            # 下一个 path entry 指向子列表
            cur = cur[idx - 1]   # idx-1 因为 stack 里存的是"下一个要读"
    self.paused = snapshot["paused"]
```

⚠️ 这种 path 序列化只能在**原 items 不变**的前提下用。如果数据可变，需要按值（而非引用）记录位置。

---

## 关键 Python 视角：用 generator 简化

如果不需要 `reset` / `skip` / 状态快照，可以用 generator + 装饰：

```python
def flatten(items):
    for x in items:
        if isinstance(x, list):
            yield from flatten(x)
        else:
            yield x

class SimpleIter:
    def __init__(self, items):
        self.items = items
        self._gen = flatten(items)
        self._peek = self._fetch()
        self.paused = False

    def _fetch(self):
        try:
            return next(self._gen)
        except StopIteration:
            return None

    def has_next(self):
        return not self.paused and self._peek is not None

    def next(self):
        if self.paused or self._peek is None:
            raise StopIteration
        v = self._peek
        self._peek = self._fetch()
        return v
```

**但 generator 不支持 `reset`**（generator 用完就废）。所以面试题用栈模拟。

---

## 怎么不写错

1. **空 list / 嵌套空 list** → `_peek_next` 必须循环 pop 直到找到 leaf 或 stack 空
2. **`has_next` 不能消费元素** → 用 peek 模式
3. **paused 状态下 next 抛异常** → 显式定义行为
4. **`isinstance(x, list)` 判断展开** → 题目可能扩展到 dict、tuple，要明确"什么算可迭代"
5. **修改原 list 期间迭代** → 文档说不允许，或拷贝一份

---

## 复杂度

| 操作 | 复杂度 |
|------|--------|
| next | **均摊 O(1)** — 整个遍历总共 O(总 leaf 数) |
| has_next | 均摊 O(1) |
| reset | O(1) |
| skip(n) | O(n) |

## 相关
- [341. 扁平化嵌套列表迭代器](https://leetcode.cn/problems/flatten-nested-list-iterator/)
- [251. 展开二维向量](https://leetcode.cn/problems/flatten-2d-vector/)
- [284. 顶端迭代器](https://leetcode.cn/problems/peeking-iterator/)
