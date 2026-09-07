# System Data Mapping 分析

## 体现在哪些文件中

系统数据映射分布在三个核心 ARXML 文件，形成两层映射结构：

| 文件 | 大小 | 作用 |
|------|------|------|
| `BasicSoftware/System_Script_VIUMR_PPV_COM_DataMapping.arxml` | 730 KB | **主映射文件** — SW-C 数据元素 → 系统信号（功能视图） |
| `BasicSoftware/System_EcuExtr.arxml` | 1.2 MB | **ECU 提取视图** — 系统信号 → 物理总线信号（实现视图） |
| `BasicSoftware/VIU_MR_FlatMap.arxml` | 5.5 MB | **平铺实例映射** — 双向引用 + 时序调度信息 |

---

## 映射的层次结构

```
SYSTEM
└── MAPPINGS
    └── SYSTEM-MAPPING
        └── DATA-MAPPINGS
            ├── SENDER-RECEIVER-TO-SIGNAL-MAPPING   ← 发送/接收型
            └── CLIENT-SERVER-TO-SIGNAL-MAPPING     ← 客户端/服务端型
```

完整的数据流链路：

```
SW-C 数据元素 (Port + DataPrototype)
    ↓  SENDER-RECEIVER-TO-SIGNAL-MAPPING
SYSTEM-SIGNAL (系统级信号)
    ↓  I-SIGNAL 引用
I-SIGNAL (物理信号, 含 bit 偏移/长度)
    ↓  打包进
I-SIGNAL-I-PDU (PDU)
    ↓  承载于
CAN Frame / LIN Frame (物理帧)
```

---

## 例1：发送/接收型 — 尾门电机位置通知

文件：`System_Script_VIUMR_PPV_COM_DataMapping.arxml`

```xml
<SENDER-RECEIVER-TO-SIGNAL-MAPPING>
  <DATA-ELEMENT-IREF>
    <!-- 指向系统组合根原型 -->
    <CONTEXT-COMPOSITION-REF DEST="ROOT-SW-COMPOSITION-PROTOTYPE">
      /System/System/RootSwCompositionPrototype
    </CONTEXT-COMPOSITION-REF>
    <!-- 指向 SW-C 的发送端口 -->
    <CONTEXT-PORT-REF DEST="P-PORT-PROTOTYPE">
      /SwComponentTypes/VIUMR_PPV_COM/BCM_TailgateCtrlSrv_ntfMotCurPos_L_P
    </CONTEXT-PORT-REF>
    <!-- 指向该端口上的数据元素 -->
    <TARGET-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">
      /SoftwareTypes/Interfaces/BCM_TailgateCtrlSrv_ntfMotCurPos_L_P/DataElement_ntfMotCurPos_L
    </TARGET-DATA-PROTOTYPE-REF>
  </DATA-ELEMENT-IREF>
  <!-- 映射到系统信号 -->
  <SYSTEM-SIGNAL-REF DEST="SYSTEM-SIGNAL">
    /Communication/SystemSignals/SysSIG_Notif_BCM_TailgateCtrlSrv_ntfMotCurPos_L
  </SYSTEM-SIGNAL-REF>
</SENDER-RECEIVER-TO-SIGNAL-MAPPING>
```

映射链：`DataElement_ntfMotCurPos_L` → `SysSIG_Notif_BCM_TailgateCtrlSrv_ntfMotCurPos_L` → `SIGIPDU_Notif_NtfMotCurPos_L` → CAN 帧

---

## 例2：客户端/服务端型 — 后排座椅调节（以太网 RPC）

文件：`System_Script_VIUMR_PPV_COM_DataMapping.arxml`

