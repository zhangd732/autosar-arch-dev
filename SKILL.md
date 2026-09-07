---
name: autosar-arch-dev
description: >
  AUTOSAR Classic Platform 架构搭建助手。当用户提到任何与 ARXML 架构修改、SWC 新增、PORT 新增、
  Connector（ASC/DSC）构建、System Data Mapping、需求搭建、Composition 更新、Delegate Port 建立、
  Router 连接、信号映射、RTE 生成、ECU 抽取、ECU Extract、CSXfrm、RIPS 使能、enablerips、
  或 AUTOSAR 架构变更相关的操作时，**必须触发此 skill**。
  即使用户只说了"搭一下架构"、"改一下 arxml"、"新增一个 port"、"跑一下需求"这类简写，
  也应该使用该 skill。适用于 N80KS VIUMR 域控制器（AURIX TC377）项目的 AUTOSAR Classic Platform 架构开发。
---

# AUTOSAR Classic Platform 架构搭建助手

> **项目背景**：N80KS VIUMR 域控制器，AUTOSAR Classic Platform，AURIX TC377。  
> **核心文件**：`VIUMR_PPV_COM.arxml`（Composition 描述文件）、`VIUMR_COMPO.arxml`。  
> **工具链**：ETAS ISOLAR-A/B、RTA-RTE、RTA-BSW / DaVinci、SCons。

---

## 触发条件

以下任一关键词出现时，**必须**使用该 skill：

- 架构搭建、需求搭建、搭架构、改 arxml、ARXML 修改
- 新增 SWC、新增 PORT、新增接口、新增信号
- Connector、ASC、DSC、Assembly Connector、Delegation Connector
- System Data Mapping、信号映射、mapping 信号
- Delegate Port、Composition Port、Router、Router SWC
- RTE 生成、重新生成 RTE、跑构建、scons
- ECU 抽取、ECU Extract、ecuextract、FlatMap、FlatView 重新生成
- CSXfrm、CS_XFRM、RIPS 使能、enablerips、Data Transformation、RTE-PLUGIN-PROPS
- VIUMR_PPV_COM、VIUMR_COMPO、Composition 更新
- PORT-API-OPTION、OptionApi
- 需求包、AchReqPack、需求拆解

---

## 工作流程概览

架构变更的标准操作流分为 **6 个阶段**：

```
Step 0: 获取原始需求描述（由用户在对话中提供）
    ↓
Phase 1: 将原始需求描述整理成具体实施的表
    ↓
Phase 2: 分析需求包，提取 SWC 描述文件
    ↓
Phase 3: 更新 Composition（替换 SWC → 补充 Interface → 建立 Delegate Port）
    ↓
Phase 4: Connector 构建（DSC / ASC）
    ↓
Phase 5: System Data Mapping
    ↓
【条件工序】Gate A: 抽取输入域有变更且需重新生成 RTE？→ Phase 5.5a: ECU 抽取（headless）
    ↓
【条件工序】Gate B: 跨 ECU C/S 且配置了 Data Transformation？→ Phase 5.5b: CSXfrm 使能（headless）
    ↓
Phase 6: 验证（RTE 重新生成 + scons 编译 + 日志记录）
```

---

## Step 0: 获取原始需求描述

**这是整个流程的起点。原始需求描述必须由用户在对话中提供，Agent 不得自行编造或假设。**

当 skill 触发后，如果用户尚未提供原始需求描述，**必须先向用户询问**：

> "请提供本次架构变更的原始需求描述。需求描述通常包含以下内容：
> - 涉及哪些 SWC（如 tailgate_app、BCM_TailgateCtrlSrv 等）
> - 每个 SWC 需要新增哪些 PORT（名称、类型 R-PORT/P-PORT）
> - 是否需要做 Composition Delegate Port / mapping 信号 / COM 回调
> - 是否需要连接 Router（如 1B1 Router）
> - 是否有内部信号自动连线的需求
> 
> 请将原始需求描述完整粘贴到对话中。"

**只有在用户提供了原始需求描述后，才能进入 Phase 1。**

---

### 用户确认机制（关键）

