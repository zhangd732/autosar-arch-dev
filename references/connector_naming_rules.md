# VIUMR_COMPO.arxml Connector 命名规则总结

## 一、Connector 类型概览

`VIUMR_COMPO.arxml` 中仅存在两种 Connector 类型：

| 类型 | 数量 | XML 标签 | 前缀 |
|:---|:---:|:---|:---|
| **Assembly Connector** | 2846 | `<ASSEMBLY-SW-CONNECTOR>` | `ASC_` |
| **Delegation Connector** | 831 | `<DELEGATION-SW-CONNECTOR>` | `DSC_` |

> **无其他 Connector 类型**（如 Pass-Through Connector 等在此文件中不存在）。

---

## 二、全局长度限制

所有 Connector 名称存在 **128 字符硬长度限制**，超长名称会被截断：

| 类型 | 平均长度 | 最大长度 | 被截断数量 | 截断比例 |
|:---|:---:|:---:|:---:|:---:|
| Assembly Connector | 108 | 128 | 593 | **20.8%** |
| Delegation Connector | 85 | 128 | 5 | **0.6%** |

> **注意**：被截断的名称仍保持可识别的前缀结构，但末端的 Port 名或 SWC 名会被截短。

---

## 三、Assembly-SW-Connector 命名规则

### 3.1 基本格式

```
ASC_<SourceSWC>_<SourcePort>_<TargetSWC>_<TargetPort>
```

**验证结果**：
- 符合率：**78.4%** (2230/2846) 完全匹配
- 截断率：**21.6%** (616/2846) 因超 128 字符被截断

### 3.2 字段解析

| 字段 | 示例值 | 说明 |
|:---|:---|:---|
| `ASC` | `ASC` | Assembly-Sw-Connector 固定前缀 |
| `<SourceSWC>` | `CPT_BCM_TailgateCtrlSrv` | Provider（P-Port 所在 SWC）实例名 |
| `<SourcePort>` | `BCM_TailgateCtrlSrv_ntfTailgateSt` | Provider 的 P-Port 名 |
| `<TargetSWC>` | `CPT_LegacyEcuRouter_MR` | Requester（R-Port 所在 SWC）实例名 |
| `<TargetPort>` | `BCM_TailgateCtrlSrv_ntfTailgateSt` | Requester 的 R-Port 名 |

### 3.3 命名示例

**标准示例（未被截断）**：
```
ASC_CPT_BCM_ReverseLamp_Ri_BCM_ReverseLamp_Ri_CPT_BCM_ReverseLampCtrlSrv_BCM_ReverseLamp_Ri
```
解析：
| 字段 | 值 |
|:---|:---|
| Source SWC | `CPT_BCM_ReverseLamp_Ri` |
| Source Port | `BCM_ReverseLamp_Ri` |
| Target SWC | `CPT_BCM_ReverseLampCtrlSrv` |
| Target Port | `BCM_ReverseLamp_Ri` |

**截断示例（超 128 字符）**：
```
Actual:   ASC_CPT_BCM_Actr_SlideRMot_ExtrMirrAdjXpos_R_BCM_Actr_SlideRMot_ExtrMirrAdjXpos_R_CPT_BCM_RearMirr_Ri_BCM_Actr_SlideRMot_ExtrMir
Expected: ASC_CPT_BCM_Actr_SlideRMot_ExtrMirrAdjXpos_R_BCM_Actr_SlideRMot_ExtrMirrAdjXpos_R_CPT_BCM_RearMirr_Ri_BCM_Actr_SlideRMot_ExtrMirrAdjXpos_R
```
> 末端 `rAdjXpos_R` 被截断为 `Mir`（实际长度 128，期望长度 138）。

### 3.4 端口同名规律

在 Assembly Connector 中，**Provider P-Port 名与 Requester R-Port 名基本一致**：

| 状态 | 数量 | 比例 |
|:---|:---:|:---:|
| P-Port == R-Port | 2777 | **97.6%** |
| P-Port != R-Port | 69 | **2.4%** |

