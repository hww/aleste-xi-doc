**GPU Interface**

| Offset | Name | Description |
| --- | --- | --- |
| `0x00` | <a id="GPU_ADDR0"></a>**GPU_ADDR0** | A[7:0] Address of GPU program in memory |
| `0x01` | <a id="GPU_ADDR1"></a>**GPU_ADDR1** | A[15:8] Address of GPU program in memory |
| `0x02` | <a id="GPU_ADDR2"></a>**GPU_ADDR2** | A[23:16] Address of GPU program in memory |
| `0x03` | <a id="COMMAND"></a>**COMMAND** | — |
| `0x04` | <a id="STATUS"></a>**STATUS** | — |
| `0x05` | <a id="IRQ_CODE"></a>**IRQ_CODE** | Read-only: 8-bit code of the last IRQ instruction; reading auto-acknowledges the interrupt |

**COMMAND** (`0x03`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:2] | 6 | Reserved |
| <a id="GPU_COMMAND"></a>**GPU_COMMAND** | [1:0] | 2 | GPU command |

**STATUS** (`0x04`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="GPU_HALT"></a>**GPU_HALT** | [7] | 1 | 1 = GPU is in HALT state (idle or stopped on error) |
| <a id="GPU_RESULT"></a>**GPU_RESULT** | [6:0] | 7 | Result / error code (HALT argument or hardware fault code) |
