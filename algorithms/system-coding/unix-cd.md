# Unix `cd` with Symlinks — OpenAI

> 看似简单的路径解析，但 **symlink + 环检测**是真考点。

---

## 问题

实现一个简化版 `cd` 命令：

```python
class FileSystem:
    def __init__(self):
        self.cwd = "/"
        self.symlinks = {}    # path → target

    def cd(self, path: str) -> str:
        """返回 cd 后的 cwd。"""

    def mkdir(self, path: str) -> None: ...
    def link(self, src: str, dst: str) -> None:
        """创建 symlink: src → dst"""
```

支持：
- 绝对路径 `/foo/bar`
- 相对路径 `bar/baz`
- `.` 和 `..`
- **多级 symlink 解析**
- **环检测**（symlink 循环 → 抛异常或返回错误）

---

## 澄清问题

- 路径不存在怎么办？（创建？抛异常？）
- symlink 解析最深几层？（Linux 默认 40）
- 是否要 handle 文件 vs 目录区分？
- 环境变量 `~`、`$HOME`？

---

## L1：基础路径解析（无 symlink）

```python
def normalize(cwd: str, path: str) -> str:
    """把 path 相对 cwd 解析成绝对规范路径。"""
    if path.startswith('/'):
        parts = path.split('/')
    else:
        parts = cwd.split('/') + path.split('/')
    
    stack = []
    for part in parts:
        if part == '' or part == '.':
            continue
        elif part == '..':
            if stack:
                stack.pop()
        else:
            stack.append(part)
    return '/' + '/'.join(stack)
```

测试：
```python
assert normalize("/foo", "bar") == "/foo/bar"
assert normalize("/foo", "../bar") == "/bar"
assert normalize("/foo/bar", "./baz/../qux") == "/foo/bar/qux"
assert normalize("/", "..") == "/"           # root 的父是自己
```

---

## L2：加入 symlink 解析

**核心思路**：边走边解析，每遇到 symlink **递归展开**。

```python
class FileSystem:
    MAX_SYMLINK_DEPTH = 40

    def __init__(self):
        self.cwd = '/'
        self.dirs = set(['/'])
        self.symlinks = {}    # absolute path → absolute target
    
    def mkdir(self, path: str):
        abs_path = self._resolve(path)
        # 创建所有中间目录
        parts = abs_path.strip('/').split('/')
        cur = '/'
        for p in parts:
            cur = cur.rstrip('/') + '/' + p
            self.dirs.add(cur)
    
    def link(self, src: str, target: str):
        abs_src = self._resolve(src, follow_symlinks=False)
        # target 可以是相对的，按 src 所在目录解析
        if not target.startswith('/'):
            parent = '/'.join(abs_src.split('/')[:-1]) or '/'
            target = self._resolve(target, cwd_override=parent, follow_symlinks=False)
        self.symlinks[abs_src] = target
    
    def cd(self, path: str) -> str:
        new = self._resolve(path)
        if new not in self.dirs:
            raise FileNotFoundError(f"no such directory: {new}")
        self.cwd = new
        return self.cwd
    
    def _resolve(self, path: str, cwd_override=None, follow_symlinks=True) -> str:
        """完整解析，含 symlink。"""
        cwd = cwd_override or self.cwd
        return self._resolve_recursive(cwd, path, depth=0, follow=follow_symlinks)
    
    def _resolve_recursive(self, cwd, path, depth, follow):
        if depth > self.MAX_SYMLINK_DEPTH:
            raise OSError("too many levels of symbolic links")
        
        # 构建初始绝对路径
        if path.startswith('/'):
            parts = path.split('/')
            cur = '/'
        else:
            cur = cwd
            parts = path.split('/')
        
        stack = [p for p in cur.split('/') if p]
        
        for part in parts:
            if part == '' or part == '.':
                continue
            if part == '..':
                if stack:
                    stack.pop()
                continue
            stack.append(part)
            # 构建当前完整路径
            current = '/' + '/'.join(stack)
            # 解析 symlink
            if follow and current in self.symlinks:
                target = self.symlinks[current]
                # 把 target 解析掉，替换 stack 末尾
                resolved = self._resolve_recursive(
                    '/'.join(['/'] + stack[:-1]),
                    target, depth + 1, follow
                )
                stack = [p for p in resolved.split('/') if p]
        
        return '/' + '/'.join(stack)
```

---

## L3：环检测（真的需要）

简单的"最大深度限制"是 Linux 的方法（深度 > 40 就报错）。

**精确环检测**用 visited set：

```python
def _resolve_recursive(self, cwd, path, visited=None, follow=True):
    if visited is None:
        visited = set()
    # ...
    if follow and current in self.symlinks:
        if current in visited:
            raise OSError(f"symlink loop detected at {current}")
        visited.add(current)
        target = self.symlinks[current]
        resolved = self._resolve_recursive(
            '/'.join(['/'] + stack[:-1]), target, visited.copy(), follow
        )
```

⚠️ 注意 `visited.copy()` —— 不同 branch 不应共享 visited 状态。

---

## 完整测试

```python
def test():
    fs = FileSystem()
    fs.mkdir("/a/b/c")
    fs.mkdir("/x/y")

    assert fs.cd("/a/b/c") == "/a/b/c"
    assert fs.cd("..") == "/a/b"
    assert fs.cd("../..") == "/"
    assert fs.cd("/a/b") == "/a/b"
    assert fs.cd("./c") == "/a/b/c"

    # Symlink
    fs.link("/a/link_to_xy", "/x/y")
    assert fs.cd("/a/link_to_xy") == "/x/y"

    # Symlink chain
    fs.link("/a/link2", "/a/link_to_xy")
    assert fs.cd("/a/link2") == "/x/y"

    # Cycle
    fs.link("/loop1", "/loop2")
    fs.link("/loop2", "/loop1")
    try:
        fs.cd("/loop1")
        assert False, "should detect cycle"
    except OSError:
        pass

    # root .. is still root
    assert fs.cd("/") == "/"
    assert fs.cd("..") == "/"

    print("All passed")

test()
```

---

## L4：扩展讨论

| Q | A |
|---|---|
| 相对 symlink？ | target 相对 link 所在目录解析 |
| 跨设备 symlink？ | 实际 Linux 区分 mount point |
| 权限检查？ | 每段都要 check 权限 |
| 并发 cd 不同目录？ | cwd 是线程/进程局部状态 |
| 怎么实现 `realpath`？ | 用同样的解析逻辑，遇到非目录最后一段不解析 |

---

## 边界与陷阱

1. **`cd /` 后 `cd ..`** → 还是 `/`
2. **`/a/b/c` 但 `/a/b` 不存在** → mkdir 是否要 `-p` 行为？看题意
3. **symlink 指向不存在的 path** → mkdir 时 ok，cd 时 fail
4. **绝对 symlink 在相对路径中** → `/a/sym` 其中 sym → `/x/y`，访问 `/a/sym/z` → `/x/y/z`
5. **`..` 跨越 symlink** → 在 Linux 里 `cd a/sym/..` 不一定回到 `a`，是回到 `target` 的父
6. **trailing 斜杠**：`/a/b/` 和 `/a/b` 视为相同

## 复杂度
- 每次 cd：O(path_len × max_symlink_depth)

## 相关
- POSIX `realpath()` 函数
- Linux kernel namei.c