从 Step 0 开始，**每一个阶段的输出都必须提交给用户审查，并获得明确许可后才能进入下一阶段**。具体规则：

1. **生成需求表后**：将 `req_table.md` 展示给用户，说明拆解逻辑和待确认项。
2. **请求许可**：明确询问用户"以上需求表是否准确？是否可以进入工程实现阶段？"
3. **用户许可**：用户确认（如"可以"、"没问题"、"继续"）→ 进入 Phase 2 及后续步骤。
4. **用户不许可**：用户提出修改意见或拒绝 → **终止后续工程实现步骤**，根据用户反馈修改需求表，重新提交确认。

---

## Phase 1: 需求点整理成具体实施的表

将用户提供的原始需求描述拆解为可落地的需求表，用于工程师审查。

### 标准表头（14 列）

| No | requirement | SWC name | Port/Interface Name | Port Type | Add PortApiOption | Router Name | Router RPort Name | Router PPort Name | Add Delegate PORT | Delegate Port Name | Signal Name | DSC Connection Name | ASC Connection Name |

### 各列填写规则

| 列名 | 规则 |
|------|------|
| **SWC name** | 从需求包中获取对应 SWC 描述文件的 **SHORT-NAME**（如 `BCM_Tailgate_APP`，不是需求简写 `tailgate_app`） |
| **Port/Interface Name** | 从需求包 SWC 描述文件（.arxml）中获取的**完整 PORT 名称**。需求简写可能缺少 `VIUBUS_` 前缀，需以 arxml 为准 |
| **Port Type** | `R-PORT`（接收/需求方）或 `P-PORT`（提供/发送方） |
| **Add PortApiOption** | 依据《需要配置 PORT-API-OPTIONS 的 SWC 清单》判断：SWC 在 72 个清单中 → `Y`，否则 → `N` |
| **Router Name** | 需求含"连接 xxx Router"时填写 Router 的组件类型 SHORT-NAME（如 `Router_VIUMRBUS_PEPS_0x1B1`），无需时填 `NA` |
| **Router RPort Name** | Router 上接收 Composition Delegate 的 R-PORT 名称。`0x1B1` 帧的信号通过 Signal Group `VIUBUS_SG_PEPS_0x1B1_PEPS_0x1B1_SigGrp` 统一接收 |
| **Router PPort Name** | Router 上向 App SWC 提供信号的 P-PORT 名称（如 `VIUBUS_PwrMod`） |
| **Add Delegate PORT** | 需求含"做 composition RPORT"或"mapping 信号" → `Y`；通过 Router 或直接连线 → `N` |
| **Delegate Port Name** | `Add Delegate PORT = Y` 时填写；不通过 Router 时与 SWC Port/Interface Name 相同 |
| **Signal Name** | 通信矩阵上的信号名称；通常与 Port/Interface Name 保持一致 |
| **DSC Connection Name** | 不涉及 Router 时：`DSC_CPT_<App实例名>_<Port>_<Port>`；涉及 Router 时：填写 Router 到 Composition 的 DSC 名称 |
| **ASC Connection Name** | 不涉及 Router 且需 Delegate 时：`NA`；涉及 Router 时：`ASC_CPT_Router_<RouterPort>_CPT_<App实例名>_<AppPort>`；内部信号时：`ASC_CPT_<Provider实例名>_<ProviderPort>_CPT_<Requester实例名>_<RequesterPort>` |

### 输出
生成 `req_table.md`，包含：需求汇总表、列标题对照说明、需求分类统计、待确认/待补充项。

### 完成后必须执行
生成需求表后，**必须暂停并提交给用户审查**：

> "以上是根据您提供的需求描述整理的需求表（`req_table.md`）。请审查：
> - 各列填写是否符合您的原始意图？
> - 是否有遗漏的需求项？
> - SWC 名称、Port 名称、Router 信息是否需要调整？
> 
> **确认无误后请回复'可以继续'，我将进入工程实现阶段。如您有修改意见，请指出，我将调整后重新提交确认。**"

**在未获得用户明确许可前，不得进入 Phase 2 及后续任何工程实现步骤。**

