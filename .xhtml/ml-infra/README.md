# ML Infra

ML 基础设施相关笔记。结构待第一篇笔记成型后再定型，预想可能的细分：

```
ml-infra/
├── training/        ← 分布式训练：DDP / FSDP / DeepSpeed / Megatron / 3D 并行
├── inference/       ← 推理优化：quantization / batching / KV cache / speculative
├── serving/         ← 服务化：Triton / vLLM / TGI / Ray Serve
├── data/            ← 数据 pipeline：DataLoader / sharding / streaming
├── hardware/        ← 加速器：GPU mem model / NVLink / TPU / collective ops
├── scheduling/      ← 调度编排：Slurm / K8s / Ray
└── concepts/        ← 跨领域概念：autograd / mixed precision / compile / profiling
```

## 写笔记的原则

不同于算法刷题，ML infra 没有「pattern → problem」的清晰对偶，更像「系统组件 → 设计权衡 → 实战经验」。每篇尽量包括：

1. **这个组件 / 技术解决什么问题**（如果不存在会怎样）
2. **核心机制**（一两句话 + 一张图）
3. **关键设计权衡**（为什么不是另一种做法）
4. **常见踩坑 / 调参经验**
5. **延伸阅读**（论文 / blog / 源码链接）

## 索引

待写。
