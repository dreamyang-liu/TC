# KV Store Serialize/Deserialize — OpenAI 经典

> **核心 trick：length-prefix encoding**。Redis 协议、Protobuf、Thrift 都用这思想。

---

## 问题

实现 `serialize(d: Dict[str, str]) -> str` 和 `deserialize(s: str) -> Dict[str, str]`。

**坑**：key 和 value 都**可以包含任意字符**，包括 `:`、`,`、`\n`、`{` 等常用分隔符。

---

## 为什么不能用简单分隔符

```python
# 错误尝试 1
"{key}:{value},{key2}:{value2}"
# 问题：value 里有 ',' 怎么办？
```

```python
# 错误尝试 2：escape
"a\\,b:c"   # 表示 key="a,b", value="c"
# 问题：要写一堆 escape 逻辑，容易漏一个；嵌套时炸
```

```python
# 错误尝试 3：JSON
json.dumps(d)
# 问题：面试官就是要你不用 json，证明你懂底层
```

---

## 正确方案：Length-Prefix Encoding

**结构**：`<len>:<string>` 重复

```
{"hello": "world", "foo": "bar"}
→ "5:hello5:world3:foo3:bar"
```

每段都先告诉解析器"接下来读多少字节"。**完全不需要 escape**。

---

## 完整实现

```python
class KVSerializer:
    @staticmethod
    def serialize(d: dict) -> str:
        parts = []
        for k, v in d.items():
            k, v = str(k), str(v)
            parts.append(f"{len(k)}:{k}{len(v)}:{v}")
        return ''.join(parts)
    
    @staticmethod
    def deserialize(s: str) -> dict:
        result = {}
        i = 0
        while i < len(s):
            # 读 key 长度
            j = s.index(':', i)
            klen = int(s[i:j])
            i = j + 1
            key = s[i:i + klen]
            i += klen
            # 读 value 长度
            j = s.index(':', i)
            vlen = int(s[i:j])
            i = j + 1
            value = s[i:i + vlen]
            i += vlen
            result[key] = value
        return result
```

---

## 测试 + 边界

```python
def test():
    # 1. 普通
    d = {"a": "b", "c": "d"}
    s = KVSerializer.serialize(d)
    assert KVSerializer.deserialize(s) == d

    # 2. value 含 ':' 和 ','
    d = {"key:1": "val,ue:2"}
    s = KVSerializer.serialize(d)
    assert KVSerializer.deserialize(s) == d, f"got {KVSerializer.deserialize(s)}"

    # 3. 空 dict
    assert KVSerializer.serialize({}) == ""
    assert KVSerializer.deserialize("") == {}

    # 4. 空 string
    d = {"": "val", "key": ""}
    s = KVSerializer.serialize(d)
    assert KVSerializer.deserialize(s) == d

    # 5. unicode
    d = {"键": "值"}
    s = KVSerializer.serialize(d)
    assert KVSerializer.deserialize(s) == d

    # 6. 数字字符串
    d = {"3": "abc"}
    s = KVSerializer.serialize(d)
    assert KVSerializer.deserialize(s) == d

    print("All passed")

test()
```

---

## Unicode 陷阱（面试官会问）

```python
s = "你好"
len(s)         # 2 (char count)
len(s.encode('utf-8'))  # 6 (byte count)
```

`len()` 在 Python 是 char 数。如果题目要求**按 byte 序列化**（更通用）：

```python
class ByteKVSerializer:
    @staticmethod
    def serialize(d: dict) -> bytes:
        parts = []
        for k, v in d.items():
            kb, vb = str(k).encode(), str(v).encode()
            parts.append(f"{len(kb)}:".encode() + kb + f"{len(vb)}:".encode() + vb)
        return b''.join(parts)
    
    @staticmethod
    def deserialize(b: bytes) -> dict:
        result = {}
        i = 0
        while i < len(b):
            j = b.index(b':', i)
            klen = int(b[i:j])
            i = j + 1
            key = b[i:i+klen].decode()
            i += klen
            j = b.index(b':', i)
            vlen = int(b[i:j])
            i = j + 1
            value = b[i:i+vlen].decode()
            i += vlen
            result[key] = value
        return result
```

---

## Follow-up 1：流式 / 增量 deserialize

输入是一个**很长的流**（10 GB），不能一次性 load。

```python
class StreamDeserializer:
    def __init__(self, stream):
        self.stream = stream    # 提供 .read(n) 方法的对象
    
    def read_until(self, delim: bytes) -> bytes:
        buf = b''
        while True:
            c = self.stream.read(1)
            if not c or c == delim:
                return buf
            buf += c
    
    def __iter__(self):
        while True:
            try:
                klen_bytes = self.read_until(b':')
                if not klen_bytes:
                    return
                klen = int(klen_bytes)
                key = self.stream.read(klen)
                vlen = int(self.read_until(b':'))
                value = self.stream.read(vlen)
                yield key.decode(), value.decode()
            except (ValueError, EOFError):
                return
```

---

## Follow-up 2：嵌套结构（dict 套 dict）

让每个 value 也用 length-prefix 编码后塞进 string：

```python
def serialize_nested(obj):
    if isinstance(obj, str):
        b = obj.encode()
        return f"s{len(b)}:".encode() + b
    if isinstance(obj, int):
        s = str(obj).encode()
        return f"i{len(s)}:".encode() + s
    if isinstance(obj, list):
        parts = [serialize_nested(x) for x in obj]
        body = b''.join(parts)
        return f"l{len(body)}:".encode() + body
    if isinstance(obj, dict):
        parts = []
        for k, v in obj.items():
            parts.append(serialize_nested(k))
            parts.append(serialize_nested(v))
        body = b''.join(parts)
        return f"d{len(body)}:".encode() + body
```

类型标签（s/i/l/d）+ 长度前缀 = 完全自描述的二进制格式。**类似 BitTorrent bencode**。

---

## Follow-up 3：版本演化

`v1:` 前缀让 deserialize 知道用哪个版本的格式：

```python
def serialize_v2(d):
    return b"v2:" + serialize_nested(d)

def deserialize_versioned(b):
    if b.startswith(b"v2:"):
        return deserialize_v2(b[3:])
    elif b.startswith(b"v1:"):
        return deserialize_v1(b[3:])
    else:
        # legacy 默认 v1
        return deserialize_v1(b)
```

---

## 边界 / 陷阱

1. **空 key 或空 value** → `0:`，要 handle
2. **`:` 在 key 里** → length-prefix 自动 handle，不要 escape
3. **多字节字符**：`len()` vs `len(.encode())`，面试**问一下**
4. **CRLF**：网络协议里常加 `\r\n` 作为可选分隔，让人类可读
5. **整数前缀本身是字符串** → 用 `int()` parse

## 复杂度

- serialize: O(n) where n = 总字符数
- deserialize: O(n)

## 相关
- Redis RESP 协议
- BitTorrent bencode (类似但用 'e' 结尾而非长度前缀)
- Protobuf / Thrift（生产用 varint + tag）
