# In-Memory SQL Engine — OpenAI

> 60-90 分钟实现**简化的 SQL DB**。考察 **parser + executor 分层 + 数据结构选型**。

---

## 问题

实现支持以下语句的内存 DB：

```sql
CREATE TABLE users (id, name, age)
INSERT INTO users VALUES (1, "Alice", 30)
SELECT name, age FROM users WHERE age > 25
SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id
```

---

## 澄清问题

1. 字段类型要 schema 吗？还是全当 string / dynamic？
2. 支持 `UPDATE` / `DELETE` 吗？
3. WHERE 子句多复杂？（`AND/OR`、嵌套？）
4. JOIN 类型？（只 INNER 还是要 LEFT/RIGHT？）
5. NULL 怎么处理？
6. 索引？事务？

L5 面试**建议先做最小核心**，再讨论扩展。

---

## 设计：3 层架构

```
┌──────────────┐
│ Parser       │  string → AST (Statement objects)
├──────────────┤
│ Executor     │  AST → 操作 storage
├──────────────┤
│ Storage      │  in-memory tables (dict 套 list)
└──────────────┘
```

---

## L1：最小可用 (CREATE / INSERT / SELECT *)

### Storage

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Table:
    columns: List[str]
    rows: List[List[Any]] = field(default_factory=list)

class Storage:
    def __init__(self):
        self.tables: Dict[str, Table] = {}
    
    def create(self, name: str, cols: List[str]):
        if name in self.tables:
            raise ValueError(f"table {name} exists")
        self.tables[name] = Table(cols)
    
    def insert(self, name: str, values: List[Any]):
        t = self._get(name)
        if len(values) != len(t.columns):
            raise ValueError("column count mismatch")
        t.rows.append(list(values))
    
    def _get(self, name):
        if name not in self.tables:
            raise ValueError(f"no such table: {name}")
        return self.tables[name]
```

### Parser（简单 tokenize + 关键字驱动）

```python
import re

def tokenize(sql: str):
    """简单 lexer: keywords, identifiers, strings, numbers, operators."""
    pattern = r'''
        "[^"]*"          # 双引号字符串
        | '[^']*'        # 单引号字符串
        | -?\d+\.?\d*    # 数字
        | [A-Za-z_][A-Za-z0-9_.]*  # identifier
        | <=|>=|<>|!=|<|>|=
        | [(),*]
    '''
    return re.findall(pattern, sql, re.VERBOSE)

def parse(sql: str):
    tokens = tokenize(sql)
    head = tokens[0].upper()
    if head == 'CREATE':
        # CREATE TABLE name (col1, col2, ...)
        name = tokens[2]
        cols = [t for t in tokens if t not in ('CREATE', 'TABLE', name, '(', ')', ',')]
        return ('CREATE', name, cols)
    if head == 'INSERT':
        # INSERT INTO name VALUES (v1, v2, ...)
        name = tokens[2]
        vals_start = tokens.index('VALUES') + 1
        raw = tokens[vals_start:]
        values = [parse_literal(t) for t in raw if t not in ('(', ')', ',')]
        return ('INSERT', name, values)
    if head == 'SELECT':
        return parse_select(tokens)
    raise ValueError(f"unknown statement: {head}")

def parse_literal(t):
    if t.startswith('"') or t.startswith("'"):
        return t[1:-1]
    try:
        return int(t)
    except ValueError:
        try:
            return float(t)
        except ValueError:
            return t

def parse_select(tokens):
    """SELECT cols FROM table [WHERE cond] [JOIN ...]"""
    # 找关键字位置
    from_idx = tokens.index('FROM')
    where_idx = next((i for i, t in enumerate(tokens) if t.upper() == 'WHERE'), None)
    join_idx = next((i for i, t in enumerate(tokens) if t.upper() == 'JOIN'), None)
    
    cols = [t for t in tokens[1:from_idx] if t != ',']
    end = where_idx or join_idx or len(tokens)
    table = tokens[from_idx + 1]
    
    where = None
    if where_idx is not None:
        # 简化：WHERE col OP value
        where = (tokens[where_idx + 1], tokens[where_idx + 2], parse_literal(tokens[where_idx + 3]))
    
    join = None
    if join_idx is not None:
        # JOIN table ON col1 = col2
        join_table = tokens[join_idx + 1]
        on_idx = tokens.index('ON')
        join_cond = (tokens[on_idx + 1], tokens[on_idx + 3])
        join = (join_table, join_cond)
    
    return ('SELECT', cols, table, where, join)
