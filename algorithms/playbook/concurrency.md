# Python 并发速通（面试用）

> **OpenAI 和 Anthropic 都问** —— web crawler、KV store、rate limiter 的 follow-up 几乎一定问"怎么改成多线程"。

---

## 三个工具一句话区分

| 工具 | 适用场景 | 真并行？ |
|------|---------|---------|
| `threading` / `ThreadPoolExecutor` | **I/O 密集**：网络、磁盘、子进程 | ❌ GIL 限制 |
| `multiprocessing` / `ProcessPoolExecutor` | **CPU 密集**：计算、解析、加密 | ✅ 多核 |
| `asyncio` | **大量轻量 I/O**：HTTP、长连接 | ❌ 单线程协程 |

**面试金句**：
> "Python 有 GIL，所以多线程在 CPU 密集任务上不会变快。但 I/O 操作会**释放 GIL**，所以 web crawler、文件读取这种用 ThreadPool 是 OK 的。"

---

## 最小可跑模板

### 1. ThreadPoolExecutor（最常用）

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch(url):
    return requests.get(url).text

urls = [...]
with ThreadPoolExecutor(max_workers=10) as ex:
    futures = {ex.submit(fetch, u): u for u in urls}
    for fut in as_completed(futures):
        u = futures[fut]
        try:
            data = fut.result()
        except Exception as e:
            print(f"{u} failed: {e}")
```

**关键**：
- `as_completed` 一完成一个就 yield —— 不用等最慢的
- 用字典存 future→input 方便错误归因
- `try/except fut.result()` 捕获 worker 异常

### 2. asyncio + aiohttp

```python
import asyncio, aiohttp

async def fetch(session, url):
    async with session.get(url) as resp:
        return await resp.text()

async def main(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, u) for u in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)

results = asyncio.run(main(urls))
```

适用：**几万个并发连接**（线程开不出这么多）。

### 3. ProcessPoolExecutor

```python
from concurrent.futures import ProcessPoolExecutor

def cpu_heavy(x):
    return sum(i*i for i in range(x))

with ProcessPoolExecutor() as ex:
    results = list(ex.map(cpu_heavy, [10**6]*8))
```

**坑**：传给子进程的函数必须**可 pickle**（不能是 lambda、不能是嵌套函数）。

---

## 锁与原语

### threading.Lock

```python
from threading import Lock

class Counter:
    def __init__(self):
        self.n = 0
        self.lock = Lock()
    def inc(self):
        with self.lock:        # 永远用 with
            self.n += 1
```

**用 with，不要手动 acquire/release** —— 异常会忘 release 死锁。

### 别的常用原语

| 原语 | 用途 |
|------|------|
| `Lock` | 互斥 |
| `RLock` | 可重入锁（同一线程多次 acquire 不阻塞） |
| `Semaphore` | 限制并发数（rate limit） |
| `Event` | 一次性信号 |
| `Condition` | 条件等待（生产者消费者） |
| `Barrier` | 多线程 rendezvous |
| `queue.Queue` | 线程安全队列，**比手写锁好用** |

**Anthropic 分布式 mode 题用 send/recv/barrier** —— 知道这些 primitive 怎么用。

---

## 经典面试场景

### 1. Web Crawler 加多线程

```python
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from collections import deque

class Crawler:
    def __init__(self, max_workers=10):
        self.visited = set()
        self.lock = Lock()
        self.ex = ThreadPoolExecutor(max_workers=max_workers)

    def crawl(self, seed):
        self._submit(seed)
        self.ex.shutdown(wait=True)

    def _submit(self, url):
        with self.lock:
            if url in self.visited: return
            self.visited.add(url)
        self.ex.submit(self._fetch_and_recurse, url)

    def _fetch_and_recurse(self, url):
        try:
            links = fetch_links(url)
            for link in links:
                if same_domain(link):
                    self._submit(link)
        except Exception as e:
            log(e)
```

⚠️ **死锁陷阱**：在 ThreadPoolExecutor 内部 submit 给同一个 executor，如果池满会卡死。生产代码用专门的 worker queue。

### 2. 线程安全 LRU Cache

```python
from collections import OrderedDict
from threading import RLock

class ThreadSafeLRU:
    def __init__(self, capacity):
        self.cap = capacity
        self.d = OrderedDict()
        self.lock = RLock()

    def get(self, key):
        with self.lock:
            if key not in self.d: return -1
            self.d.move_to_end(key)
            return self.d[key]

    def put(self, key, val):
        with self.lock:
            if key in self.d:
                self.d.move_to_end(key)
            self.d[key] = val
            if len(self.d) > self.cap:
                self.d.popitem(last=False)
```

**用 RLock 比 Lock 安全**：get 调 put 之类的嵌套不会死锁。

### 3. Rate Limiter（令牌桶）

```python
import time
from threading import Lock

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate           # tokens per second
        self.cap = capacity
        self.tokens = capacity
        self.last = time.monotonic()
        self.lock = Lock()

    def allow(self):
        with self.lock:
            now = time.monotonic()
            self.tokens = min(self.cap, self.tokens + (now - self.last) * self.rate)
            self.last = now
            if self.tokens >= 1:
                self.tokens -= 1
                return True
            return False
```

---

## 6 个高频面试问答

**Q1：为什么 Python 多线程不能加速 CPU？**
> 因为 CPython 的 GIL（Global Interpreter Lock）保证同一时刻只有一个线程执行 Python 字节码。

**Q2：GIL 什么时候释放？**
> I/O 阻塞、C 扩展（numpy）执行、`time.sleep()`、字节码执行约 100 次。

**Q3：threading 和 asyncio 哪个更轻？**
> asyncio。一个线程 ~1MB 栈，协程 ~KB。**10000+ 并发**用 asyncio。

**Q4：进程间怎么通信？**
> `multiprocessing.Queue`、`Pipe`、`shared_memory`、外部消息队列（Redis、Kafka）。

**Q5：什么是死锁？怎么避免？**
> 两线程互相等对方持有的锁。避免：**固定加锁顺序**；用 `timeout`；用 RLock；尽量短临界区。

**Q6：什么时候用 Thread 什么时候用 Process？**
> I/O 多 → Thread；CPU 多 → Process；超高并发 → asyncio；混合 → Process 内套 asyncio。

---

## 不要在面试现场做的

❌ 手写 Mutex / Semaphore（用标准库）
❌ 写 race condition 然后用 sleep "调试"
❌ 在 with 块外做锁相关操作
❌ 把 lock 当作普通变量传来传去 → 易丢
❌ 多线程里 print 调试（输出会交错乱掉，用 `logging`）
