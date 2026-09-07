# 集成模式卡片（Integration Patterns）

> 来源于 Req #181（FRSeatEasyEntryCtrlApp，20260805）实战验证的可复用集成模式。
> 项目：N80KS VIUMR，AUTOSAR Classic，RTA-RTE。

---

## 模式 1：Dlt 集成（SwcMessageService 5 件套 + SessionControlCallback 3 件套）

APP SWC 使用 Dlt 日志服务（`SendLogMessage`）时，需配置两组套件：

### 1A. SwcMessageService 5 件套（收日志）

| # | 位置 | 内容 |
|---|------|------|
| 1 | SWC 类型（VIUMR_PPV_COM.arxml） | R-PORT `<SwcName>_DltSwcMessageService` → `/AUTOSAR_Dlt/ClientServerInterfaces/DltSwcMessageService`；runnable 内 ASYNCHRONOUS-SERVER-CALL-POINT + RESULT-POINT |
| 2 | Composition ASC | `ASC_CPT_Dlt_SwcMessageService_<SwcName>_CPT_<SwcName>_<SwcName>_DltSwcMessageService`，Provider P 口 = `/AUTOSAR_Dlt/SwComponentTypes/Dlt/SwcMessageService_<SwcName>` |
| 3 | Dlt_Cfg_SWCD.arxml（ecu_config/bsw/gen/swcd/） | Dlt 侧新增 P-PORT `SwcMessageService_<SwcName>`（4 个 SERVER-COM-SPEC：RegisterContext/UnRegisterContext/SendLogMessage/SendTraceMessage，QUEUE-LENGTH=1）+ 4 个 OPERATION-INVOKED-EVENT（`OpInvEvent_DltSwcMessageService_{RC,URC,SLM,STM}_<SwcName>`） |
| 4 | Dlt_Cfg_SWCD.arxml PORT-API-OPTION | `SessionId_<SwcName>` = 当前全部 SessionId 最大值+1（先脚本扫 `SessionId_(\w+)` 取 max） |
| 5 | Rte_EcucValues.arxml | `OpInvEvent_DltSwcMessageService_SLM_<SwcName>` 映射到 `OsTask_Rte_Event_ASW_Core1`，RtePositionInTask 取该任务当前 max+1 |

### 1B. SessionControlCallback 3 件套（Dlt 反调通知，漏则编译报错 undeclared）

Dlt EcucValues 中的 DltContext 会在 `Dlt_Cfg_PBcfg.c` 生成 `Rte_Call_SessionControlCallback_<Swc>_LogLevelChangedNotification / _TraceStatusChangedNotification` 函数指针引用。必须在 `Dlt_Cfg_SWCD.arxml` 中补齐，否则 RTE 不生成该 API：

| # | 内容 |
|---|------|
| 1 | Dlt SWC 新增 R-PORT ×2：`SessionControlCallback_<SwcName>` → `/AUTOSAR_Dlt/ClientServerInterfaces/LogTraceSessionControl`；`InjectCallback_<SwcName>` → `/AUTOSAR_Dlt/ClientServerInterfaces/InjectionCallback` |
| 2 | PORT-API-OPTION ×2（ENABLE-TAKE-ADDRESS=true，INDIRECT-API=false），各指向一个 R 口 |
| 3 | SYNCHRONOUS-SERVER-CALL-POINT ×3：`SSC_SessionControlCallback_<SwcName>`（LogLevelChangedNotification）、`SSC_SessionControlCallbackTrace_<SwcName>`（TraceStatusChangedNotification）、`SSC_InjectCallback_<SwcName>`（InjectCall） |

### 1C. DLT 用户数数组扩容（漏则校核不通过，运行时 GetLogInfo 截断/越界）

`Dlt_Cfg_SWCD.arxml` 的 `Dlt_LogInfoType` 中有两处**手工维护的定长数组**，其 `ARRAY-SIZE` 必须等于 DLT 用户总数（= SessionId 条目数）：

- `contextDesc`（上下文描述数组，约 10524 行）
- `appIdInfo`（应用 ID 信息数组，约 10580 行）

新增第 N 个 DLT 用户后，两处 `ARRAY-SIZE` 必须从 N-1 改为 N。**校验方法**（脚本一行可查）：

```python
import re, io
t = io.open(r'Dlt_Cfg_SWCD.arxml', encoding='utf-8').read()
sizes = re.findall(r'<SHORT-NAME>(contextDesc|appIdInfo)</SHORT-NAME>\s*<CATEGORY>TYPE_REFERENCE</CATEGORY>(?:\s*<!--[^>]*-->)?\s*<ARRAY-SIZE>(\d+)</ARRAY-SIZE>', t)
users = len(re.findall(r'SessionId_\w+</SHORT-LABEL>', t))
print(sizes, 'users =', users)   # 两处 ARRAY-SIZE 必须都等于 users
```

