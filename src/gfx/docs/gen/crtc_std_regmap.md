# Standard MC6845 Registers (R0–R17)

![Standard MC6845 Registers (R0–R17)](gen/crtc_std_regmap.svg)

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="R0__H_Total"></a>**R0: H Total** | — |
| `0x01` | <a id="R1__H_Displayed"></a>**R1: H Displayed** | — |
| `0x02` | <a id="R2__H_Sync_Pos"></a>**R2: H Sync Pos** | — |
| `0x03` | <a id="R3__Sync_Widths"></a>**R3: Sync Widths** | — |
| `0x04` | <a id="R4__V_Total"></a>**R4: V Total** | — |
| `0x05` | <a id="R5__V_Adjust"></a>**R5: V Adjust** | — |
| `0x06` | <a id="R6__V_Displayed"></a>**R6: V Displayed** | — |
| `0x07` | <a id="R7__V_Sync_Pos"></a>**R7: V Sync Pos** | — |
| `0x08` | <a id="R8__Interlace_Skew"></a>**R8: Interlace/Skew** | — |
| `0x09` | <a id="R9__Max_Scan_Line"></a>**R9: Max Scan Line** | — |
| `0x0A` | <a id="R10__Cursor_Start"></a>**R10: Cursor Start** | — |
| `0x0B` | <a id="R11__Cursor_End"></a>**R11: Cursor End** | — |
| `0x0C` | <a id="R12__Start_Addr_H"></a>**R12: Start Addr H** | — |
| `0x0D` | <a id="R13__Start_Addr_L"></a>**R13: Start Addr L** | — |
| `0x0E` | <a id="R14__Cursor_Addr_H"></a>**R14: Cursor Addr H** | — |
| `0x0F` | <a id="R15__Cursor_Addr_L"></a>**R15: Cursor Addr L** | — |
| `0x10` | <a id="R16__Light_Pen_H"></a>**R16: Light Pen H** | — |
| `0x11` | <a id="R17__Light_Pen_L"></a>**R17: Light Pen L** | — |

**R0: H Total** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="H_TOTAL"></a>**H_TOTAL** | [7:0] | 8 | Characters per line - 1 |

**R1: H Displayed** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="H_DISP"></a>**H_DISP** | [7:0] | 8 | Visible characters per line |

**R2: H Sync Pos** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="H_SYNC_POS"></a>**H_SYNC_POS** | [7:0] | 8 | Character position of HSYNC start |

**R3: Sync Widths** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="V_WIDTH"></a>**V_WIDTH** | [7:4] | 4 | Vertical sync width |
| <a id="H_WIDTH"></a>**H_WIDTH** | [3:0] | 4 | Horizontal sync width |

**R4: V Total** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="V_TOTAL"></a>**V_TOTAL** | [6:0] | 7 | Rows per frame - 1 |

**R5: V Adjust** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="V_ADJ"></a>**V_ADJ** | [4:0] | 5 | Not implemented (legacy-compatible) |

**R6: V Displayed** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="V_DISP"></a>**V_DISP** | [6:0] | 7 | Visible rows |

**R7: V Sync Pos** (`0x07`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="V_SYNC_POS"></a>**V_SYNC_POS** | [6:0] | 7 | Row of VSYNC start |

**R8: Interlace/Skew** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="SKEW"></a>**SKEW** | [5:4] | 2 | Skew 0-3 char delays |
| <a id="INTERLACE"></a>**INTERLACE** | [1:0] | 2 | Interlace mode |

**R9: Max Scan Line** (`0x09`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="MAX_SCAN"></a>**MAX_SCAN** | [4:0] | 5 | Raster rows per character - 1 |

**R10: Cursor Start** (`0x0A`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="C_MODE"></a>**C_MODE** | [6:5] | 2 | Blink mode |
| <a id="C_START"></a>**C_START** | [4:0] | 5 | Cursor start scanline |

**R11: Cursor End** (`0x0B`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="C_END"></a>**C_END** | [4:0] | 5 | Cursor bottom scanline |

**R12: Start Addr H** (`0x0C`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_H"></a>**ADDR_H** | [5:0] | 6 | Bits A15:A10 of start address |

**R13: Start Addr L** (`0x0D`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR_L"></a>**ADDR_L** | [7:0] | 8 | Bits A9:A2 of start address |

**R14: Cursor Addr H** (`0x0E`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CUR_H"></a>**CUR_H** | [5:0] | 6 | High cursor address |

**R15: Cursor Addr L** (`0x0F`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="CUR_L"></a>**CUR_L** | [7:0] | 8 | Low cursor address |

**R16: Light Pen H** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="LP_H"></a>**LP_H** | [7:0] | 8 | Not implemented |

**R17: Light Pen L** (`0x11`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="LP_L"></a>**LP_L** | [7:0] | 8 | Not implemented |
