# VIUMR_PPV_COM.arxml Connector 构建指南

> **适用范围**：指导 Agent 在 `BasicSoftware/VIUMR_PPV_COM.arxml` 中正确创建 `ASSEMBLY-SW-CONNECTOR` 和 `DELEGATION-SW-CONNECTOR`。
> **项目背景**：N80KS VIUMR 域控制器，AUTOSAR Classic Platform，基于 AURIX TC377。

---

## 1. 概述

`VIUMR_PPV_COM.arxml` 中的 `<CONNECTORS>` 节点位于 `VIUMR_PPV_COM` 组合组件（Composition）内部，用于定义各 SWC 实例之间的端口连接关系。

### 1.1 Connector 类型

| 类型 | 标签名 | 作用 | 当前数量 |
|------|--------|------|----------|
| 组装连接器 | `<ASSEMBLY-SW-CONNECTOR>` | 将两个内部组件实例的 P-Port 与 R-Port 互联 | 2846 |
| 委托连接器 | `<DELEGATION-SW-CONNECTOR>` | 将内部组件端口暴露到组合组件边界，或反向委托 | 831 |

### 1.2 文件定位

```xml
<!-- 查找路径：AR-PACKAGE -> SwComponentTypes -> VIUMR_PPV_COM -> CONNECTORS -->
<COMPOSITION-SW-COMPONENT-TYPE>
  <SHORT-NAME>VIUMR_PPV_COM</SHORT-NAME>
  <COMPONENTS>
    <SW-COMPONENT-PROTOTYPE>...</SW-COMPONENT-PROTOTYPE>
  </COMPONENTS>
  <CONNECTORS>
    <!-- 所有 ASC / DSC 定义在此节点内 -->
  </CONNECTORS>
</COMPOSITION-SW-COMPONENT-TYPE>
```

---

## 2. 命名规范（SHORT-NAME）

Connector 的 `SHORT-NAME` 必须**全局唯一**，采用长命名策略，由多个下划线分隔的语义段组成。

### 2.1 ASSEMBLY-SW-CONNECTOR 命名规则

**格式模板**：
```
ASC_CPT_<ProviderComp>_<ProviderPort>_CPT_<RequesterComp>_<RequesterPort>
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| `ASC_` | 固定前缀，表示 Assembly-Sw-Connector | `ASC_` |
| `CPT_<ProviderComp>` | Provider（数据提供方）组件实例名 | `CPT_BCM_SysPwrMode_Consumer` |
| `<ProviderPort>` | Provider 侧的 P-Port 名称 | `BCM_SysPwrMode_NtfPowermodeSt` |
| `CPT_<RequesterComp>` | Requester（数据请求方）组件实例名 | `CPT_RoofLampPowermodeCtrlAPP` |
| `<RequesterPort>` | Requester 侧的 R-Port 名称 | `BCM_SysPwrMode_NtfPowermodeSt` |

**完整示例**：
```
ASC_CPT_BCM_SysPwrMode_Consumer_BCM_SysPwrMode_NtfPowermodeSt_CPT_RoofLampPowermodeCtrlAPP_BCM_SysPwrMode_NtfPowermodeSt
```

### 2.2 DELEGATION-SW-CONNECTOR 命名规则

**格式模板**：
```
DSC_CPT_<InnerComp>_<InnerPort>_<OuterPort>
```

**字段说明**：

| 字段 | 说明 | 示例 |
|------|------|------|
| `DSC_` | 固定前缀，表示 Delegation-Sw-Connector | `DSC_` |
| `CPT_<InnerComp>` | 内部被委托的组件实例名 | `CPT_BCM_TailgateCtrlSrv_Provider` |
| `<InnerPort>` | 内部组件的实际端口名 | `BCM_TailgateCtrlSrv_ntfMotStallSt_R_P` |
| `<OuterPort>` | 组合组件 `VIUMR_PPV_COM` 暴露的外部端口名 | `BCM_TailgateCtrlSrv_ntfMotStallSt_R_P` |

**完整示例**：
```
DSC_CPT_BCM_TailgateCtrlSrv_Provider_BCM_TailgateCtrlSrv_ntfMotStallSt_R_P_BCM_TailgateCtrlSrv_ntfMotStallSt_R_P
```

### 2.3 命名约束

1. **唯一性**：同一个 `<CONNECTORS>` 节点内，任意两个 `SHORT-NAME` 不能重复。
2. **长度限制**：ARXML 标准未硬性限制，但建议控制在 **256 字符**以内；若超出，可对中间段做合理截断（保持可读性）。
3. **分隔符**：统一使用下划线 `_` 连接，禁止出现空格、中划线 `-`、点 `.`。
4. **前缀约定**：
   - 组件实例名必须以 `CPT_` 开头（Component Prototype）。
   - ASC 必须以 `ASC_` 开头。
   - DSC 必须以 `DSC_` 开头。

---

## 3. XML 结构模板

### 3.1 ASSEMBLY-SW-CONNECTOR 模板

```xml
<ASSEMBLY-SW-CONNECTOR>
  <SHORT-NAME>ASC_CPT_${ProviderComp}_${ProviderPort}_CPT_${RequesterComp}_${RequesterPort}</SHORT-NAME>
  <PROVIDER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">
      /SwComponentTypes/VIUMR_PPV_COM/CPT_${ProviderComp}
    </CONTEXT-COMPONENT-REF>
    <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">
      /SoftwareTypes/ComponentTypes/${ProviderComp}/${ProviderPort}
    </TARGET-P-PORT-REF>
  </PROVIDER-IREF>
  <REQUESTER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">
      /SwComponentTypes/VIUMR_PPV_COM/CPT_${RequesterComp}
    </CONTEXT-COMPONENT-REF>
    <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">
      /SoftwareTypes/ComponentTypes/${RequesterComp}/${RequesterPort}
    </TARGET-R-PORT-REF>
  </REQUESTER-IREF>