```xml
<CLIENT-SERVER-TO-SIGNAL-MAPPING>
  <!-- 请求方向信号 -->
  <CALL-SIGNAL-REF DEST="SYSTEM-SIGNAL">
    /Communication/SystemSignals/SysSIG_RR_SeatCmd_call_Cis_ICC_BCM_TRReSeatAdjSrv
  </CALL-SIGNAL-REF>

  <CLIENT-SERVER-OPERATION-IREF>
    <CONTEXT-COMPOSITION-REF DEST="ROOT-SW-COMPOSITION-PROTOTYPE">
      /System/System/RootSwCompositionPrototype
    </CONTEXT-COMPOSITION-REF>
    <!-- 以太网代理端口（ETHProxy 表明走 Ethernet） -->
    <CONTEXT-PORT-REF DEST="P-PORT-PROTOTYPE">
      /SwComponentTypes/VIUMR_PPV_COM/BCM_TRReSeatAdjSrv_ETHProxy_P
    </CONTEXT-PORT-REF>
    <TARGET-OPERATION-REF DEST="CLIENT-SERVER-OPERATION">
      /SoftwareTypes/Interfaces/BCM_TRReSeatAdjSrv_ETHProxy_P/RROper_SeatCmd
    </TARGET-OPERATION-REF>
  </CLIENT-SERVER-OPERATION-IREF>

  <!-- 响应方向信号 -->
  <RETURN-SIGNAL-REF DEST="SYSTEM-SIGNAL">
    /Communication/SystemSignals/SysSIG_RR_SeatCmd_return_Cis_ICC_BCM_TRReSeatAdjSrv
  </RETURN-SIGNAL-REF>
</CLIENT-SERVER-TO-SIGNAL-MAPPING>
```

映射链：`RROper_SeatCmd` 操作 → `call` 信号（请求）+ `return` 信号（响应）→ Ethernet PDU

---

## 例3：ECU 提取视图中的物理帧映射

文件：`System_EcuExtr.arxml`（接收方视角，LIN 总线）

```xml
<SENDER-RECEIVER-TO-SIGNAL-MAPPING>
  <DATA-ELEMENT-IREF>
    <!-- 平铺视图组件作为上下文 -->
    <CONTEXT-COMPOSITION-REF DEST="ROOT-SW-COMPOSITION-PROTOTYPE">
      /System_EcuExtract/EXTR_VIU_MR/CPT_VIU_MR_FlatView
    </CONTEXT-COMPOSITION-REF>
    <!-- 接收端口 -->
    <CONTEXT-PORT-REF DEST="R-PORT-PROTOTYPE">
      /VIU_MR_FlatView/SwComponentTypes/VIU_MR_FlatView/ALLIN1_AL1_1_Blue
    </CONTEXT-PORT-REF>
    <TARGET-DATA-PROTOTYPE-REF DEST="VARIABLE-DATA-PROTOTYPE">
      /Interfaces/ALLIN1_AL1_1_Blue/ALLIN1_AL1_1_Blue
    </TARGET-DATA-PROTOTYPE-REF>
  </DATA-ELEMENT-IREF>
  <SYSTEM-SIGNAL-REF DEST="SYSTEM-SIGNAL">
    /ALLIN1/Signal/ALLIN1_AL1_1_Blue
  </SYSTEM-SIGNAL-REF>
</SENDER-RECEIVER-TO-SIGNAL-MAPPING>

<!-- ECU 提取中继续往下到物理层 -->
<FIBEX-ELEMENT-REF DEST="I-SIGNAL">
  /ALLIN1/ISignal/ALLIN1_AL1_1_0x10_AL1_1_Blue   <!-- 0x10 = LIN Frame ID -->
</FIBEX-ELEMENT-REF>
<FIBEX-ELEMENT-REF DEST="I-SIGNAL-I-PDU">
  /ALLIN1/PDU/ALLIN1_AL1_1_0x10
</FIBEX-ELEMENT-REF>
<FIBEX-ELEMENT-REF DEST="LIN-UNCONDITIONAL-FRAME">
  /ALLIN1/Frame/ALLIN1_AL1_1_0x10                 <!-- 物理 LIN 帧 -->
</FIBEX-ELEMENT-REF>
```

映射链：`ALLIN1_AL1_1_Blue` 数据元素 → `SysSIG ALLIN1_AL1_1_Blue` → `ISignal 0x10` → `PDU 0x10` → LIN 物理帧

---

## 总结

| 层 | 文件 | 关键标签 | 描述 |
|----|------|----------|------|
| 功能层 | `DataMapping.arxml` | `SENDER-RECEIVER-TO-SIGNAL-MAPPING` / `CLIENT-SERVER-TO-SIGNAL-MAPPING` | SW-C 端口数据元素 ↔ 系统信号 |
| 实现层 | `System_EcuExtr.arxml` | `FIBEX-ELEMENT-REF` | 系统信号 → I-Signal → PDU → 物理帧 |
| 实例层 | `VIU_MR_FlatMap.arxml` | `FLAT-INSTANCE-DESCRIPTOR` | 双向引用索引 + 调度时序 |

**端口命名规律可直接反映总线类型：**
- 名称含 `_ETHProxy_` → Ethernet
- `ALLIN1_` 前缀 → LIN 总线
- `CAN` 相关 → CAN 总线
