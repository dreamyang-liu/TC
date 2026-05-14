# Python 数据结构复杂度速查（面试时直接背）

## 内置容器

### list（CPython 动态数组）

| 操作 | 复杂度 | 备注 |
|------|--------|------|
| `a[i]` | **O(1)** | |
| `a[-1]` | **O(1)** | |
| `a.append(x)` | **O(1)** 均摊 | 偶尔 O(n) 扩容 |
| `a.pop()` | **O(1)** | 尾部 |
| `a.pop(0)` | **O(n)** | ⚠️ 头部要移动所有 |
| `a.insert(i, x)` | **O(n)** | |
| `x in a` | **O(n)** | |
| `a.index(x)` | **O(n)** | |
| `a.sort()` | **O(n log n)** | Timsort |
| `a[i:j]` slice | **O(j-i)** | |
| `len(a)` | **O(1)** | |

**坑**：`pop(0)` 看起来无害，n 次循环里就是 O(n²)。要从头删用 `collections.deque`。

### dict

| 操作 | 平均 | 最坏 |
|------|------|------|
| `d[k]` 读 | O(1) | O(n) |
| `d[k] = v` 写 | O(1) | O(n) |
| `k in d` | O(1) | O(n) |
| `del d[k]` | O(1) | O(n) |
| 迭代 | O(n) | O(n) |

**3.7+ 保证插入顺序**。

### set

跟 dict 一样的 hash 表，所有操作 O(1) 平均。
`a | b`, `a & b`, `a - b` 都是 O(|a| + |b|)。

### tuple

不可变，可哈希（前提是元素都可哈希）。适合做 dict 的 key、堆里的复合元素。

### str

不可变。**切片 / 拼接都是 O(n)**。
循环里拼接字符串用 `''.join(parts)`，不要 `s += c`（变成 O(n²)）。

---

## collections 模块

### deque
| 操作 | 复杂度 |
|------|--------|
| `appendleft`, `popleft` | **O(1)** |
| `append`, `pop` | **O(1)** |
| 随机访问 `d[i]` | O(n) ⚠️ |

BFS、滑窗、单调队列必备。

### Counter
基本就是 dict。
- `Counter(iterable)` — O(n) 计数
- `c.most_common(k)` — O(n log k)
- `c1 - c2` — 只保留正差

### defaultdict
等同 dict，访问不存在 key 时调用工厂函数初始化。
```python
g = defaultdict(list)
g[u].append(v)        # 不用判空
```

---

## heapq（最小堆）

| 操作 | 复杂度 |
|------|--------|
| `heappush(h, x)` | **O(log n)** |
| `heappop(h)` | **O(log n)** |
| `h[0]` 偷看堆顶 | **O(1)** |
| `heapify(list)` | **O(n)** ⚡ |
| `nsmallest(k, it)` / `nlargest(k, it)` | O(n log k) |

**最大堆技巧**：存负数。

---

## 排序

`sorted(iterable, key=..., reverse=...)` — **O(n log n)**，稳定。
`list.sort()` 原地。

按多个 key 排：`key=lambda x: (x[0], -x[1])`。

---

## 字符串操作

| 操作 | 复杂度 |
|------|--------|
| `s + t` | O(\|s\|+\|t\|) |
| `s * n` | O(n·\|s\|) |
| `s[i:j]` | O(j-i) |
| `s.find(t)` | O(\|s\|·\|t\|) 最坏，平均更快 |
| `t in s` | 同上 |
| `s.split()` | O(\|s\|) |
| `''.join(list)` | O(总长度) |
| `s.replace(a, b)` | O(\|s\|) |

`f-string` 比 `%` 和 `.format()` 都快。

---

## 常见操作复杂度对照

| 想干啥 | 用啥 | 复杂度 |
|--------|------|--------|
| 查找元素 | set / dict | O(1) |
| 维护有序 + 插入 / 删除 | `SortedList`（sortedcontainers）| O(log n) |
| 最大/最小堆 | heapq | push/pop O(log n) |
| 队首队尾都要 O(1) | deque | O(1) |
| 静态有序数组二分 | bisect | O(log n) |
| LRU | OrderedDict / 双向链表+dict | O(1) |
| 区间查询 | 前缀和 / 线段树 / BIT | 前缀和 O(1) 查 |

---

## bisect 用法（手写二分前先想想）

```python
import bisect

a = [1, 3, 5, 7]
bisect.bisect_left(a, 4)    # 2 （第一个 >= 4 的位置）
bisect.bisect_right(a, 5)   # 3 （第一个 > 5 的位置）
bisect.insort(a, 4)         # a = [1, 3, 4, 5, 7]
```

**记忆**：`bisect_left` 找**左**边界（第一个 ≥）；`bisect_right` 找**右**边界（第一个 >）。

---

## 内存估算

| 类型 | 大约字节 |
|------|----------|
| int (小) | 28 |
| float | 24 |
| 空 list | 56 |
| 空 dict | 232 |
| 空 set | 216 |
| 1 字符 str | 50 |

⚠️ Python 对象有 header，**实际内存 ≈ 数学估算 × 5-10**。
10⁶ int 在 list 里大概 30MB。

---

## 复杂度感觉（面试常用）

| n | 上限算法 |
|---|----------|
| 10⁹ | O(log n), O(√n) |
| 10⁸ | O(n) |
| 10⁶ | O(n log n) |
| 10⁵ | O(n √n) |
| 10⁴ | O(n²) |
| 500 | O(n³) |
| 20 | O(2ⁿ), O(n!) |

面试里面试官说 n ≤ 10⁵ —— 默认 O(n log n) 期望解。

---

## 一句话面试金句

> "Python 的 `dict` lookup 摊销 O(1)，最坏 O(n) 当所有 key 哈希冲突；但实际不会发生除非被人为攻击。所以这里用 dict 处理 frequency count 是 O(n) 总体。"

把"摊销"、"最坏"、"期望"分开说，立刻显得 senior。
