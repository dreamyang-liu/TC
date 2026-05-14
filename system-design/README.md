# System Design

系统设计面试 + 知识体系。结构待第一篇笔记成型后再定型，预想可能的细分：

```
system-design/
├── concepts/        ← 核心概念：CAP / consistency / consensus / sharding / caching
├── primitives/      ← 常用组件：load balancer / message queue / DB / cache / CDN
├── problems/        ← 经典面试题：design Twitter / TinyURL / chat / feed / search
└── frameworks/      ← 面试套路：容量估算 / API 设计 / 数据模型 / 扩容路径
```

## 写笔记的原则

System design 没有标准答案，每道题都是「需求 → 估算 → 数据模型 → API → 架构 → 扩容」的迭代。每篇尽量包括：

1. **需求澄清的关键点**（哪些假设最影响架构）
2. **量级估算**（QPS / 存储 / 带宽）
3. **关键设计决策**（每个决策背后的权衡：一致性 vs 可用性、延迟 vs 吞吐、成本 vs 复杂度）
4. **bottleneck 在哪 + 怎么扩**（先单机 → 主从 → 分片 → 缓存 → 异步）
5. **可能的 follow-up 问题**

Concept 笔记则聚焦：「这个概念的本质问题是什么，工业界有哪些解法，各自的权衡」。

## 索引

待写。