---

## Phase 2: 分析需求包

1. **定位需求包路径**：`\zd_dbg_ArchDevLog\VIUMR_P_AchReqPack\`，名称格式 `VIUMR_{Project Stage}_{date}`（如 `VIUMR_P_20260331`）。
2. **提取 SWC 描述文件**：在需求包中找到更新的 APP SWC 描述文件（以 SWC 名称作为文件名，扩展名 `.arxml`）。
3. **解析完整 Port 名**：打开 SWC 描述文件，确认新增的 PORT 及其引用的 INTERFACE 的**完整 SHORT-NAME**（注意 `VIUBUS_` 等前缀）。
4. **确认 Add PortApiOption**：对照 `需要配置 PORT-API-OPTIONS 的 SWC 清单.md` 判断是否需要添加。

### 2.5 输入完备性检查（Gate，不通过则停工）

在进入 Phase 3 之前，必须完成以下检查：

1. **系统信号存在性**：需求涉及的每个 CAN/LIN 信号，在 `BasicSoftware/InputFiles/*.arxml` 和 `BasicSoftware/System_EcuExtr.arxml` 中检索其 I-SIGNAL / SYSTEM-SIGNAL / 所在帧是否已定义。**任何一个缺失 → 停止后续工程步骤**，反馈用户等待系统方同步矩阵后再开工。
2. **需求与矩阵一致性**：需求描述中的帧号、信号名、信号组归属与矩阵不符时（实战案例：需求写 0x185，矩阵实际在 0x321），**以矩阵为准**，向用户/系统方确认差异并记录。
3. **源码交付方式**：确认 SWC 源码是否随包交付；若以 lib 方式后交付，本次只做架构 + RTE/OS 配置，验收标准相应调整（允许缺少 runnable 实现符号）。

---

## Phase 3: 更新 Composition

> **修改前必须备份！备份范围 = 所有待改文件，不只是 VIUMR_PPV_COM.arxml！**  
> 新增 SWC 典型涉及：VIUMR_PPV_COM.arxml、VIU_MR_FlatView_SWCD.arxml、System_Script_*_DataMapping.arxml、Rte_EcucValues.arxml、VIU_MR_Project_EcuC_EcucValues.arxml、Com_EcucValues.arxml、Dlt_Cfg_SWCD.arxml —— 逐一备份（含时间戳）。

> **新增前必查重（铁律）**：对每个计划新增的元素（接口、ComSignal 容器、MappingSet、端口等），先在目标文件/相关配置文件中全文检索其 SHORT-NAME。已存在 → 改为“在已有项上补参数”；不存在 → 才插入新项。系统方同步的配置文件可能已包含部分目标配置（实战案例：Com 信号容器已被矩阵同步带入，重复插入导致配置冲突）。

### Step 1: 替换 SWC 类型定义
从需求包 SWC 描述文件中找到 `APPLICATION-SW-COMPONENT-TYPE`，替换掉 `VIUMR_PPV_COM.arxml` 中同名的 `APPLICATION-SW-COMPONENT-TYPE`。

### Step 2: 确认并补充 INTERFACE 定义
1. 检查 PORT 引用的 INTERFACE 是否在 `VIUMR_PPV_COM.arxml`（或 `Interfaces.arxml`）中有定义。
2. 如果没有，将 SWC 描述文件中相应的 INTERFACE 定义复制到 **独立接口文件**（如 `Interfaces.arxml`）的 `AR-PACKAGE: Interfaces` 下。
3. 确保所有 PORT 的 `REQUIRED-INTERFACE-TREF` / `PROVIDED-INTERFACE-TREF` 路径指向 `/Interfaces/<InterfaceName>`。

### Step 3: 检查引用项完整性
检查 COMPOSITION 中相应的 `APPLICATION-SW-COMPONENT-TYPE` 所有引用项（DataType、DataConstr、ImplementationDataType 等）是否都有定义：
- 缺失定义 → 从 SWC 描述文件中复制到相应 AR-PACKAGE 下。
- 路径不准确 → 查找实际位置并修改路径。

### Step 4: 建立 Delegate Port 和 Delegation Connector
对于 `Add Delegate PORT = Y` 的需求项：
1. 在 Composition（`VIUMR_PPV_COM`）上建立与 SWC 新增 PORT **同名** 的 Delegate Port，引用**同样的 INTERFACE**。
2. 建立 `DELEGATION-SW-CONNECTOR` 连接 SWC Port 和 Composition Delegate Port。
3. Connector 名称遵循 `DSC_CPT_<InnerComp>_<InnerPort>_<OuterPort>` 格式。

### Step 5: 完整变更面清单（新增 SWC 的 9 项固定动作）

新增 SWC 时，除 Composition 主文件外，以下配套文件**缺一不可**（遗漏将导致 RTE 生成报错）：

| # | 动作 | 文件 |
|---|------|------|
| 1 | SWC 类型 + PORT-API-OPTION + DataTypeMappingSet 合入 | VIUMR_PPV_COM.arxml |
| 2 | 新接口（先查重；`_P` 变体放主文件 /Interfaces） | VIUMR_PPV_COM.arxml |
| 3 | CPT 实例 + Delegate 外口 + ASC/DSC | VIUMR_PPV_COM.arxml |
| 4 | **FlatView 扁平视图同步**（CPT + 外口 + 全部 connector，上下文路径换为 `/VIU_MR_FlatView/...`）。**优先级：优先由 Phase 5.5a 工具抽取重新生成 FlatView（方案 B）；本项手动同步仅在 ISOLAR 不可用时作为应急 fallback** | VIU_MR_FlatView_SWCD.arxml |
| 5 | System Data Mapping | System_Script_*_DataMapping.arxml |
| 6 | **Rte 任务映射**（RtePositionInTask = 目标任务当前最大值+1 即“放最后”；先脚本扫最大值） | ecu_config/rte/internal/Rte_EcucValues.arxml |
| 7 | **EcucPartition 登记**（EcucPartitionSoftwareComponentInstanceRef 加入任务所属分区，如 EcucPartitionQM_Core1；漏此项 → RTE 报 E002463） | ecu_config/bsw/VIU_MR_Project_EcuC_EcucValues.arxml |
| 8 | Dlt 配套（若 SWC 用 SendLogMessage，见 `references/integration_patterns.md`） | ecu_config/bsw/gen/swcd/Dlt_Cfg_SWCD.arxml |
| 9 | Com 信号 + 回调（先查重！） | ecu_config/bsw/VIU_MR_Project_Com_EcucValues.arxml |

---

## Phase 4: Connector 构建

### 命名规范

**DSC（Delegation Connector）**：
```
DSC_CPT_<InnerComp>_<InnerPort>_<OuterPort>
```
- `InnerComp`：内部 SWC 实例名（含 `CPT_` 前缀）
- `InnerPort` == `OuterPort`（100% 同名）

**ASC（Assembly Connector）**：
```
ASC_CPT_<ProviderComp>_<ProviderPort>_CPT_<RequesterComp>_<RequesterPort>
```
- `ProviderComp`：数据提供方实例名（含 `CPT_`）
- `RequesterComp`：数据接收方实例名（含 `CPT_`）
- Provider P-Port 名与 Requester R-Port 名基本一致（97.6% 同名）

### 长度限制
- 所有 Connector `SHORT-NAME` 存在 **128 字符硬限制**，超长会被截断。
- 写入前先用 `Select-String` 或 `grep` 在现有 `<CONNECTORS>` 节点中查重，确保全局唯一。

### XML 路径前缀速查

| 对象 | 路径前缀 |
|------|----------|
| 组合组件内实例 | `/SwComponentTypes/VIUMR_PPV_COM/CPT_...` |
| 组件类型定义中的 Port | `/SoftwareTypes/ComponentTypes/<CompType>/...` |
| 组合组件外部 Port | `/SwComponentTypes/VIUMR_PPV_COM/...` |

### DEST 属性速查

| 引用元素 | `DEST` 值 |
|----------|-----------|
| SW-COMPONENT-PROTOTYPE | `SW-COMPONENT-PROTOTYPE` |
| P-Port 原型 | `P-PORT-PROTOTYPE` |
| R-Port 原型 | `R-PORT-PROTOTYPE` |

详细的 XML 结构模板、完整示例和常见错误，见 `references/connector_guide.md`。

---

## Phase 5: System Data Mapping

对于需要 "mapping 信号" 的需求项：
1. 在 `System_Script_VIUMR_PPV_COM_DataMapping.arxml` 中建立 `SENDER-RECEIVER-TO-SIGNAL-MAPPING`。
2. 映射链：`SW-C 数据元素` → `SYSTEM-SIGNAL` → `I-SIGNAL` → `I-SIGNAL-I-PDU` → `CAN/LIN Frame`。
3. 端口命名反映总线类型：
   - `_ETHProxy_` → Ethernet
   - `ALLIN1_` 前缀 → LIN 总线
   - `CAN` 相关 → CAN 总线

详细的映射结构分析，见 `references/system_data_mapping.md`。

---

## Phase 5.5: ECU 抽取与 CSXfrm 使能（条件工序）

> **条件工序（铁律）**：5.5a 与 5.5b 不是每次必跑，必须先过各自的 Gate 判断，Gate 不通过则直接跳过。
> **前置配置（铁律）**：两个脚本顶部的 `ISOLAR_A_CMD` 必须先在脚本配置区填入本机 ISOLAR-A.cmd 完整路径，否则脚本直接拒绝运行。
> **确认机制沿用**：5.5a 产物核验通过后**必须暂停汇报用户**，获得许可后再进 5.5b；5.5b 完成后同样汇报，再进 Phase 6。

### Gate A：是否执行 Phase 5.5a（ECU 抽取）

**判断标准（可操作检查项）**：

1. 本次 Phase 3–5 的变更是否触及**抽取输入域**？即改动文件 ∈ {`VIUMR_PPV_COM.arxml`、`*_DataMapping.arxml`、通信矩阵文件}，也就是 Composition / 连接 / Mapping / 矩阵有变更。
2. 下一步是否**要重新生成 RTE**？

**两条都成立 → 执行 5.5a。** 只改了 BSW 配置类文件（Com_EcucValues、EcuC EcucValues、Dlt 配套）→ **跳过**，旧 ECU Extract 仍有效。首次抽取为全量，之后工具自动走增量（Iterative）模式。

**调用方式**：

```bat
python scripts/isolar_extract.py --project=<项目根目录> [--ecu=VIU_MR] [--system=System]
```

**产物核验要点**（脚本已自动判定，此处为人工复核口径）：

1. 退出码 0，且日志末行出现 `EcuExtract is generated successfully`。
2. ULF 中无 `<CATEGORY>ERROR</CATEGORY>` 条目。
3. 三个产物存在：`<ECUInstance>_FlatMap.arxml`、`<ECUInstance>_FlatView_SWCD.arxml`、`<System>_EcuExtr.arxml`（默认落在 `new/` 目录）。
4. 源 System Description 不会被修改，生成物全是新建元素——若发现源文件被改动，立即停工排查。

### Gate B：是否执行 Phase 5.5b（CSXfrm 使能）

**判断标准（可操作检查项，三条同时成立才执行）**：

1. 本次变更涉及 **Client/Server 接口**；
2. 该 C/S 通信为**跨 ECU**（intra-ECU C/S 一律跳过）；
3. 映射的 Signal 配置了 **Data Transformation**（Call/Return 双向）。

**跳过规则**：纯 S/R 信号变更跳过；intra-ECU C/S 跳过；日志报 `No possible FlatInstanceDescriptors` 视为已全部使能（或无满足前提的 FID），**不算错误**，回报人工检查映射即可。

**判据前置沉淀**：Phase 1 需求表中 INTERFACE 为 `CLIENT-SERVER-INTERFACE` 且跨 ECU 的行，即为 5.5b 的目标子集——整理需求表时就应标记出来。

**调用方式**：

```bat
python scripts/isolar_enablerips.py --project=<项目根目录> --flatmap=VIU_MR_FlatMap [--type=CS_XFRM]
```

**产物核验要点**：退出码 0 + 日志无异常 + ULF 无 ERROR；事后确认 FlatMap（或 splitfile）中目标 FID 下出现 `RTE-PLUGIN-PROPS`（脚本自动核验并注明核验粒度）。本质是给目标 FID 写入 RTE-PLUGIN-PROPS，RTE 生成时据此挂接 C/S 数据变换插件。

> 详细参数（全部命令行开关、偏好文件、增量抽取条件、ShortName 发现方法），见 `references/isolar_headless.md`。

---

## Phase 6: 验证与记录

1. **备份**：修改前已执行备份（`arxml_backup.bat`）。
2. **格式校验**：确认 XML 标签闭合正确，无非法字符。
3. **日志记录**：在 `zd_dbg_ArchDevLog/ArchModLog.md` 中记录：
   ```markdown
   | 修改时间 | 备份文件名 | 修改人 | 修改原因 | 备注 |
   |---|---|---|---|---|
   | 20260521_103651 | VIUMR_PPV_COM.arxml.bak_... | Agent | 新增 XXX Connector | 见详细日志 |
   ```
4. **重新生成 RTE**：Connector 或 Port 变更后，必须重新运行 RTA-RTE 生成代码。
   - ⚠️ **提醒用户先在 ISOLAR/RTA 工具中刷新/重载被外部修改的文件**（Eclipse 打开的文件不会自动读磁盘新内容），否则会拿旧模型生成，出现“修复假无效”。识别方法：对比被改文件的 mtime 与 RteErr.xml/rta-rte.ulf 的时间戳。
5. **编译验证**：执行 `scons` 进行全量构建，确保代码与 ARXML 同步。

### RTE 报错分诊表（RteErr.xml / rta-rte.ulf）

| 错误码 | 含义 | 处理 |
|--------|------|------|
| E002411 Unable to resolve reference | 引用路径失效，多为矩阵同步后接口/信号改名残留 | 全工程检索新旧名（含 VIU_MR_FlatMap.arxml 的 upstreamReference、SWC 访问点 TARGET-DATA-PROTOTYPE-REF），统一改为新路径 |
| E002463 not mapped to partition | SWC 实例 runnable 映射到某 OsApplication 的任务，但实例未登记到对应 EcucPartition | 在 VIU_MR_Project_EcuC_EcucValues.arxml 的对应 EcucPartition 补 EcucPartitionSoftwareComponentInstanceRef |
| 修复后重跑仍报同样的错 | 工具读了旧模型 | 对比文件 mtime 与日志时间；ISOLAR 中刷新/重开文件后重新生成 |
| C/S Data Transformation 相关生成错误 | 对应 FID 未使能 CSXfrm，RTE 找不到数据变换插件配置 | 检查 FlatMap 中对应 FID 下是否有 RTE-PLUGIN-PROPS；无 → 重跑 Phase 5.5b（enablerips -t=CS_XFRM） |
| enablerips 日志报 No possible FlatInstanceDescriptors | 前提不满足（无跨 ECU C/S 或未配 Transformation）或已全部使能 | 不算错误；回报人工检查映射与 Data Transformation 配置，确认后决定是否真正需要使能 |

---

## 参考资料索引

| 文档 | 路径（相对项目根目录） |
|------|------------------------|
| Connector 构建完整指南 | `references/connector_guide.md` |
| Connector 命名规则总结 | `references/connector_naming_rules.md` |
| System Data Mapping 分析 | `references/system_data_mapping.md` |
| PORT-API-OPTIONS SWC 清单 | `references/port_api_options_list.md` |
| VIUMR_COMPO.arxml 文件说明 | `references/viumr_compo_guide.md` |
| 集成模式卡片（Dlt 5 件套 / Router 扩展 / 任务部署 / 分区登记） | `references/integration_patterns.md` |
| ISOLAR headless 参数手册（ecuextract / enablerips 完整参数与判定） | `references/isolar_headless.md` |

> **提示**：当 skill 触发后，先读取项目根目录下的 `AGENTS.md` 获取最新项目上下文，再根据当前任务阶段读取对应的参考资料。