</ASSEMBLY-SW-CONNECTOR>
```

**变量替换说明**：

| 变量 | 来源 | 示例值 |
|------|------|--------|
| `${ProviderComp}` | 提供数据的组件实例名（去掉 CPT_ 前缀） | `BCM_SysPwrMode_Consumer` |
| `${ProviderPort}` | 该组件的 P-Port 名 | `BCM_SysPwrMode_NtfPowermodeSt` |
| `${RequesterComp}` | 接收数据的组件实例名（去掉 CPT_ 前缀） | `RoofLampPowermodeCtrlAPP` |
| `${RequesterPort}` | 该组件的 R-Port 名 | `BCM_SysPwrMode_NtfPowermodeSt` |

### 3.2 DELEGATION-SW-CONNECTOR 模板（P-Port 委托）

将内部组件的 **P-Port** 暴露到组合组件外部边界：

```xml
<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>DSC_CPT_${InnerComp}_${InnerPort}_${OuterPort}</SHORT-NAME>
  <INNER-PORT-IREF>
    <P-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">
        /SwComponentTypes/VIUMR_PPV_COM/CPT_${InnerComp}
      </CONTEXT-COMPONENT-REF>
      <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">
        /SoftwareTypes/ComponentTypes/${InnerComp}/${InnerPort}
      </TARGET-P-PORT-REF>
    </P-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
  <OUTER-PORT-REF DEST="P-PORT-PROTOTYPE">
    /SwComponentTypes/VIUMR_PPV_COM/${OuterPort}
  </OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>
```

### 3.3 DELEGATION-SW-CONNECTOR 模板（R-Port 委托）

将组合组件外部边界的 **R-Port** 委托给内部组件：

```xml
<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>DSC_CPT_${InnerComp}_${InnerPort}_${OuterPort}</SHORT-NAME>
  <INNER-PORT-IREF>
    <R-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">
        /SwComponentTypes/VIUMR_PPV_COM/CPT_${InnerComp}
      </CONTEXT-COMPONENT-REF>
      <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">
        /SoftwareTypes/ComponentTypes/${InnerComp}/${InnerPort}
      </TARGET-R-PORT-REF>
    </R-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
  <OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">
    /SwComponentTypes/VIUMR_PPV_COM/${OuterPort}
  </OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>
