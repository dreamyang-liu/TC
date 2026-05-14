# Spreadsheet Formula Evaluation — OpenAI

> 表格单元格可以引用其他单元格。**核心：拓扑排序 + 循环检测 + 增量更新**。

---

## 问题

```python
class Spreadsheet:
    def set(self, cell: str, formula: str) -> None:
        """formula 可以是数字（"42"）或公式（"=A1+B2*3"）。"""
    
    def get(self, cell: str) -> float:
        """返回该 cell 计算后的值。"""
```

公式支持：`+ - * /` 和单元格引用（如 `A1`、`B10`）。

---

## L1：基础表达式求值（无引用）

先实现简单的 `eval`：把 token 流转成 AST 或直接用 shunting-yard。

```python
import re

def tokenize(expr):
    return re.findall(r'[A-Z]+\d+|\d+\.?\d*|[\+\-\*/\(\)]', expr)

def to_rpn(tokens):
    """中缀转后缀（Shunting-yard）。"""
    out, ops = [], []
    prec = {'+': 1, '-': 1, '*': 2, '/': 2}
    for t in tokens:
        if t in prec:
            while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                out.append(ops.pop())
            ops.append(t)
        elif t == '(':
            ops.append(t)
        elif t == ')':
            while ops and ops[-1] != '(':
                out.append(ops.pop())
            ops.pop()
        else:
            out.append(t)
    while ops:
        out.append(ops.pop())
    return out

def eval_rpn(rpn, lookup):
    """lookup(cell_name) -> float, used for cell references."""
    stack = []
    for t in rpn:
        if t in '+-*/':
            b = stack.pop()
            a = stack.pop()
            stack.append({'+': a+b, '-': a-b, '*': a*b, '/': a/b}[t])
        elif re.match(r'[A-Z]+\d+', t):
            stack.append(lookup(t))
        else:
            stack.append(float(t))
    return stack[0]
```

---

## L2：处理引用 + 循环检测

```python
class Spreadsheet:
    def __init__(self):
        self.formulas = {}     # cell → formula string
        self.values = {}       # cell → cached value
        self.deps = {}         # cell → set of cells it depends on
        self.reverse_deps = {} # cell → set of cells that depend on it
    
    def set(self, cell: str, formula: str) -> None:
        # 解析依赖
        if formula.startswith('='):
            tokens = tokenize(formula[1:])
            new_deps = {t for t in tokens if re.match(r'[A-Z]+\d+', t)}
        else:
            new_deps = set()
        
        # 检查循环依赖（DFS）
        if self._creates_cycle(cell, new_deps):
            raise ValueError(f"setting {cell} = {formula} creates a cycle")
        
        # 更新反向依赖
        for old_dep in self.deps.get(cell, set()):
            self.reverse_deps.setdefault(old_dep, set()).discard(cell)
        for new_dep in new_deps:
            self.reverse_deps.setdefault(new_dep, set()).add(cell)
        
        self.formulas[cell] = formula
        self.deps[cell] = new_deps
        
        # 递归 invalidate 所有依赖此 cell 的
        self._invalidate(cell)
    
    def _creates_cycle(self, cell, new_deps):
        """从 new_deps 出发能不能到 cell？"""
        visited = set()
        stack = list(new_deps)
        while stack:
            c = stack.pop()
            if c == cell:
                return True
            if c in visited:
                continue
            visited.add(c)
            stack.extend(self.deps.get(c, set()))
        return False
    
    def _invalidate(self, cell):
        """清空 cell 和所有传递依赖于它的 cell 的缓存。"""
        stack = [cell]
        while stack:
            c = stack.pop()
            if c not in self.values:
                continue
            del self.values[c]
            stack.extend(self.reverse_deps.get(c, set()))
    
    def get(self, cell: str) -> float:
        if cell in self.values:
            return self.values[cell]
        if cell not in self.formulas:
            return 0.0   # 默认值
        formula = self.formulas[cell]
        if formula.startswith('='):
            tokens = tokenize(formula[1:])
            rpn = to_rpn(tokens)
            value = eval_rpn(rpn, self.get)
        else:
            value = float(formula)
        self.values[cell] = value
        return value
```

---

## 复杂度

- `set`：O(D) 找循环 + O(R) invalidate，D 是依赖图大小，R 是反向依赖数
- `get`：O(子树大小)，缓存后 O(1)
- 整张表 recalc：O(V + E) 用拓扑排序

---

## L3：增量重新计算

当 cell 改变时，只重算受影响的子图（用拓扑序）：

```python
def _recalc_dependents(self, changed_cell):
    """重新计算所有依赖 changed_cell 的 cell，按拓扑序。"""
    # BFS 收集所有受影响 cell
    affected = set()
    stack = [changed_cell]
    while stack:
        c = stack.pop()
        if c in affected:
            continue
        affected.add(c)
        stack.extend(self.reverse_deps.get(c, set()))
    
    # 在 affected 子集上做拓扑排序
    indeg = {c: 0 for c in affected}
    for c in affected:
        for d in self.deps.get(c, set()):
            if d in affected:
                indeg[c] += 1
    
    from collections import deque
    q = deque([c for c, d in indeg.items() if d == 0])
    while q:
        c = q.popleft()
        # 用 get 算（先 clear cache）
        self.values.pop(c, None)
        self.get(c)
        for dependent in self.reverse_deps.get(c, set()):
            if dependent in indeg:
                indeg[dependent] -= 1
                if indeg[dependent] == 0:
                    q.append(dependent)
```

---

## L4：扩展讨论

| Q | A |
|---|---|
| 函数支持？（SUM、AVG、IF） | 解析时识别函数名，递归 eval |
| 范围引用 `A1:A10`？ | 解析时展开成单个 cell list |
| 错误传播（`#DIV/0!`）？ | 用特殊 sentinel value 在公式间传递 |
| 并发编辑？ | 每个 cell 一把锁；或乐观锁 |
| 持久化？ | 存 formula 字典即可，启动时 lazy 计算 |
| 撤销 / 重做？ | command pattern + 历史栈 |

---

## 测试

```python
def test():
    s = Spreadsheet()
    s.set("A1", "5")
    s.set("B1", "10")
    s.set("C1", "=A1+B1")
    assert s.get("C1") == 15

    s.set("A1", "20")   # 触发 C1 invalidate
    assert s.get("C1") == 30

    # 循环检测
    s.set("D1", "=E1")
    try:
        s.set("E1", "=D1")    # 应该抛
        assert False
    except ValueError:
        pass

    # 嵌套
    s.set("D1", "=A1+B1")
    s.set("E1", "=D1*2")
    assert s.get("E1") == 60

    print("All passed")

test()
```

---

## 边界与陷阱

1. **除以 0** → 返回 `inf` 还是抛？(用 sentinel)
2. **未定义 cell** → 默认 0 还是抛？
3. **公式语法错误** → 抛带详细信息的异常
4. **大表 (10⁴ cells)** → 不能每次 set 全表重算 → 必须有反向依赖图
5. **自引用** → `A1 = A1` 是循环，直接拒
6. **interleave set / get 多线程** → 用 RLock

## 复杂度
- set: O(parse + cycle check + invalidate)
- get: O(子树未缓存部分)
- recalc: O(V + E) 子图

## 相关
- 拓扑排序：[topological-sort.md](../patterns/topological-sort.md)
- Make / Bazel build system 都基于 DAG 增量更新
- Excel / Google Sheets 内部
