# UART registers

![UART registers](gen/uart.svg)

| Offset | Name | Access | Reset | Description |
| --- | --- | --- | --- | --- |
| `0x00` | <a id="DATA"></a>**DATA** | rw | — | Data |
| `0x04` | <a id="STATUS"></a>**STATUS** | ro | — | Status |
| `0x08` | <a id="BAUD"></a>**BAUD** | rw | 0x01B2 | Baud divisor |

**DATA** (`0x00`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [15:8] | 8 | Reserved |
| <a id="D"></a>**D** | [7:0] | 8 | — |

**STATUS** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [15:4] | 12 | Reserved |
| <a id="ERR"></a>**ERR** | [3:2] | 2 | — |
| <a id="RXF"></a>**RXF** | [1] | 1 | — |
| <a id="TXE"></a>**TXE** | [0] | 1 | — |

**BAUD** (`0x08`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="DIV"></a>**DIV** | [15:0] | 16 | — |
