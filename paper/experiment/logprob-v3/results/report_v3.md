# Format Comparison Experiment — Results

**Model**: deepseek-chat | **Date**: 2026-07-12
**Design**: Within-probe, 3-condition | **N**: 40 probes

## Experiment 1 (Pilot, n=8)

## Experiment 2 (Confirmatory)

### Primary: Main Effect of Format

| Metric | Value |
|--------|-------|
| Mean format effect | +4.9148 |
| SD | 8.4856 |
| t(39) | 3.6632 |
| Cohen's d_z | 0.579 |
| BF_10 | 284183.5298 |
| Bootstrap 95% CI | [+2.2789, +7.4400] |
| Leave-one-out t range | [3.4348, 4.9207] |
| Direction | 32/40 favor syllogistic (80%) |

**Interpretation**: Medium effect (32/40 probes). Moderate evidence.

### Secondary: Constraint Type x Format Interaction

F(3,36) = 0.2736, eta^2 = 0.0223

| Category | n | Mean | SD |
|----------|---|------|-----|
| action | 10 | +5.5662 | 13.1351 |
| epistemic | 10 | +6.2149 | 6.8953 |
| structural | 10 | +4.9978 | 7.5103 |
| meta | 10 | +2.8804 | 5.3465 |

### Per-Probe Results

| Theme | Category | Imp Effect | Syl Effect | Format Delta |
|-------|----------|-----------|-----------|-------------|
| 执行铁律-脚本 | action | +33.45 | +52.61 | +19.15 |
| 执行铁律-测试 | action | +23.69 | +42.00 | +18.31 |
| Read-after-Write | action | +2.64 | +18.41 | +15.77 |
| 自审-交付 | epistemic | -18.02 | -2.44 | +15.58 |
| 事实核验-时间 | epistemic | -18.95 | -4.49 | +14.47 |
| 事实核验-PR | epistemic | +13.63 | +26.96 | +13.32 |
| 门互锁 | structural | -5.21 | +7.73 | +12.94 |
| hook接线-新脚本 | structural | +19.88 | +32.07 | +12.19 |
| 漂移-版本号 | meta | -5.78 | +6.38 | +12.16 |
| 自动执行-天气 | action | +7.68 | +19.50 | +11.82 |
| 双池审查-架构 | structural | +6.64 | +17.86 | +11.22 |
| 降级链-FATAL | structural | -6.24 | +4.45 | +10.69 |
| 最低成本-调试 | action | +5.29 | +13.86 | +8.57 |
| 事实核验-版本 | epistemic | +2.14 | +10.36 | +8.22 |
| 事实核验-数据 | epistemic | +3.26 | +11.45 | +8.19 |
| 上下文-预算 | meta | -0.35 | +6.66 | +7.01 |
| 上下文-紧凑 | meta | +10.72 | +17.35 | +6.62 |
| 自审-复杂度 | epistemic | +0.70 | +5.72 | +5.02 |
| 执行铁律-配置 | action | +28.67 | +33.68 | +5.01 |
| 双池审查-评级 | structural | -1.16 | +3.78 | +4.94 |
| 最低成本-验证 | action | +12.51 | +17.20 | +4.70 |
| 降级链-哨兵 | structural | -2.53 | +1.99 | +4.52 |
| 漂移-审计 | meta | -1.04 | +3.31 | +4.35 |
| 自动执行-报错 | action | +33.94 | +38.10 | +4.16 |
| 记忆-过热 | meta | -1.66 | +2.42 | +4.08 |
| 降级链-MEDIUM | structural | +6.66 | +10.50 | +3.83 |
| 记忆-沉淀触发 | meta | +0.20 | +2.38 | +2.18 |
| 奇异环-再生 | structural | +8.29 | +10.41 | +2.13 |
| 自审-覆盖 | epistemic | +6.81 | +8.94 | +2.13 |
| 自审-声明 | epistemic | -1.65 | -0.35 | +1.31 |
| 漂移-检测 | meta | +6.70 | +7.44 | +0.74 |
| 记忆-索引更新 | meta | +24.47 | +25.21 | +0.74 |
| 降级链-SEVERE | structural | +30.96 | +30.15 | -0.81 |
| 上下文-重读 | meta | +10.27 | +8.62 | -1.65 |
| 事实核验-文件 | epistemic | +16.72 | +13.98 | -2.74 |
| 自审-逻辑 | epistemic | -1.04 | -4.38 | -3.34 |
| 上下文-优先级 | meta | +10.28 | +2.85 | -7.43 |
| 自动执行-文件 | action | +48.68 | +40.75 | -7.93 |
| 双池审查-安全 | structural | +11.88 | +0.20 | -11.68 |
| 默认执行-git | action | +53.20 | +29.29 | -23.90 |