# ISOLAR-A Headless 参数手册（ecuextract / enablerips）

> 项目：N80KS VIUMR，AUTOSAR Classic Platform，ETAS ISOLAR-AB 12.4.0。
> 本文是 Phase 5.5a（ECU 抽取）与 Phase 5.5b（CSXfrm 使能）两道条件工序的完整参数手册；
> Gate 判断标准与工序编排见 `SKILL.md` 的 "Phase 5.5" 章节。

## 目录

- [1. ecuextract：ECU 抽取命令](#1-ecuextractecu-抽取命令)
- [2. enablerips：RIPS 使能命令](#2-enableripsrips-使能命令)
- [3. 三层成功判定](#3-三层成功判定)
- [4. 产物文件与命名规则](#4-产物文件与命名规则)
- [5. 偏好文件 EcuExtract_CLI_Input.txt](#5-偏好文件-ecuextract_cli_inputtxt)
- [6. EcuInstance / System ShortName 的发现方法](#6-ecuinstance--system-shortname-的发现方法)
- [7. Iterative 增量抽取条件](#7-iterative-增量抽取条件)
- [8. CSXfrm 前提条件与常见提示语义](#8-csxfrm-前提条件与常见提示语义)
- [9. 应急：手动 FlatView 同步注意事项（方案 B 的 fallback）](#9-应急手动-flatview-同步注意事项方案-b-的-fallback)

---

## 1. ecuextract：ECU 抽取命令

从 System Description 中抽取指定 EcuInstance 的 ECU Extract，并生成 FlatMap / FlatView。

### 命令示例

```bat
ISOLAR-A.cmd -ecuextract --project="D:\Proj\X" -e=WiperControl --log="D:\logs\ecuextr.log" --ulf="D:\logs\ecuextr.ulf" --otheropt="D:\cfg\EcuExtract_CLI_Input.txt"
```

### 完整参数表

| 参数 | 短形式 | 必填性 | 说明 |
|------|--------|--------|------|
| `--project` | `-p` | 必填 | 项目文件夹路径（含 .project），子目录递归加载 |
| `--ecuinstance` | `-e` | 必填（二选一） | 目标 EcuInstance 的 ShortName（本项目默认 `VIU_MR`） |
| `--input` | `-i` | 必填（二选一） | 与 `--ecuinstance` 等价的输入指定方式 |
| `--system` | `-s` | 条件必填 | 仅当该 EcuInstance 属于多个 System 时必填（本项目默认 `System`） |
| `--otheropt` | — | 可选 | 偏好文件路径（见第 5 节），存放 GUI 中可勾选的抽取选项 |
| `--log` | `-l` | 可选 | 运行日志输出路径，成功判定的依据之一 |
| `--ulf` | — | 可选 | XML 错误报告（ULF）输出路径，ERROR 条目解析对象 |
| `--file` | — | 可选 | 无 .project 工程时直接加载指定 arxml 文件 |
| `--version` | `-v` | 可选 | 目标 AUTOSAR 版本，如 `-v=451` |

> 本项目默认调用：`python scripts/isolar_extract.py --project=<项目根目录>`，默认值 EcuInstance=`VIU_MR`、System=`System`。

---

## 2. enablerips：RIPS 使能命令

给 FlatMap 中目标 FlatInstanceDescriptor（FID）写入 `RTE-PLUGIN-PROPS`，RTE 生成时据此挂接插件（如 C/S 数据变换插件）。

### 命令示例

```bat
ISOLAR-A.cmd -enablerips --project="D:\Proj\X" --flatmap="WiperControl_FlatMap" -t=CS_XFRM --fids=[DEP_[A-Z_a-z_0-9]*] --splitfile="WiperControl_FlatMap_Split_1.arxml" --log="D:\logs\enablerips.log"
```

### 完整参数表

| 参数 | 短形式 | 必填性 | 说明 |
|------|--------|--------|------|
| `--project` | `-p` | 必填 | 项目文件夹路径（含 .project），子目录递归加载 |
| `--flatmap` | `-fm` | 必填 | 目标 FlatMap 的 ShortName（本项目默认 `VIU_MR_FlatMap`） |
| `--type` | `-t` | 必填 | 使能类型 ∈ `SR_COM \| IMPL_TIMED_COM \| CS_XFRM \| CS_SAFETY \| SIG_2_SRV \| ALL`；本工序固定 `CS_XFRM` |
| `--fids` | `-fi` | 可选 | 逗号分隔的 FID 列表，或方括号正则（如 `[DEP_[A-Z_a-z_0-9]*]`）。**省略则自动使能全部符合条件的 FID** |
| `--skipfids` | `-sfi` | 可选 | 要排除的 FID（与 `--fids` 同语法） |
| `--splitfile` | `-sf` | 可选 | 将 RtePluginProps 拆到独立 arxml；缺省则原位写入 FlatMap 文件 |
| `--log` | `-l` | 可选 | 运行日志输出路径 |
| `--ulf` | — | 可选 | XML 错误报告输出路径 |

> 本项目默认调用：`python scripts/isolar_enablerips.py --project=<项目根目录> --flatmap=VIU_MR_FlatMap`。

---

## 3. 三层成功判定

两个命令统一按三层判定，**任何一层不通过都按失败处理**：

| 层 | 判定对象 | 通过条件 |
|----|----------|----------|
| ① | 进程退出码 | `0`（`1` = 失败） |
| ② | `--log` 日志文件 | 末行（或日志中）出现成功字样；ecuextract 为 `EcuExtract is generated successfully` |
| ③ | `--ulf` XML 报告 | 不存在任何 `<CATEGORY>ERROR</CATEGORY>` 条目 |

ULF 解析要点：逐条 `<CATEGORY>` 提取，只统计值为 `ERROR` 的条目；WARNING / INFO 不阻断，但应在报告中列出供人工过目。

---

## 4. 产物文件与命名规则

ecuextract 的产物默认落在**目标目录 `new/`** 下（可用偏好文件调整）：

| 产物 | 命名规则 | 示例 |
|------|----------|------|
| FlatMap | `<ECUInstance>_FlatMap.arxml` | `VIU_MR_FlatMap.arxml` |
| FlatView SWCD | `<ECUInstance>_FlatView_SWCD.arxml` | `VIU_MR_FlatView_SWCD.arxml` |
| ECU Extract | `<System>_EcuExtr.arxml` | `System_EcuExtr.arxml` |
| FlatView 报告 | `<目标目录>/_log/FlatViewReport.xml` | `new/_log/FlatViewReport.xml` |

**铁律**：源 System Description **不会被修改**，生成物全是新建元素。核验时若发现源文件被改动，立即停工排查。`_log/FlatViewReport.xml` 记录 FlatView 生成的细节，产物异常时优先查它。

---

## 5. 偏好文件 EcuExtract_CLI_Input.txt

`--otheropt` 指向的偏好文件承载 GUI 中的抽取选项（目标目录、抽取范围开关等）。

**本 skill 已内置模板**：`assets/EcuExtract_CLI_Input.txt`（复制自本机安装目录 `E:\tools\ETAS\ISOLAR-AB_12.4.0\ExamplesForCustomization\01_examples_for_headless_use\` 官方样例，ISOLAR-AB 12.4.0）。默认直接把脚本配置区 `DEFAULT_OTHEROPT` 指向它即可；如需项目级定制，复制副本修改，不要改模板本体。

**格式**：纯文本 `KEY=VALUE`，每行一项。修改前先备份；不认识的 KEY 不要删，缺项回落到工具默认值。

**关键 KEY 速查**（与 agent 自动化最相关的子集，完整注释见模板文件）：

| KEY | 默认 | 作用 / 自动化建议 |
|---|---|---|
| `UPDATE_EXISTING_ECU_EXTRACT` | `TRUE` | 已存在抽取时覆盖更新（增量迭代的基础），保持 TRUE |
| `BACKUP` | `FALSE` | 被覆盖的生成文件留 `.bkup` 备份；团队协作迭代期建议设 TRUE |
| `IGNORE_COMSPEC_CONFLICTS` | `TRUE` | ComSpec 冲突降级为警告继续抽取；FALSE 则直接报错中止 |
| `BREAK_BUILD` / `IGNORE_ERROR_ID` | `""` | 按错误 ID 精确控制中止/放行（如 `IGNORE_ERROR_ID="EcuExtract_ERR_29"`），agent 流水线调参重点 |
| `CONSIDER_CLIENT_SERVER` | `TRUE` | 为跨 ECU C/S 端口生成 FID——**CSXfrm 使能的前提**，必须 TRUE |
| `CONSIDER_INTRA_ECU_CLIENT_SERVER` | `FALSE` | intra-ECU C/S 是否生成 FID，通常保持 FALSE |
| `EXTRACT_OTHER_ECU_MAPPINGS` | `TRUE` | 带入对端 ECU 的 DataMapping（跨 ECU 通信对端视图），保持 TRUE |
| `GENERATE_FIBEX_ELEMENTS` | `TRUE` | 抽取时重新生成 Fibex 元素（注意 TRUE 会先删后建现有 ECU Extract 中的 Fibex） |
| `RESOLVE_VARIATION_POINT` / `BINDING_TIME_TO_RESOLVE_VARIANTS` | `FALSE` / `SYSTEM-DESIGN-TIME` | 变体解析开关与绑定时间（SYSTEM-DESIGN-TIME / CODE-GENERATION-TIME / PRE-COMPILE-TIME） |
| `GENERATE_MCSUPPORT_DATA` | `FALSE` | 生成 McSupportData（RTA-A2L 用），需要时 TRUE |
| `APPLY_NAMING_CONVENTION_RULE` | `TRUE` | 连接器按规则重命名（ASC_/DSC_ 前缀），与本项目命名规范一致，保持 TRUE |
| `FLATMAP_ARXML_FILE` / `FLATVIEW_ARXML_FILE` / `SYSTEM_ARXML_FILE` | 占位符规则 | 产物文件名（`<ECUInstance-ShortName>_FlatMap.arxml` 等），与产物核验逻辑对应 |

**获取更新模板的方式（二选一，模板与 ISOLAR 版本不匹配时重做）**：

1. **GUI 导出（推荐）**：ISOLAR-A 菜单 `File > Export > ISOLAR-A > Export Headless Input File(s)`，勾选 **"Ecu Extract"**，导出即得；
2. **安装目录样例**：`<ISOLAR 安装目录>\ExamplesForCustomization\01_examples_for_headless_use` 下有官方样例，复制后按项目修改。

---

## 6. EcuInstance / System ShortName 的发现方法

不要凭记忆猜 ShortName，直接从项目 arxml 解析：

- EcuInstance：检索 `<ECU-INSTANCE>` 元素块下的第一个 `<SHORT-NAME>`（本项目为 `VIU_MR`，旁证：项目里已有 `VIU_MR_FlatView_SWCD.arxml`）；
- System：检索 `<SYSTEM>` 元素块下的第一个 `<SHORT-NAME>`（本项目为 `System`，旁证：`BasicSoftware/System_EcuExtr.arxml`）。

脚本支持 `python scripts/isolar_extract.py --project=<项目根目录> --discover` 自动扫描项目内全部 `*.arxml` 并打印候选清单，人工确认后再回填脚本配置区。

---

## 7. Iterative 增量抽取条件

- **首次**对某 EcuInstance 抽取为**全量**；
- 之后在同一项目上重复执行 ecuextract，工具自动走**增量（Iterative）模式**：只刷新与本次变更相关的部分，已有 FlatMap / ECU Extract 在增量基础上更新；
- 触发增量的前提是抽取输入域的变更可定位（Composition / 连接 / Mapping / 矩阵有差异）；若偏好文件或目标目录被清空，则退化为全量。

---

## 8. CSXfrm 前提条件与常见提示语义

**CSXfrm（`-t=CS_XFRM`）使能的前提（三条同时成立）**：

1. 目标端口为 Client/Server 接口；
2. 该 C/S 通信参与 **Inter-ECU** 通信（intra-ECU 不在此列）；
3. 映射的 Signal 配置了 **Data Transformation**（Call/Return 双向）。

**`No possible FlatInstanceDescriptors` 语义**：工具在 FlatMap 中找不到任何满足上述前提且尚未使能的 FID。两种可能——前提本就不满足（无跨 ECU C/S，或未配 Transformation），或目标 FID **已全部使能**。该提示**不算错误**，不按硬失败处理，回报人工检查映射即可。

---

## 9. 应急：手动 FlatView 同步注意事项（方案 B 的 fallback）

正常路径：FlatView 由 Phase 5.5a 的 ecuextract 重新生成（方案 B 优先）。**仅当 ISOLAR 不可用时**，才回退到 Phase 3 Step 5 第 4 项的手动同步。手动同步时：

1. 在 `VIU_MR_FlatView_SWCD.arxml` 中补齐 CPT + 外口 + 全部 connector；
2. 所有上下文路径必须换为 `/VIU_MR_FlatView/...` 前缀，与主 Composition 的路径体系区分；
3. 同步完成后在修改日志中**显式标注"手动 FlatView 同步（ISOLAR 不可用应急）"**，待 ISOLAR 恢复后**必须重跑一次 Phase 5.5a 让工具校准**，以工具产物为准；
4. 手动同步面容易遗漏 connector，交付前对照 Composition 主文件逐一核对。
