# Web Crawler — Anthropic Q1

> Anthropic 题库第一题。**单线程 → 多线程 → 分布式**的完整演进。

## 问题（4 级递进）

- **L1**：起始 URL → BFS → 同域内抓所有 URL（**< 100 个**就算 pass）
- **L2**：处理 URL fragment（`#section` 算同一 URL）、相对路径、去重
- **L3**：改成多线程（`ThreadPoolExecutor`）
- **L4**：politeness（每 host 限速）、分布式（多机协调 visited）、内容去重

---

## 澄清问题

1. 给的 `fetch(url) -> List[str]` API 同步还是异步？
2. "同域" 指 host 完全相同？子域算不算？
3. URL fragment（`#`）和 query string（`?`）算不算同一个？
4. 有失败重试需求吗？超时多少？
5. 内存有限制吗？预期 URL 数量级？
6. 要不要 respect robots.txt？

---

## L1：单线程版

```python
from urllib.parse import urlparse, urljoin
from collections import deque
from typing import List, Set

class HTMLParser:           # 假设题目给的 API
    def getUrls(self, url: str) -> List[str]: ...

def get_host(url: str) -> str:
    return urlparse(url).netloc

def normalize(url: str) -> str:
    """去掉 fragment，统一末尾斜杠。"""
    p = urlparse(url)
    path = p.path or '/'
    return f"{p.scheme}://{p.netloc}{path}"

class Crawler:
    def __init__(self, parser: HTMLParser):
        self.parser = parser

    def crawl(self, start_url: str) -> List[str]:
        host = get_host(start_url)
        visited: Set[str] = {normalize(start_url)}
        q = deque([start_url])
        while q:
            u = q.popleft()
            for link in self.parser.getUrls(u):
                norm = normalize(link)
                if get_host(link) == host and norm not in visited:
                    visited.add(norm)
                    q.append(link)
        return list(visited)
```

### 边界
- 起始 URL 不在 visited 里 → 漏算自己
- 相对路径要用 `urljoin(base, rel)` 转绝对
- 自环（页面链到自己）→ visited 防住
- fragment 不去 → 同页多次抓

---

## L2：处理边界

```python
def normalize(url: str, base: str = None) -> str:
    if base:
        url = urljoin(base, url)
    p = urlparse(url)
    # 1. 小写 host
    netloc = p.netloc.lower()
    # 2. 默认路径
    path = p.path or '/'
    # 3. 去 fragment
    # 4. 排序 query parameter（可选）
    return f"{p.scheme}://{netloc}{path}{('?' + p.query) if p.query else ''}"
```

---

## L3：多线程版

### 难点：`visited` 的并发访问

```python
from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Condition

class MultiThreadCrawler:
    def __init__(self, parser, workers=10):
        self.parser = parser
        self.workers = workers

    def crawl(self, start_url: str) -> List[str]:
        host = get_host(start_url)
        visited = {normalize(start_url)}
        lock = Lock()

        with ThreadPoolExecutor(max_workers=self.workers) as ex:
            futures = {ex.submit(self.parser.getUrls, start_url)}
            while futures:
                done, futures = self._wait_one(futures)
                for fut in done:
                    try:
                        links = fut.result(timeout=5)
                    except Exception:
                        continue
                    for link in links:
                        norm = normalize(link)
                        if get_host(link) != host:
                            continue
                        with lock:
                            if norm in visited:
                                continue
                            visited.add(norm)
                        futures.add(ex.submit(self.parser.getUrls, link))
        return list(visited)

    @staticmethod
    def _wait_one(futures):
        from concurrent.futures import wait, FIRST_COMPLETED
        done, pending = wait(futures, return_when=FIRST_COMPLETED)
        return done, pending
```

### 生产版：Worker pool + 任务队列（推荐）

避免 "executor 内部 submit 给自己" 的死锁，改用 **N 个长期 worker + 一个共享 Queue**：

