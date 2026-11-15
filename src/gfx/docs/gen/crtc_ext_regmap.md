**Extended Native Registers (R18–R21)**

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