参考样板：`FRSeatLocAdjApp`（全套现成，照抄改名即可）。

---

## 模式 2：Router 扩展（Tx 方向，如 Router_VIUMRBUS_VIUMR_0x31C）

APP 新增一路 CAN 输出经 Router 时：

1. **Router SWC 类型**（/SoftwareTypes/ComponentTypes/Router_*）：
   - 新增 R-PORT `VIUBUS_<Sig>` → `/Interfaces/VIUBUS_<Sig>`
   - 新增 P-PORT `VIUBUS_<Sig>_P` → `/Interfaces/VIUBUS_<Sig>_P`（`_P` 接口定义在主文件 `/Interfaces` 包，数据元素名**不带** `_P`，类型引用 `/VIUBUS/ImplementationDataTypes/VIUBUS_<Sig>_Type`，该类型由 InputFiles 矩阵提供）
   - Router 的 10ms runnable 增加 `DRPA_VIUBUS_<Sig>_0`（读 R 口）+ `DSP_VIUBUS_<Sig>_0`（写 `_P` 口）
2. **Composition**：
   - ASC：App P 口 → Router R 口（Provider = App）
   - 新增外口 P-PORT `VIUBUS_<Sig>_P` + DSC（Router P 口 → 外口）
3. **DataMapping**：外口 P → `/VIUBUS/Signal/VIUBUS_<Sig>`（SENDER-RECEIVER-TO-SIGNAL-MAPPING，CONTEXT-PORT-REF 用 P-PORT-PROTOTYPE）
4. **Com**：Tx ComSignal（容器名 `S_VIUBUS_<Frame>_<Sig>_VIUBUS_CAN_Tx`）挂入对应 Tx IPdu 的 ComIPduSignalRef 列表；BitPosition/BitSize 以矩阵 I-SIGNAL-TO-I-PDU-MAPPING 为准；回调 `ComNotification=Rte_COMCbk_S_...`
5. **FlatView**：以上 connector/外口同步扁平化

Rx 方向直连信号（不经 Router）：Composition 外口 R + DSC + Rx DataMapping + Com Rx 信号（TRIGGERED + `Rte_COMCbk_S_` 回调）。

---

## 模式 3：任务部署（含"执行顺序放最后"）

- runnable→task 映射在 `ecu_config/rte/internal/Rte_EcucValues.arxml` 的 `RteSwComponentInstance/RteEventToTaskMapping` 容器
- **"放最后"实现**：脚本扫描目标任务全部 `RtePositionInTask`，取 max+1
- 典型映射：10ms 周期 runnable → `OsTask_ASW_10ms_Core1`；InitEvent → `OsTask_ASW_InitTask_Core1`
- OS 侧（Os_EcucValues.arxml）无需改动；任务优先级由 OsTask 属性决定，与 PositionInTask 无关（PositionInTask 是同任务内的执行顺序）
- 实例引用路径走扁平视图：`/VIU_MR_FlatView/SwComponentTypes/VIU_MR_FlatView/CPT_<SwcName>`

## 模式 4：EcucPartition 登记（必做，漏则 E002463）

- 文件：`ecu_config/bsw/VIU_MR_Project_EcuC_EcucValues.arxml`
- 容器：`/ETAS_Project/EcucModuleConfigurationValuess/EcuC/EcucPartitionCollection/EcucPartitionQM_Core1`（ASW Core1 任务所属分区）
- 动作：在其 REFERENCE-VALUES 末尾追加 `EcucPartitionSoftwareComponentInstanceRef`，CONTEXT-ELEMENT-REF 固定为 `/System_EcuExtract/EXTR_VIU_MR/CPT_VIU_MR_FlatView`，TARGET-REF 指向扁平 CPT
- 自查：新 SWC 映射到的所有任务所属的 OsApplication 实现的分区，都需有登记（本工程 ASW 10ms/Init/Rte_Event 三个 Core1 任务均属 OsApplicationQM_Core1，一条即可）

---

## 实施工程化建议（实战验证）

1. **锚点断言 + 倒序行号插入**脚本化修改大文件：每个插入点先断言锚点行内容，全部通过后按行号降序插入，避免行号漂移。
2. 改完必做：XML 良构解析 + 与备份 diff（应只有预期插入块、0 删除）+ 新 SHORT-NAME 全局唯一性/128 字符检查。
3. 参考存档：`zd_dbg_ArchDevLog/Req181_FRSeatEasyEntryCtrlApp_20260805/`（含 8 个实施脚本 freasyentry_step1~7，可直接改造成新 SWC 的脚本）。