> 2.4% 的不匹配属于历史拼写变体（如 `ntfFltSt` vs `ntfFltst`）。

---

## 四、Delegation-SW-Connector 命名规则

### 4.1 基本格式

```
DSC_<InnerSWC>_<InnerPort>_<OuterPort>
```

由于 **Inner Port 名 == Outer Port 名**（符合率 100%），实际表现为：
```
DSC_<InnerSWC>_<PortName>_<PortName>
```

**验证结果**：
- 符合率：**99.8%** (829/831) 完全匹配
- 截断率：**0.2%** (2/831) 因超 128 字符被截断

### 4.2 字段解析

| 字段 | 示例值 | 说明 |
|:---|:---|:---|
| `DSC` | `DSC` | Delegation-Sw-Connector 固定前缀 |
| `<InnerSWC>` | `CPT_BCM_Window_Right_Provider` | 内部 SWC 实例名 |
| `<InnerPort>` | `BCM_Window_Right_ntfWinWinRunngSts_FR_P` | 内部 Port 名 |
| `<OuterPort>` | `BCM_Window_Right_ntfWinWinRunngSts_FR_P` | 外部 Port 名（与 Inner 同名） |

### 4.3 命名示例

**标准示例**：
```
DSC_CPT_Router_VIUMRBUS_BDCU_SWS_0x287_MRLIN1_MoveNext_MRLIN1_MoveNext
```
解析：
| 字段 | 值 |
|:---|:---|
| Inner SWC | `CPT_Router_VIUMRBUS_BDCU_SWS_0x287` |
| Inner/Outer Port | `MRLIN1_MoveNext` |

**带 Provider 角色的示例**（P-Port 委托）：
```
DSC_CPT_BCM_Window_Right_Provider_BCM_Window_Right_ntfWinWinRunngSts_FR_P_BCM_Window_Right_ntfWinWinRunngSts_FR_P
```
解析：
| 字段 | 值 |
|:---|:---|
| Inner SWC | `CPT_BCM_Window_Right_Provider` |
| Inner/Outer Port | `BCM_Window_Right_ntfWinWinRunngSts_FR_P` |

> 注意：当 SWC 实例名本身包含 `_Provider` 或 `_Consumer` 后缀时，该后缀属于 `<InnerSWC>` 的一部分。

### 4.4 Inner == Outer 规律

在所有 **831 个 Delegation Connector** 中：
- **Inner Port 名 == Outer Port 名**：831/831 = **100%**

这是本项目 Delegation 的严格设计规范。

---

## 五、命名规则对比表

| 对比项 | Assembly Connector | Delegation Connector |
|:---|:---|:---|
| **前缀** | `ASC_` | `DSC_` |
| **核心功能** | 连接两个内部 SWC 的 P-Port ↔ R-Port | 将内部 SWC Port 委托到 Composition 边界 |
| **命名格式** | `ASC_<源SWC>_<源Port>_<目标SWC>_<目标Port>` | `DSC_<内部SWC>_<内部Port>_<外部Port>` |
| **Port 同名规律** | 源 Port == 目标 Port（97.6%） | 内部 Port == 外部 Port（100%） |
| **SWC 名前缀** | 全部以 `CPT_` 开头 | 全部以 `CPT_` 开头 |
| **长度限制** | 128 字符（20.8% 被截断） | 128 字符（0.6% 被截断） |
| **完全匹配率** | 78.4% | 99.8% |

---

## 六、按 SWC 分类的 Connector 前缀分布

### 6.1 Assembly Connector 的主要来源 SWC

| 来源 SWC 前缀 | 数量 | 说明 |
|:---|:---:|:---|
| `CPT_BCM_` | 1678 | BCM 模块内部互联 |
| `CPT_IoHwAb_` | 366 | IO 硬件抽象层 |
| `CPT_Dem_` | 176 | 诊断事件管理 |
| `CPT_LegacyEcuRouter_` | 150 | 聚合路由器 |
| `CPT_DIDMgr_` | 100 | DID 管理 |
| `CPT_Dlt_` | 73 | 诊断日志跟踪 |