```

**变量替换说明**：

| 变量 | 来源 | 示例值 |
|------|------|--------|
| `${InnerComp}` | 内部被委托的组件实例名（去掉 CPT_ 前缀） | `BCM_TailgateCtrlSrv_Provider` |
| `${InnerPort}` | 内部组件的端口名 | `BCM_TailgateCtrlSrv_ntfMotStallSt_R_P` |
| `${OuterPort}` | 组合组件外部端口名 | `BCM_TailgateCtrlSrv_ntfMotStallSt_R_P` |

---

## 4. Agent 构建 Connector 的步骤

### Step 1：确认连接需求

明确以下信息：
- 是**组件间互联**（ASC）还是**端口委托**（DSC）？
- Provider / Requester 的组件实例名和端口名分别是什么？
- 对于 DSC，是 P-Port 向外暴露，还是 R-Port 向内委托？

### Step 2：检查端口兼容性

- **接口类型一致**：P-Port 和 R-Port 必须引用同一个 `SENDER-RECEIVER-INTERFACE` 或 `CLIENT-SERVER-INTERFACE`。
- **数据元素匹配**：若为 S/R 接口，DataElement 的名称和数据类型需匹配。
- **方向正确**：ASC 必须连接 P-Port → R-Port，不能反向。

### Step 3：生成 SHORT-NAME

严格按照第 2 章的命名规则拼接，确保：
- 以 `ASC_` 或 `DSC_` 开头。
- 组件实例段以 `CPT_` 开头。
- 整个名称在现有 `<CONNECTORS>` 中无重复。

**快速查重命令（PowerShell）**：
```powershell
$pattern = "ASC_CPT_BCM_MyComp_MyPort_CPT_OtherComp_OtherPort"
Select-String -Path "BasicSoftware\VIUMR_PPV_COM.arxml" -Pattern $pattern
```

### Step 4：填充 XML 节点

使用第 3 章的模板，替换所有 `${变量}`，生成完整的 XML 片段。

### Step 5：插入到文件正确位置

1. 在 `BasicSoftware/VIUMR_PPV_COM.arxml` 中定位到 `<CONNECTORS>` 节点。
2. 将新生成的 connector 插入到 `</CONNECTORS>` 结束标签之前。
3. 保持 XML 缩进风格（2 或 4 空格缩进，与周围代码一致）。

### Step 6：验证与备份

1. **备份**：修改前必须执行 `arxml_backup.bat` 或 `python zd_dbg_ArchDevLog\modify_helper.py backup`。
2. **格式校验**：确认 XML 标签闭合正确，无非法字符。
3. **日志记录**：在 `zd_dbg_ArchDevLog/ArchModLog.md` 中记录修改内容。
4. **重新生成 RTE**：Connector 变更后，需重新运行 RTA-RTE 生成代码，再执行 `scons` 构建验证。

---

## 5. 完整示例

### 5.1 ASSEMBLY-SW-CONNECTOR 示例

**场景**：`BCM_ReverseLamp_Ri` 组件提供倒车灯状态，`BCM_ReverseLampCtrlSrv` 组件接收该状态。

```xml
<ASSEMBLY-SW-CONNECTOR>
  <SHORT-NAME>ASC_CPT_BCM_ReverseLamp_Ri_BCM_ReverseLamp_Ri_CPT_BCM_ReverseLampCtrlSrv_BCM_ReverseLamp_Ri</SHORT-NAME>
  <PROVIDER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/CPT_BCM_ReverseLamp_Ri</CONTEXT-COMPONENT-REF>
    <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">/SoftwareTypes/ComponentTypes/BCM_ReverseLamp_Ri/BCM_ReverseLamp_Ri</TARGET-P-PORT-REF>
  </PROVIDER-IREF>
  <REQUESTER-IREF>
    <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/CPT_BCM_ReverseLampCtrlSrv</CONTEXT-COMPONENT-REF>
    <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">/SoftwareTypes/ComponentTypes/BCM_ReverseLampCtrlSrv/BCM_ReverseLamp_Ri</TARGET-R-PORT-REF>
  </REQUESTER-IREF>
</ASSEMBLY-SW-CONNECTOR>
```

### 5.2 DELEGATION-SW-CONNECTOR 示例（P-Port 委托）

**场景**：将 `BCM_Window_Right_Provider` 的内部 P-Port 暴露到 `VIUMR_PPV_COM` 外部。

```xml
<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>DSC_CPT_BCM_Window_Right_Provider_BCM_Window_Right_ntfWinWinRunngSts_FR_P_BCM_Window_Right_ntfWinWinRunngSts_FR_P</SHORT-NAME>
  <INNER-PORT-IREF>
    <P-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/CPT_BCM_Window_Right_Provider</CONTEXT-COMPONENT-REF>
      <TARGET-P-PORT-REF DEST="P-PORT-PROTOTYPE">/SoftwareTypes/ComponentTypes/BCM_Window_Right_Provider/BCM_Window_Right_ntfWinWinRunngSts_FR_P</TARGET-P-PORT-REF>
    </P-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
  <OUTER-PORT-REF DEST="P-PORT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/BCM_Window_Right_ntfWinWinRunngSts_FR_P</OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>
