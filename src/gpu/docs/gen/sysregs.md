**System Registers (32..41, 42..43 reserved)**

| Value | Name | Description |
| --- | --- | --- |
| 32 | <a id="ZERO"></a>**ZERO** | Constant zero |
| 33 | <a id="FLAGS"></a>**FLAGS** | Flags V, C, N, Z (see flags_bitfield) |
| 34 | <a id="BUSY"></a>**BUSY** | Channel status (see busy_bitfield) |
| 35 | <a id="SHADOW"></a>**SHADOW** | CALL/RET return address and flags (see shadow_bitfield) |
| 36 | <a id="LOOP_CNT"></a>**LOOP_CNT** | Loop counter |
| 37 | <a id="LOOP_TGT"></a>**LOOP_TGT** | Loop target |
| 38 | <a id="ROML"></a>**ROML** | ROM access, low 16 bits |
| 39 | <a id="ROMH"></a>**ROMH** | ROM access, high 16 bits (a read or a write increments ROMA) |
| 40 | <a id="ROMA"></a>**ROMA** | ROM access address (write only) |
| 41 | <a id="MHI"></a>**MHI** | Upper 16 bits of MUL |
