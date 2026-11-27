**System Timer Port Map (lx_sys.sv)**

| Offset | Name | Access | Description |
| --- | --- | --- | --- |
| `0xF4` | <a id="RT_LO___CMP_LO"></a>**RT_LO / CMP_LO** | rw | — |
| `0xF5` | <a id="RT_HI___CMP_HI"></a>**RT_HI / CMP_HI** | rw | — |
| `0xF6` | <a id="STATUS___CONTROL"></a>**STATUS / CONTROL** | rw | — |

**RT_LO / CMP_LO** (`0xF4`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RT_LO"></a>**RT_LO** | [7:0] | 8 | R: low byte of RT_SNAPSHOT; latches the full 16-bit RT |
| <a id="CMP_LO"></a>**CMP_LO** | [7:0] | 8 | W: buffer low byte of COMPARE (supervisor only) |

**RT_HI / CMP_HI** (`0xF5`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RT_HI"></a>**RT_HI** | [7:0] | 8 | R: high byte of RT_SNAPSHOT |
| <a id="CMP_HI"></a>**CMP_HI** | [7:0] | 8 | W: commit high byte; full 16-bit COMPARE is written atomically (supervisor only) |

**STATUS / CONTROL** (`0xF6`)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:4] | 4 | Reserved |
| <a id="DUE"></a>**DUE** | [3] | 1 | R: live comparator output (ARMED & ~delta[15]). W: ignored |
| <a id="WINDOW"></a>**WINDOW** | [2] | 1 | R: two-byte access window is open (blocks INT, not NMI). W: ignored |
| <a id="ARMED"></a>**ARMED** | [1] | 1 | R: target timestamp has been committed. W: ignored |
| <a id="ENABLE"></a>**ENABLE** | [0] | 1 | R: comparison enabled. W: 1 = enable, 0 = disable (supervisor only) |
