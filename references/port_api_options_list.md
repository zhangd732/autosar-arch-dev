## VIUMR_COMPO.arxml 中需要配置 PORT-API-OPTIONS 的 SWC 清单

经对 `BasicSoftware/VIUMR_COMPO.arxml` 的全量解析，共有 **72 个 SWC** 为其端口配置了 `PORT-API-OPTIONS`，合计 **923 条** 配置记录。

### 配置特征
| 属性 | 统计 |
|------|------|
| **总 SWC 数** | 72 |
| **总 PORT-API-OPTION 条目** | 923 |
| **ENABLE-TAKE-ADDRESS=true** | 921 (99.8%) |
| **R-Port** | 710 |
| **P-Port** | 213 |

> **技术含义**：`ENABLE-TAKE-ADDRESS=true` 表示 RTE 会为该端口生成支持**取地址**的 API（如 `Rte_Read_xxx` 返回指针或允许对端口数据取 `&`），SWC 可以直接操作数据地址而非值拷贝。

---

### 按端口数量排序的 72 个 SWC

| 排名 | SWC 名称 | 总端口数 | R-Port | P-Port |
|:---:|:---|:---:|:---:|:---:|
| 1 | `BCM_Seat_FrntRi` | 49 | 37 | 12 |
| 2 | `BCM_TRReSeatAdjSrv` | 33 | 27 | 6 |
| 3 | `BCM_FrntRiSeatAdjSrv` | 33 | 27 | 6 |
| 4 | `BCM_CushionTemp_MidRi` | 29 | 23 | 6 |
| 5 | `BCM_CushionTemp_FrntRi` | 29 | 23 | 6 |
| 6 | `BCM_CushionTemp_ThirdRi` | 29 | 23 | 6 |
| 7 | `FRSeatLocAdjApp` | 27 | 27 | 0 |
| 8 | `Swc_Diag_OTA` | 27 | 21 | 6 |
| 9 | `TRRSeatLocAdjApp` | 27 | 27 | 0 |
| 10 | `BCM_RearMirr_Ri` | 25 | 19 | 6 |
| 11 | `BCM_Seat_ThirdRi` | 25 | 17 | 8 |
| 12 | `BCM_WiperCtrlSrv_Rear` | 24 | 21 | 3 |
| 13 | `BCM_FrntRiSeatPosnMemSrv` | 24 | 23 | 1 |
| 14 | `FRSeatDiagAdjCtrlApp` | 23 | 23 | 0 |
| 15 | `TRRSeatDiagAdjCtrlApp` | 23 | 23 | 0 |
| 16 | `SWC_OTA` | 20 | 1 | 19 |
| 17 | `BCM_RSeatAntiPinch` | 19 | 13 | 6 |
| 18 | `BCM_Hndl_ReRi` | 19 | 12 | 7 |
| 19 | `BCM_Hndl_FrntRi` | 19 | 12 | 7 |
| 20 | `BCM_Door_FR` | 15 | 8 | 7 |
| 21 | `BCM_Door_RR` | 15 | 8 | 7 |
| 22 | `BCM_DoorPwrSuc_FR` | 14 | 10 | 4 |
| 23 | `BCM_DoorPwrSuc_RR` | 14 | 10 | 4 |
| 24 | `BCM_FrntDefrost` | 14 | 12 | 2 |
| 25 | `RearWiperSwtCtrlApp` | 12 | 12 | 0 |
| 26 | `BCM_RearDefrostCtrlSrv` | 12 | 10 | 2 |
| 27 | `BCM_VIUMR_ECUCtrlCmd` | 12 | 4 | 8 |
| 28 | `BCM_SavePwrCtrlSrv` | 11 | 8 | 3 |
| 29 | `BCM_RearMacWiper` | 11 | 7 | 4 |
| 30 | `MRSeatHeatVentCtrlApp` | 10 | 10 | 0 |
| 31 | `BCM_BosAdjSwt` | 10 | 8 | 2 |
| 32 | `MRSeatUnlockMotCtrlAPP` | 10 | 10 | 0 |
| 33 | `RoofLampSwitchCtrlAPP` | 10 | 10 | 0 |
| 34 | `RoofLampUnlockCtrlAPP` | 9 | 9 | 0 |
| 35 | `RoofLampPowermodeCtrlAPP` | 9 | 9 | 0 |
| 36 | `BCM_TrunkLamp` | 9 | 5 | 4 |
| 37 | `CrashUnlockApp_Ri` | 9 | 9 | 0 |
| 38 | `EMSPwrOnOffApp` | 9 | 8 | 1 |
| 39 | `BCM_PwrSplyVIUMRAt` | 8 | 4 | 4 |
| 40 | `BCM_BackLi` | 8 | 4 | 4 |
| 41 | `BCM_DoorRels_FR` | 8 | 5 | 3 |
| 42 | `BCM_SeatHeatIndcr_TRR1` | 8 | 5 | 3 |
| 43 | `BCM_RoofLamp` | 8 | 4 | 4 |
| 44 | `BCM_SeatHeatIndcr_TRR3` | 8 | 5 | 3 |
| 45 | `BCM_SeatHeatIndcr_TRR2` | 8 | 5 | 3 |
| 46 | `RoofLampDoorCtrlAPP` | 8 | 8 | 0 |
| 47 | `BackLiCtrlAPP` | 8 | 8 | 0 |
| 48 | `BCM_DoorRels_RR` | 8 | 5 | 3 |
| 49 | `BCM_RoofLampCtrlSrv` | 7 | 5 | 2 |
| 50 | `SavePwrDoorResetApp` | 7 | 7 | 0 |
| 51 | `BCM_SeatUnlockMot_MR` | 7 | 4 | 3 |
| 52 | `TRRSeatHeatVentCtrlApp` | 7 | 7 | 0 |
| 53 | `BCM_DoLiMainSwt` | 6 | 2 | 4 |
| 54 | `BCM_RearDefrost` | 6 | 4 | 2 |
| 55 | `SavePwrCtrlAPP` | 6 | 6 | 0 |
| 56 | `ReverseLampApp` | 6 | 6 | 0 |
| 57 | `TrunkLampTailgateCtrlApp` | 5 | 5 | 0 |
| 58 | `BCM_DoorRelsSwt_FR` | 5 | 3 | 2 |
| 59 | `SavePwrLockResetAPP` | 5 | 5 | 0 |
| 60 | `BCM_CrashSt_Ri` | 5 | 3 | 2 |
| 61 | `BCM_DoorRelsSwt_RR` | 5 | 3 | 2 |
| 62 | `BCM_SBRSwt_TRR` | 5 | 3 | 2 |
| 63 | `BCM_SeatHeatSwt_TRR` | 5 | 3 | 2 |
| 64 | `BCM_SBRSwt_FR` | 5 | 3 | 2 |
| 65 | `SavePwrHazzardLampResetApp` | 4 | 4 | 0 |
| 66 | `SavePwrBrkLiResetAPP` | 4 | 4 | 0 |
| 67 | `BCM_SeatAdjSwt_ThirdRi` | 4 | 2 | 2 |
| 68 | `BCM_SeatAdjSwt_TrunkLe` | 4 | 2 | 2 |
| 69 | `BCM_SeatAdjSwt_TrunkRi` | 4 | 2 | 2 |
| 70 | `BCM_SeatAdjSwt_FrntRi` | 4 | 2 | 2 |
| 71 | `BCM_SeatUnlockSwt_MR` | 4 | 2 | 2 |
| 72 | `RoofLampAntCtrlAPP` | 4 | 4 | 0 |

---

### 结论
- **72 个 SWC** 需要为其端口添加 `PORT-API-OPTION`（具体位于各 SWC 的 `SWC-INTERNAL-BEHAVIOR` 内部）。
- 配置内容**几乎统一**为 `<ENABLE-TAKE-ADDRESS>true</ENABLE-TAKE-ADDRESS>`。
- 配置集中在**车身控制相关 SWC**（座椅、车门、车灯、后视镜、雨刮等）以及少量**热管理/OTA** 模块。