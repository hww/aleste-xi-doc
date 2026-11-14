# INSTRUCTION · 32 BIT

All microinstruction formats. J and I select the format.

![INSTRUCTION · 32 BIT](gen/insn.svg)

| Format | Selector | Description |
| --- | --- | --- |
| <a id="reg-reg"></a>**REG-REG** | `J=0 I=0` | d = d op s |
| <a id="reg-imm12"></a>**REG-IMM12** | `J=1 I=1` | d = d op imm |
| <a id="ldi24"></a>**LDI24** | `J=0 I=1` | R[DST] = imm24; unconditional, flags untouched |
| <a id="control"></a>**CONTROL** | `J=1 I=0` | — |

**REG-REG** (`J=0 I=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | — | DST bank: 0 = R0..R31, 1 = special operand |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | Condition; false = no register write, no port access [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | 1 = update flags |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | ALU operation [`alu_ops`](gen/alu_ops.md) |
| <a id="SRC"></a>**SRC** | [12:7] | 6 | — | Second operand {S, n[4:0]} [`operand_map`](gen/operand_map.md) |
| <a id="RSV"></a>**RSV** | [6:0] | 7 | — | Reserved, must be 0 |

**REG-IMM12** (`J=1 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Destination operand, low 5 bits |
| <a id="DS"></a>**DS** | [23] | 1 | — | — |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | — |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | [`alu_ops`](gen/alu_ops.md) |
| <a id="SX"></a>**SX** | [12] | 1 | — | 1 = sign-extend IMM, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [11:0] | 12 | — | 12-bit immediate, operand B |

**LDI24** (`J=0 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | R0..R31 only |
| <a id="IMM24"></a>**IMM24** | [23:0] | 24 | — | 24-bit constant |

**CONTROL** (`J=1 I=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="DST"></a>**DST** | [28:24] | 5 | — | Unused |
| <a id="DS"></a>**DS** | [23] | 1 | — | Unused |
| <a id="COND"></a>**COND** | [22:19] | 4 | — | [`conditions`](gen/conditions.md) |
| <a id="F"></a>**F** | [18] | 1 | — | Unused |
| <a id="OP"></a>**OP** | [17:13] | 5 | — | [`ctrl_ops`](gen/ctrl_ops.md) |
| <a id="REG"></a>**REG** | [12:7] | 6 | — | Operand for JMPR (any operand, including special) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | — | Target address (JMP/CALL), halt code (HALT), IRQ code (IRQ) |

**Notes:**

- L bit: after the word, if count > 1 then count--, PC = loop target; else fall through. Runs even if COND is false.
