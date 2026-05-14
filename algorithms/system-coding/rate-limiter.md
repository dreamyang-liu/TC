# Rate Limiter

> 系统设计 + 代码题双面神器。**Token bucket + sliding window** 两个必背。

---

## 问题

```python
class RateLimiter:
    def allow(self, user_id: str) -> bool:
        """返回 True 表示该请求可以处理；False 表示触发限流。"""
```

要求：**每用户每秒最多 N 个请求**。

---

## 三种主流算法

| 算法 | 优点 | 缺点 | 场景 |
|------|------|------|------|
| **Token bucket** | 允许 burst；O(1) | 边界稍模糊 | 通用 API gateway |
| **Sliding window log** | 100% 精确 | 内存 O(N) per user | 严格审计 |
| **Sliding window counter** | 平滑 + 内存小 | 微小误差 | 大规模生产 |
| Leaky bucket | 强制平滑速率 | 不允许 burst | 队列削峰 |

---

## 实现 1：Token Bucket（最常考）

**模型**：每个用户有一个桶，桶以 `rate` tokens/sec 速率匀速注入 tokens，**最多装 capacity 个**。请求消耗 1 token，没 token 就拒绝。

```python
import time
from threading import Lock
from collections import defaultdict
from dataclasses import dataclass

@dataclass
class Bucket:
    tokens: float
    last_refill: float

class TokenBucketLimiter:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate           # tokens per second
        self.cap = capacity
        self.buckets: dict = {}
        self.lock = Lock()
    
    def allow(self, user_id: str) -> bool:
        now = time.monotonic()
        with self.lock:
            b = self.buckets.get(user_id)
            if b is None:
                b = Bucket(tokens=self.cap, last_refill=now)
                self.buckets[user_id] = b
            # 按时间补 tokens
            elapsed = now - b.last_refill
            b.tokens = min(self.cap, b.tokens + elapsed * self.rate)
            b.last_refill = now
            
            if b.tokens >= 1:
                b.tokens -= 1
                return True
            return False
```

**为什么不真的每秒注入**？— **lazy 计算**：要用时再补。省 CPU 和定时器。

### 边界
- 第一次访问：桶满
- `monotonic` 而非 `time.time()`：防系统时间跳变
- 桶不为整数：用 float
- 多线程：lock per limiter，**或** lock per user 桶

---

## 实现 2：Sliding Window Log

```python
from collections import defaultdict, deque
import time

class SlidingWindowLog:
    def __init__(self, max_requests: int, window_sec: float):
        self.max = max_requests
        self.window = window_sec
        self.log: dict = defaultdict(deque)
        self.lock = Lock()
    
    def allow(self, user_id: str) -> bool:
        now = time.monotonic()
        with self.lock:
            q = self.log[user_id]
            # 清掉窗口外的
            while q and q[0] <= now - self.window:
                q.popleft()
            if len(q) < self.max:
                q.append(now)
                return True
            return False
```

**100% 精确**：完美知道任意 1 秒窗口内的请求数。
**缺点**：每个 user 的 deque 长度最多 `max_requests`，N 个 user → O(N · max) 内存。

---

## 实现 3：Sliding Window Counter（生产首选）

把当前窗口和上一个窗口的计数加权混合，**O(1) 内存 per user**。

```python
class SlidingWindowCounter:
    def __init__(self, max_requests: int, window_sec: float):
        self.max = max_requests
        self.window = window_sec
        self.buckets: dict = defaultdict(lambda: {'cur': 0, 'prev': 0, 'start': 0.0})
        self.lock = Lock()
    
    def allow(self, user_id: str) -> bool:
        now = time.monotonic()
        with self.lock:
            b = self.buckets[user_id]
            if now - b['start'] >= self.window:
                # 滚动窗口
                if now - b['start'] < 2 * self.window:
                    b['prev'] = b['cur']
                else:
                    b['prev'] = 0
                b['cur'] = 0
                b['start'] = (now // self.window) * self.window
            
            # 上窗口的"剩余权重"
            elapsed_in_window = now - b['start']
            overlap_ratio = 1 - (elapsed_in_window / self.window)
            estimated = b['prev'] * overlap_ratio + b['cur']
            
            if estimated < self.max:
                b['cur'] += 1
                return True
            return False
```

**误差**：< 1%，但内存 O(1)，速度快。

---

## 怎么不写错

1. **monotonic 而非 wall clock**：系统时间可能被 NTP 调
2. **lazy refill**：不要 spawn 后台 thread 每秒 refill 所有 bucket
3. **lock 粒度**：global lock 大用户场景会瓶颈 → lock per user bucket
4. **首次访问初始化**：要么桶满（推荐），要么桶空看 UX
5. **GC 不活跃 user**：长期不访问的 user 占内存 → 用 LRU 或定期清

---

## 多桶 / 多策略组合

真实场景常常要"每秒 10 个 + 每分钟 100 个 + 每天 1000 个"：

```python
class CompositeLimiter:
    def __init__(self, configs):
        # configs = [(rate=10, cap=10), (rate=100/60, cap=100), ...]
        self.limiters = [TokenBucketLimiter(r, c) for r, c in configs]
    
    def allow(self, user_id):
        # 所有 limiter 都要通过
        return all(l.allow(user_id) for l in self.limiters)
```

⚠️ 这里有个 bug：**如果某个 limiter pass 但另一个 fail，第一个已经扣 token 了**。
真正生产要"先全部检查可不可以，都可以才扣"：

```python
def allow(self, user_id):
    with all_locks_acquired:
        if all(l.can_take(user_id) for l in self.limiters):
            for l in self.limiters:
                l.take(user_id)
            return True
    return False
```

---

## 分布式 Rate Limiter

### 方案 A：Redis + Lua（原子 INCR + EXPIRE）

```lua
-- KEYS[1] = user bucket key
-- ARGV[1] = max, ARGV[2] = window
local cur = redis.call('INCR', KEYS[1])
if cur == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[2])
end
return cur > tonumber(ARGV[1]) and 0 or 1
```

### 方案 B：本地 limiter + 定期 sync 给中央

每节点保留 quota 的一小部分，定期从中央补充。

---

## 完整测试

```python
def test():
    rl = TokenBucketLimiter(rate=2, capacity=5)
    
    # 满桶，前 5 个通过
    assert all(rl.allow("u1") for _ in range(5))
    # 第 6 个失败
    assert not rl.allow("u1")
    
    # 等 1 秒，补 2 个 token
    time.sleep(1.0)
    assert rl.allow("u1")
    assert rl.allow("u1")
    assert not rl.allow("u1")
    
    # 不同 user 独立
    assert rl.allow("u2")
    
    print("All passed")

test()
```

---

## 复杂度

| 操作 | TB | SW Log | SW Counter |
|------|----|----|----|
| allow | O(1) | O(max) 摊销 O(1) | O(1) |
| 内存 per user | O(1) | O(max) | O(1) |
| 精度 | 中（允许 burst） | 完美 | ~99% |

## 相关
- [Concurrency Primer](../playbook/concurrency.md)
- "Designing Data-Intensive Applications" 第 5 章
- Stripe / Cloudflare 的 rate limiter blog post
