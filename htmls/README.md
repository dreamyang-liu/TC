# TC — 跳槽备战笔记

按**领域**组织。每个领域底下再按自己的逻辑细分（pattern / 题目 / 概念）。

```
TC/
├── algorithms/        ← LeetCode 算法 & 数据结构
├── ml-infra/          ← ML 基础设施（训练/推理/分布式/serving）
└── system-design/     ← 系统设计
```

## 写笔记的通用原则

1. **First principles 优先**：解释「为什么这个套路 / 设计有效」，而不是「步骤几步」
2. **记错的思路**：写下最初的错误尝试 + 为什么错。未来自己会感谢
3. **能抽象就抽象**：一道题 → 一个 pattern；一个系统 → 一类设计权衡
4. **一句话本质**：每篇笔记顶部强迫自己写一句话能讲清的本质

## 领域索引

### Algorithms

LeetCode 刷题笔记。按 **pattern** 而不是题号组织。详见 [algorithms/README.md](algorithms/README.md)。

- [差分数组 / 前缀和](algorithms/patterns/difference-array.md)
  - [1674. Min Moves to Make Array Complementary](algorithms/problems/1674-min-moves-complementary.md)

### ML Infra

待写。预想覆盖：分布式训练（DDP / FSDP / DeepSpeed）、推理优化（quant / batching / KV cache）、serving 系统（Triton / vLLM / Ray Serve）、数据 pipeline、加速器（GPU / TPU）特性、调度（Slurm / K8s）。详见 [ml-infra/README.md](ml-infra/README.md)。

### System Design

待写。预想覆盖：经典题（Twitter / TinyURL / chat / feed / search）、概念（CAP / consistency / sharding / consensus / caching）、面试套路（容量估算 / API 设计 / 数据模型 / 扩容）。详见 [system-design/README.md](system-design/README.md)。
