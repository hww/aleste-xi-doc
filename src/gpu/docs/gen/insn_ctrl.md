# INSTRUCTION · 32 BIT · J=1 I=0 CONTROL

![INSTRUCTION · 32 BIT · J=1 I=0 CONTROL](gen/insn_ctrl.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | = 1 |
| <a id="I"></a>**I** | [29] | 1 | = 0 |
| <a id="DST"></a>**DST** | [28:24] | 5 | Unused |
| <a id="DS"></a>**DS** | [23] | 1 | Unused |
| <a id="COND"></a>**COND** | [22:19] | 4 | Condition [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | Unused |
| <a id="OP"></a>**OP** | [17:13] | 5 | Control operation [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="REG"></a>**REG** | [12:7] | 6 | Operand for JMPR (any operand, including special) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | Target address (JMP/CALL), halt code (HALT), IRQ code (IRQ) |
