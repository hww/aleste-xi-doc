**Palette Controller Register Map**

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
