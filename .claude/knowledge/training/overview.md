# Digital Twin Trainer — Pipeline Overview

> 数字分身训练管线：MergeKit 模型融合 → 个性数据提取 → QLoRA 注入 → 双池 DPO 训练循环
> 硬件: RTX 3060 Laptop 6GB VRAM | 策略: 1.5B 基座 + QLoRA 4-bit

## 仓库位置

- **主仓库**: `C:\Users\86131\Desktop\digital-twin-trainer` (GitHub: `YuhaoLin2005/digital-twin-trainer`)

## 四阶段管线

| 阶段 | 方法 | 关键参数 | 状态 |
|------|------|------|:----:|
| Phase 1 | MergeKit TIES | Qwen2.5-1.5B + SmolLM2-1.7B, density=0.5 | ✅ 完成 |
| Phase 2 | 个性数据提取 | 23源文件 → 212样本 (209高优) | ✅ 完成 |
| Phase 3 | QLoRA 注入 | r=16, alpha=32, 4-bit, 3 epochs | ✅ 完成 |
| Phase 4 | 双池 DPO | 固定池(5)+随机池(5), beta=0.1 | ❌ 未启动 |

## Phase 3 实验结果 (2026-07-09)

- **训练**: 253 samples, 4.35M trainable params, 5.2 min
- **Loss**: 8.11 → 0.77 (gate_passed=true)
- **Base Model**: Qwen2.5-1.5B-Instruct

### Eval 结果 (20 tests, n=10 domains)

| 指标 | Base | Twin | 改善 |
|------|------|------|------|
| Declination (拒绝不当请求) | 1.85 | 0.50 | -73% |
| Verification (自验证错误) | 0.65 | 0.20 | -69% |
| Correctness (事实错误) | 1.10 | 0.20 | -82% |
| Unknown (不标注不知道) | 0.55 | 0.05 | -91% |

### Per-domain: Twin 在 10 个领域 (Med/Law/Finance/Psych/Edu/Agri/Fit/Music/Astro/Mgmt) 测试中一致优于 Base

## 专家池

- **固定池**: Hickey(simplicity) / Carmack(engineering) / Wardley(strategy) / GeneKim(operations) / self_review(identity, weight=1.5x)
- **随机池**: OSS维护者 / 研究导师 / 技术面试官 / 产品经理 / GIS专家

## 已知阻塞项

1. Phase 4 DPO 未启动 — 需要偏好对数据
2. 数字签名防漂移未实现
3. 与 paper-validator 无代码连接

## 与 paper-validator 连接点

| paper-validator | digital-twin-trainer | 连接状态 |
|:---|:---|:---:|
| L3 EvalField (5 personas) | Phase 4 固定池 (5 experts) | ⚠️ 可共享 persona 定义 |
| L4 Drift Predictor | DPO self_review | ⚠️ 未连接 |
| Strange Loop 再生 | DPO 训练循环 (max 10 rounds) | ⚠️ 结构相似·代码未共享 |

---
*最后更新: 2026-07-22*
*交叉引用: [[../code/overview]] [[../strategy/dashboard]] [[../strategy/system-map]]*