```

### 5.3 DELEGATION-SW-CONNECTOR 示例（R-Port 委托）

**场景**：将组合组件外部的 R-Port 委托给内部 `IoHwAb_Core0` 组件。

```xml
<DELEGATION-SW-CONNECTOR>
  <SHORT-NAME>DSC_CPT_IoHwAb_Core0_SIo_Actr_SlideRMot_ExtrMirrAdjYpos_R_GetAngleSnsrFltSt_SIo_Actr_SlideRMot_ExtrMirrAdjYpos_R_GetAngleSnsrFltSt</SHORT-NAME>
  <INNER-PORT-IREF>
    <R-PORT-IN-COMPOSITION-INSTANCE-REF>
      <CONTEXT-COMPONENT-REF DEST="SW-COMPONENT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/CPT_IoHwAb_Core0</CONTEXT-COMPONENT-REF>
      <TARGET-R-PORT-REF DEST="R-PORT-PROTOTYPE">/SoftwareTypes/ComponentTypes/IoHwAb_Core0/SIo_Actr_SlideRMot_ExtrMirrAdjYpos_R_GetAngleSnsrFltSt</TARGET-R-PORT-REF>
    </R-PORT-IN-COMPOSITION-INSTANCE-REF>
  </INNER-PORT-IREF>
  <OUTER-PORT-REF DEST="R-PORT-PROTOTYPE">/SwComponentTypes/VIUMR_PPV_COM/SIo_Actr_SlideRMot_ExtrMirrAdjYpos_R_GetAngleSnsrFltSt</OUTER-PORT-REF>
</DELEGATION-SW-CONNECTOR>
```

---

## 6. 常见错误与注意事项

| 错误类型 | 说明 | 规避方法 |
|----------|------|----------|
| **SHORT-NAME 重复** | 同一 `<CONNECTORS>` 内出现同名 connector | 拼接前先用 `Select-String` 或 `grep` 查重 |
| **DEST 属性错误** | `DEST` 写错导致解析失败 | 严格使用表格中的 DEST 值 |
| **路径前缀错误** | 组件实例路径用了 `/SoftwareTypes/...` | 组件实例路径必须是 `/SwComponentTypes/VIUMR_PPV_COM/CPT_xxx` |
| **P/R 方向反了** | ASC 中 PROVIDER 指向了 R-Port | PROVIDER 只能引用 P-PORT，REQUESTER 只能引用 R-PORT |
| **未备份直接修改** | 导致原始配置丢失 | 修改前执行 `arxml_backup.bat` |
| **未重新生成 RTE** | 代码与 ARXML 不同步 | 修改 ARXML 后必须重新运行 RTA-RTE 生成 |
| **XML 缩进混乱** | 破坏文件可读性 | 保持与周围代码一致的缩进（建议 2 空格） |

---

## 7. 快速参考表

### 7.1 DEST 属性速查

| 引用元素 | `DEST` 值 |
|----------|-----------|
| SW-COMPONENT-PROTOTYPE | `SW-COMPONENT-PROTOTYPE` |
| P-Port 原型 | `P-PORT-PROTOTYPE` |
| R-Port 原型 | `R-PORT-PROTOTYPE` |

### 7.2 路径前缀速查

| 对象类型 | 路径前缀 |
|----------|----------|
| 组合组件内的实例 | `/SwComponentTypes/VIUMR_PPV_COM/CPT_...` |
| 组件类型定义中的 P-Port | `/SoftwareTypes/ComponentTypes/<CompType>/...` |
| 组件类型定义中的 R-Port | `/SoftwareTypes/ComponentTypes/<CompType>/...` |
| 组合组件外部 P-Port | `/SwComponentTypes/VIUMR_PPV_COM/...` |
| 组合组件外部 R-Port | `/SwComponentTypes/VIUMR_PPV_COM/...` |

---

## 8. 附录：ARXML 修改规范（引用）

根据项目 `AGENTS.md` 要求：

> **修改 ARXML 前必须备份！**

```bash
# 方法1：批处理备份
arxml_backup.bat

# 方法2：Python 辅助脚本
python zd_dbg_ArchDevLog\modify_helper.py backup
python zd_dbg_ArchDevLog\modify_helper.py log
python zd_dbg_ArchDevLog\modify_helper.py diff
```

修改完成后需在 `zd_dbg_ArchDevLog/ArchModLog.md` 中记录：

```markdown
| 修改时间 | 备份文件名 | 修改人 | 修改原因 | 备注 |
|---|---|---|---|---|
| 20260521_103651 | VIUMR_PPV_COM.arxml.bak_20260521_103651 | Agent | 新增 XXX Connector | 见详细日志 |
```

---

*本文档基于 `VIUMR_PPV_COM.arxml` 中 2846 个 ASC 和 831 个 DSC 的实际定义分析生成。*
