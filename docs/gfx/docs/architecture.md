# LX-GPU — описание архитектуры

## Extended Native Registers (R18–R21)

![Extended Native Registers (R18–R21)](gen/crtc_ext_regmap.svg)

*Figure 8 — Extended Native Registers (R18–R21)*

**Table 8 — Extended Native Registers (R18–R21)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x12` | <a id="R18__Video_Ctrl"></a>**R18: Video Ctrl** | — |
| `0x13` | <a id="R19__High_Addr"></a>**R19: High Addr** | — |
| `0x14` | <a id="R20__Addr_Mode"></a>**R20: Addr Mode** | — |
| `0x15` | <a id="R21__Pixel_Ctrl"></a>**R21: Pixel Ctrl** | — |

**R18: Video Ctrl** (`0x12`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:6] | 2 | Reserved |
| <a id="use_cpc_modes"></a>**use_cpc_modes** | [5] | 1 | 1=use CPC Gate Array bpp |
| <a id="linear_pixel"></a>**linear_pixel** | [4] | 1 | 0=CPC palette, 1=Linear RGB |
| <a id="bpp_mode"></a>**bpp_mode** | [1:0] | 2 | 00=1bpp, 01=2bpp, 10=4bpp, 11=8bpp |

**R19: High Addr** (`0x13`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="A23_A16"></a>**A23_A16** | [7:0] | 8 | High address byte |

**R20: Addr Mode** (`0x14`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7] | 1 | Reserved |
| <a id="addr_mode"></a>**addr_mode** | [6:4] | 3 | 000=CPC 16KB, 001=EX 32KB, 010=LX 32KB, 011=LX 64KB, 100=Linear |
| <a id="address_rate"></a>**address_rate** | [2] | 1 | 1=two increments per char |
| <a id="address_step"></a>**address_step** | [1] | 1 | 0=increment by 2, 1=increment by 4 |
| <a id="linear_mode"></a>**linear_mode** | [0] | 1 | 0=CPC-style legacy, 1=linear counter |

**R21: Pixel Ctrl** (`0x15`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:2] | 6 | Reserved |
| <a id="pixel_rate"></a>**pixel_rate** | [1:0] | 2 | 00=2B, 01=4B, 10=8B, 11=16B per 16px |


[Таблица](gen/crtc_ext_regmap.md)

## R18 — Video Control (0x12)

![R18 — Video Control (0x12)](gen/crtc_r18.svg)

*Figure 9 — R18 — Video Control (0x12)*

**Table 9 — R18 — Video Control (0x12)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:6] | 2 | Reserved |
| <a id="use_cpc_modes"></a>**use_cpc_modes** | [5] | 1 | 1=use CPC Gate Array bpp |
| <a id="linear_pixel"></a>**linear_pixel** | [4] | 1 | 0=CPC palette, 1=Linear RGB |
| <a id="bpp_mode"></a>**bpp_mode** | [1:0] | 2 | 00=1bpp, 01=2bpp, 10=4bpp, 11=8bpp |


[Таблица](gen/crtc_r18.md)

## R20 — Address Mode (0x14)

![R20 — Address Mode (0x14)](gen/crtc_r20.svg)

*Figure 10 — R20 — Address Mode (0x14)*

**Table 10 — R20 — Address Mode (0x14)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7] | 1 | Reserved |
| <a id="addr_mode"></a>**addr_mode** | [6:4] | 3 | 000=CPC 16KB, 001=EX 32KB, 010=LX 32KB, 011=LX 64KB, 100=Linear |
| <a id="address_rate"></a>**address_rate** | [2] | 1 | 1=two increments per char |
| <a id="address_step"></a>**address_step** | [1] | 1 | 0=increment by 2, 1=increment by 4 |
| <a id="linear_mode"></a>**linear_mode** | [0] | 1 | 0=CPC-style legacy, 1=linear counter |


[Таблица](gen/crtc_r20.md)

## R21 — Pixel Control (0x15)

![R21 — Pixel Control (0x15)](gen/crtc_r21.svg)

*Figure 11 — R21 — Pixel Control (0x15)*

**Table 11 — R21 — Pixel Control (0x15)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:2] | 6 | Reserved |
| <a id="pixel_rate"></a>**pixel_rate** | [1:0] | 2 | 00=2B, 01=4B, 10=8B, 11=16B per 16px |


[Таблица](gen/crtc_r21.md)

## Standard MC6845 Registers (R0–R17)

![Standard MC6845 Registers (R0–R17)](gen/crtc_std_regmap.svg)

*Figure 12 — Standard MC6845 Registers (R0–R17)*

**Table 12 — Standard MC6845 Registers (R0–R17)**

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


[Таблица](gen/crtc_std_regmap.md)

## Pixel Strobe Generation

[Таблица](gen/crtc_table_pixel.md)

## Sync Strobe Generation

[Таблица](gen/crtc_table_sync.md)

## Palette Control Register (0x05)

![Palette Control Register (0x05)](gen/palette_control.svg)

*Figure 13 — Palette Control Register (0x05)*

**Table 13 — Palette Control Register (0x05)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="mod_en"></a>**mod_en** | [7] | 1 | 1=Включить модификацию индекса |
| <a id="mod_type"></a>**mod_type** | [6] | 1 | 0=OR, 1=XOR |
| <a id="auto_inc"></a>**auto_inc** | [5] | 1 | 1=Авто-инкремент индекса |
| <a id="RESERVED"></a>**RESERVED** | [4:2] | 3 | Резерв (должно быть 0) |
| <a id="write_mode"></a>**write_mode** | [1:0] | 2 | 00=12-bit, 01=CPC, 10=MSX, 11=YJK |


[Таблица](gen/palette_control.md)

## Color Modes

[Таблица](gen/palette_modes.md)

## Palette Controller Register Map

![Palette Controller Register Map](gen/palette_regmap.svg)

*Figure 14 — Palette Controller Register Map*

**Table 14 — Palette Controller Register Map**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="Palette_Index"></a>**Palette Index** | — |
| `0x01` | <a id="Palette_Data_Low"></a>**Palette Data Low** | — |
| `0x02` | <a id="Palette_Data_High"></a>**Palette Data High** | — |
| `0x03` | <a id="Border_Color_Low"></a>**Border Color Low** | — |
| `0x04` | <a id="Border_Color_High"></a>**Border Color High** | — |
| `0x05` | <a id="Control_Register"></a>**Control Register** | — |
| `0x06` | <a id="Palette_Modifier"></a>**Palette Modifier** | — |

**Palette Index** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="INDEX"></a>**INDEX** | [7:0] | 8 | Индекс цвета (0-255) |

**Palette Data Low** (`0x01`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="DATA_LO"></a>**DATA_LO** | [7:0] | 8 | Младшие 8 бит цвета |

**Palette Data High** (`0x02`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="DATA_HI"></a>**DATA_HI** | [3:0] | 4 | Старшие 4 бита (только 12-bit) |

**Border Color Low** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="BORD_LO"></a>**BORD_LO** | [7:0] | 8 | Младшие 8 бит цвета бордюра |

**Border Color High** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="BORD_HI"></a>**BORD_HI** | [3:0] | 4 | Старшие 4 бита бордюра |

**Control Register** (`0x05`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="mod_en"></a>**mod_en** | [7] | 1 | 1=Включить модификацию индекса |
| <a id="mod_type"></a>**mod_type** | [6] | 1 | 0=OR, 1=XOR |
| <a id="auto_inc"></a>**auto_inc** | [5] | 1 | 1=Авто-инкремент индекса |
| <a id="RESERVED"></a>**RESERVED** | [4:2] | 3 | Резерв (должно быть 0) |
| <a id="write_mode"></a>**write_mode** | [1:0] | 2 | 00=12-bit, 01=CPC, 10=MSX, 11=YJK |

**Palette Modifier** (`0x06`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="MODIFIER"></a>**MODIFIER** | [7:0] | 8 | Значение для OR/XOR модификации |


[Таблица](gen/palette_regmap.md)