```python
import queue
from threading import Thread, Lock

class QueueCrawler:
    SENTINEL = object()
    
    def __init__(self, parser, workers=10):
        self.parser = parser
        self.workers = workers
        self.host = None
        self.visited = set()
        self.lock = Lock()
        self.q = queue.Queue()
        self.active = 0           # 还在处理的任务数
        self.active_lock = Lock()
    
    def crawl(self, start_url):
        self.host = get_host(start_url)
        self.visited.add(normalize(start_url))
        self.q.put(start_url)
        self.active = 1
        
        threads = [Thread(target=self._worker, daemon=True) for _ in range(self.workers)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        return list(self.visited)
    
    def _worker(self):
        while True:
            try:
                url = self.q.get(timeout=0.5)
            except queue.Empty:
                with self.active_lock:
                    if self.active == 0:
                        return    # 全员空闲，结束
                continue
            if url is self.SENTINEL:
                self.q.put(self.SENTINEL)    # 让其他 worker 也退出
                return
            
            try:
                links = self.parser.getUrls(url)
                for link in links:
                    norm = normalize(link)
                    if get_host(link) != self.host:
                        continue
                    with self.lock:
                        if norm in self.visited:
                            continue
                        self.visited.add(norm)
                    with self.active_lock:
                        self.active += 1
                    self.q.put(link)
            except Exception:
                pass
            finally:
                with self.active_lock:
                    self.active -= 1
```

**关键**：
- `active` 计数器跟踪 "还在飞" 的任务数，安全判断终止
- `q.get(timeout=...)` 让 worker 不会永远阻塞
- 所有共享状态都用锁保护

⚠️ **死锁陷阱**：早期版本 ` ThreadPoolExecutor.submit` 内部又向同一 executor submit，如果池满会死锁。生产代码用 worker pool + queue（上面这种）。

---

## L4：分布式 + politeness

### Politeness（限速）
```python
import time
from collections import defaultdict
from threading import Lock

class HostLimiter:
    """每 host 至少间隔 1 秒。"""
    def __init__(self, min_interval=1.0):
        self.min = min_interval
        self.last = defaultdict(float)
        self.lock = Lock()

    def wait_for(self, host):
        with self.lock:
            now = time.time()
            elapsed = now - self.last[host]
            wait_time = max(0, self.min - elapsed)
            if wait_time > 0:
                time.sleep(wait_time)
                now = time.time()
            self.last[host] = now
```

### 分布式协调
- **去重**：Redis SET 或 Bloom filter（容许少量误判）
- **任务队列**：Kafka / SQS / Redis lpush+brpop
- **状态恢复**：URL 入队前持久化，worker crash 不丢
- **内容去重**：SimHash 检测近似重复页面

### 内容去重 hint
```python
import hashlib
def content_hash(html: str) -> str:
    return hashlib.sha256(html.encode()).hexdigest()
# 用 SimHash / MinHash 检测近似重复
```

---

## 评分点

| 维度 | L1 | L2 | L3 | L4 |
|------|----|----|----|----|
| 同域过滤 | ✓ | ✓ | ✓ | ✓ |
| 去重 | ✓ | ✓ | ✓ | ✓ |
| Fragment 处理 | ✗ | ✓ | ✓ | ✓ |
| 多线程 / 锁 | ✗ | ✗ | ✓ | ✓ |
| Politeness | ✗ | ✗ | ✗ | ✓ |
| 分布式讨论 | ✗ | ✗ | ✗ | ✓ |

---

## 常见陷阱

1. **`visited.add` 在锁外** → race condition
2. **submit 死循环**：递归 submit 没有终止机制
3. **fragment 没去** → 同页面被反复抓
4. **大小写不统一** → `EXAMPLE.com` 和 `example.com` 算两个
5. **不处理超时** → 一个慢页面卡住所有 worker

## 相关题
- [1242. 多线程网页爬虫](https://leetcode.cn/problems/web-crawler-multithreaded/)
- [Concurrency Primer](../playbook/concurrency.md)
