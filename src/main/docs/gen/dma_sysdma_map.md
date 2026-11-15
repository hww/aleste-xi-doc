**SysDMA Register Map (wb_dma.sv)**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="SRC_ADDR_ch_"></a>**SRC_ADDR[ch]** | — |
| `0x10` | <a id="DST_ADDR_ch_"></a>**DST_ADDR[ch]** | — |
| `0x20` | <a id="COUNT_ch_"></a>**COUNT[ch]** | — |
| `0x30` | <a id="CONTROL_ch_"></a>**CONTROL[ch]** | — |
| `0x31` | <a id="STATUS_ch_"></a>**STATUS[ch]** | — |
| `0x40` | <a id="IMASK"></a>**IMASK** | — |
| `0x41` | <a id="DONE_CLEAR"></a>**DONE_CLEAR** | — |
| `0x42` | <a id="ERROR_CLEAR"></a>**ERROR_CLEAR** | — |
| `0x43` | <a id="VERSION"></a>**VERSION** | — |

**SRC_ADDR[ch]** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Source address (24 bits) |

**DST_ADDR[ch]** (`0x10`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="ADDR"></a>**ADDR** | [7:0] | 8 | Destination address (24 bits) |

**COUNT[ch]** (`0x20`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="COUNT"></a>**COUNT** | [7:0] | 8 | Transfer count (24 bits) |

**CONTROL[ch]** (`0x30`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:6] | 2 | Reserved |
| <a id="MODE"></a>**MODE** | [5] | 1 | 0=Demand, 1=Block |
| <a id="ENABLE"></a>**ENABLE** | [4] | 1 | Enable channel |
| <a id="DST_CTRL"></a>**DST_CTRL** | [3:2] | 2 | Dest control |
| <a id="SRC_CTRL"></a>**SRC_CTRL** | [1:0] | 2 | Source control |

**STATUS[ch]** (`0x31`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:2] | 6 | Reserved |
| <a id="ERROR"></a>**ERROR** | [1] | 1 | Transfer error |
| <a id="DONE"></a>**DONE** | [0] | 1 | Transfer done |

**IMASK** (`0x40`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="MASK"></a>**MASK** | [3:0] | 4 | Interrupt mask per channel |

**DONE_CLEAR** (`0x41`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="CLR"></a>**CLR** | [3:0] | 4 | Clear DONE flags |

**ERROR_CLEAR** (`0x42`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="CLR"></a>**CLR** | [3:0] | 4 | Clear ERROR flags |

**VERSION** (`0x43`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="VER"></a>**VER** | [7:0] | 8 | Version / features |