### 6.2 Delegation Connector 的主要内部 SWC

| 内部 SWC 前缀 | 数量 | 说明 |
|:---|:---:|:---|
| `CPT_BCM_` | 372 | BCM 模块委托到边界 |
| `CPT_Router_` | 221 | Router SWC 委托到边界 |
| `CPT_ILCM_` | 188 | ILCM 模块委托到边界 |
| `CPT_LegacyEcuRouter_` | 8 | LegacyEcuRouter 委托 |
| `CPT_PWT_` | 6 | 动力总成委托 |

---

## 七、特殊命名模式

### 7.1 `_P` 后缀（仅 Delegation 中出现）

在 Delegation Connector 中，大量 Port 名以 `_P` 结尾：
```
DSC_CPT_BCM_RearDefrostCtrlSrv_Provider_BCM_RearDefrostCtrlSrv_NtfRearDefrostSt_P_BCM_RearDefrostCtrlSrv_NtfRearDefrostSt_P
```

含义：`_P` 是 **P-Port 的显式标记**（在 Composition 层 356 个 `_P` 后缀端口中，**100% 是 P-Port**）。

### 7.2 `_Provider` / `_Consumer` 后缀（SWC 实例名）

部分 SWC 实例名本身带有 `_Provider` 或 `_Consumer` 后缀：
```
DSC_CPT_BCM_VIUMR_ECUCtrlCmd_Provider_BCM_VIUMR_ECUCtrlCmd_NtfTailgateCloseMode_P_...
DSC_CPT_BCM_SysPwrMode_Consumer_BCM_SysPwrMode_NtfPowermodeSt_...
```

这说明 **Delegation 的 `<InnerSWC>` 字段可能包含角色后缀**，而非仅在 Port 层标记角色。

### 7.3 `_SigGrp`（Signal Group）

用于整组信号的委托：
```
DSC_CPT_Router_VIUMRBUS_PEPS_0x1B1_VIUBUS_SG_PEPS_0x1B1_PEPS_0x1B1_SigGrp_VIUBUS_SG_PEPS_0x1B1_PEPS_0x1B1_SigGrp
DSC_CPT_Router_VIUMRBUS_VIUMR_0x227_VIUBUS_SG_VIUMR_0x227_VIUMR_0x227_SigGrp_VIUBUS_SG_VIUMR_0x227_VIUMR_0x227_SigGrp
```

### 7.4 `ETHProxy`（以太网代理）

```
DSC_CPT_BCM_WiperCtrlSrv_Rear_Provider_BCM_WiperCtrlSrv_Rear_ETHProxy_P_BCM_WiperCtrlSrv_Rear_ETHProxy_P
DSC_CPT_BCM_TRReSeatAdjSrv_Provider_BCM_TRReSeatAdjSrv_ETHProxy_P_BCM_TRReSeatAdjSrv_ETHProxy_P
```

---

## 八、实践速查

### 8.1 从 Connector 名反推连接关系

**Assembly Connector 示例**：
```
ASC_CPT_BCM_TailgateCtrlSrv_BCM_TailgateCtrlSrv_ntfTailgateSt_CPT_LegacyEcuRouter_MR_BCM_TailgateCtrlSrv_ntfTailgateSt
                ^^^^^^^^^^^^^^^^^^^^^^^^                      ^^^^^^^^^^^^^^^^^^^^^^
                Source SWC + Source Port                      Target SWC + Target Port
```

**Delegation Connector 示例**：
```
DSC_CPT_Router_VIUMRBUS_BDCU_SWS_0x287_MRLIN1_MoveNext_MRLIN1_MoveNext
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^^
          Inner SWC                      Inner Port       Outer Port (同名)
```

### 8.2 判断名称是否被截断

- 长度 **< 120**：大概率完整
- 长度 **= 128**：极大概率被截断，需结合 ARXML 中的 `<PROVIDER-IREF>` / `<REQUESTER-IREF>` 确认完整信息