```

### Executor

```python
class Executor:
    def __init__(self, storage: Storage):
        self.storage = storage
    
    def execute(self, sql: str):
        stmt = parse(sql)
        op = stmt[0]
        if op == 'CREATE':
            self.storage.create(stmt[1], stmt[2])
            return None
        if op == 'INSERT':
            self.storage.insert(stmt[1], stmt[2])
            return None
        if op == 'SELECT':
            return self._select(stmt)
    
    def _select(self, stmt):
        _, cols, table_name, where, join = stmt
        t = self.storage._get(table_name)
        rows = [dict(zip(t.columns, r)) for r in t.rows]
        
        # JOIN
        if join:
            join_table, (l_col, r_col) = join
            jt = self.storage._get(join_table)
            joined = []
            for r in rows:
                for jr_vals in jt.rows:
                    jr = dict(zip(jt.columns, jr_vals))
                    # 简化：列名形如 table.col
                    lt_col = l_col.split('.')[-1]
                    rt_col = r_col.split('.')[-1]
                    if r.get(lt_col) == jr.get(rt_col):
                        merged = {**{f"{table_name}.{k}": v for k, v in r.items()},
                                  **{f"{join_table}.{k}": v for k, v in jr.items()}}
                        joined.append(merged)
            rows = joined
        
        # WHERE
        if where:
            col, op, val = where
            cmp = {
                '=': lambda a, b: a == b,
                '<': lambda a, b: a < b,
                '>': lambda a, b: a > b,
                '<=': lambda a, b: a <= b,
                '>=': lambda a, b: a >= b,
                '!=': lambda a, b: a != b,
                '<>': lambda a, b: a != b,
            }[op]
            rows = [r for r in rows if cmp(r.get(col.split('.')[-1], r.get(col)), val)]
        
        # 投影
        if cols == ['*']:
            return rows
        out = []
        for r in rows:
            out.append({c: r.get(c.split('.')[-1], r.get(c)) for c in cols})
        return out
```

### 用起来

```python
db = Executor(Storage())
db.execute("CREATE TABLE users (id, name, age)")
db.execute('INSERT INTO users VALUES (1, "Alice", 30)')
db.execute('INSERT INTO users VALUES (2, "Bob", 22)')
result = db.execute("SELECT name FROM users WHERE age > 25")
print(result)  # [{'name': 'Alice'}]
```

---

## L2：扩展 (UPDATE / DELETE / 多条件 WHERE)

### UPDATE

```python
def _update(self, table, sets, where):
    t = self.storage._get(table)
    for i, row in enumerate(t.rows):
        d = dict(zip(t.columns, row))
        if where is None or self._match(d, where):
            for col, val in sets:
                d[col] = val
            t.rows[i] = [d[c] for c in t.columns]
```

### 多条件 WHERE（递归表达式树）

把 WHERE 子句解析成 AST：
```
WHERE age > 25 AND name = "Alice"
  →  And(Cmp(age, >, 25), Cmp(name, =, "Alice"))
```

```python
def eval_where(node, row):
    if isinstance(node, And):
        return eval_where(node.left, row) and eval_where(node.right, row)
    if isinstance(node, Or):
        return eval_where(node.left, row) or eval_where(node.right, row)
    if isinstance(node, Cmp):
        return CMP_OPS[node.op](row.get(node.col), node.val)
```

---

## L3：索引 + 性能

### B-tree 索引（或就用 SortedList）

```python
from sortedcontainers import SortedList

class Index:
    def __init__(self):
        self.entries = SortedList()    # (value, row_id)
    
    def insert(self, val, row_id):
        self.entries.add((val, row_id))
    
    def range_query(self, lo, hi):
        return [rid for v, rid in self.entries.irange((lo,), (hi,))]
```

WHERE 命中索引时直接 range query，避免 full scan。

### Hash 索引（仅 equality）
```python
self.hash_index = defaultdict(list)   # value → [row_id, ...]
```

---

## L4：扩展讨论

| Q | A |
|---|---|
| ACID 事务？ | WAL + undo log + 隔离级别 |
| 持久化？ | 同上，加 snapshot |
| 并发？ | 锁粒度（表锁 / 行锁 / MVCC） |
| 优化器？ | 基于 cost model 选 join order |
| 大表 join？ | hash join、merge join（看是否有序） |

---

## 边界 / 陷阱

1. **CREATE 同名 table 两次** → 抛
2. **INSERT 列数不匹配** → 抛
3. **WHERE 引用不存在的列** → 视为 None，永远 False（或抛？）
4. **NULL handling**：等于、不等于、和 NULL 比较都是 unknown
5. **大小写敏感**：SQL 关键字通常不敏感，identifier 敏感
6. **string 内容有 quote**：要 escape，或用双 quote

## 复杂度
- INSERT: O(1)
- SELECT (no index): O(N)
- SELECT (indexed equality): O(log N + K)
- JOIN (nested loop): O(N · M)，hash join O(N + M)

## 相关
- SQLite 源码（极佳学习材料）
- LeetCode 数据库题（用 SQL 解决）
