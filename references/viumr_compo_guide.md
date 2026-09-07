
> **文件路径**：`BasicSoftware/VIUMR_COMPO.arxml`

  

### 文件定位

本文件是 N80KS VIU 域控制器的**核心软件架构描述文件（ARXML）**，属于 AUTOSAR Classic Platform ECU Extract 层级。在 ETAS ISOLAR 工具链中，它对应 ECU 的顶层 **Composition（组合组件）**，实体名为 `VIUMR_COMPO`（历史曾用名 `VIUMR_PPV_COM`、`VIUMR_SOP_COM`）。

  

### 核心作用

该文件定义了 VIU ECU 上**所有软件组件（SWC）的实例化、端口连接关系和顶层组织结构**，是应用层（ASW）与 RTE/BSW 之间的架构桥梁。

  

### 包含内容

  

| 内容类别 | 说明 | 规模 |

|----------|------|------|

| `COMPOSITION-SW-COMPONENT-TYPE` | ECU 顶层组合容器 | 1 个（`VIUMR_COMPO`） |

| `SW-COMPONENT-PROTOTYPE` | SWC 实例原型（如 `CPT_BCM_TailgateCtrlSrv`） | 大量 |

| `ASSEMBLY-SW-CONNECTOR` | 内部组件实例间 P-Port ↔ R-Port 互联 | 约 2,846 个 |

| `DELEGATION-SW-CONNECTOR` | 内部端口与组合边界的委托暴露 | 约 831 个 |

| `DATA-TYPE-MAPPING-SET` | ApplicationDataType → ImplementationDataType 映射 | 大量 |

| 标准 AR-PACKAGES | `AUTOSAR_ComM`、`AUTOSAR_EcuM` 等 BSW 接口定义 | 多个 |

  

### 在工具链中的角色

  

- **ISOLAR-A**：作为 Composition Diagram 的输入，图形化展示 SWC 实例、端口和连接器

- **ISOLAR-B / RTA-RTE**：读取 Connector 和 Port 定义，生成 RTE 接口代码（`Rte_Read_xxx`、`Rte_Write_xxx` 等）

- **RTA-BSW / DaVinci**：基于其中的 PortInterfaces 和 DataTypes 配置 COM、NvM、Dcm 等 BSW 模块

  

### 修改规范

  

⚠️ **此文件为关键配置文件，修改前必须备份！**

  

```bash

# 备份命令

arxml_backup.bat

# 或

python zd_dbg_ArchDevLog\modify_helper.py backup

```

  

- 修改后需**重新生成 RTE**

- 修改后需**全量编译验证**（`scons`）

- 禁止直接修改 `output/inc/` 下的符号链接头文件

- 所有修改需在 `zd_dbg_ArchDevLog/ArchModLog.md` 中记录