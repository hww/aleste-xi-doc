# Instruction Set Architecture (ISA)

Instructions are 32-bit, fixed-format. The instruction class is determined by field (J, I). Within a class, field `REG_OP` (ALU / CTRL op) determines the operation.

## Instruction Format

The format is fixed; all fields have strict positions. This simplifies decoding: all fields are available combinationally from `insn`.

![INSTRUCTION · 32 BIT](gen/insn.svg)

*Figure 2 — INSTRUCTION · 32 BIT*

**Table 5 — INSTRUCTION · 32 BIT**

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


*Fig. 9. Instruction format.*

## ALU Instructions

ALU instructions (class `00` and `01`) perform logical and arithmetic operations. The result is written to `DST` if `nowrite = 0`. Flags (`Z`, `N`, `C`, `V`) are updated according to `F` and the opcode.

**Table 6 — ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="MOV"></a>**MOV** | cls=00, fn=00, inv=0: d = s |
| 1 | <a id="MVN"></a>**MVN** | cls=00, fn=00, inv=1: d = ~s |
| 2 | <a id="AND"></a>**AND** | cls=00, fn=01, inv=0: d = d & s |
| 3 | <a id="BIC"></a>**BIC** | cls=00, fn=01, inv=1: d = d & ~s |
| 4 | <a id="OR"></a>**OR** | cls=00, fn=10, inv=0: d = d \| s |
| 5 | <a id="ORN"></a>**ORN** | cls=00, fn=10, inv=1: d = d \| ~s |
| 6 | <a id="XOR"></a>**XOR** | cls=00, fn=11, inv=0: d = d ^ s |
| 7 | <a id="XNOR"></a>**XNOR** | cls=00, fn=11, inv=1: d = d ^ ~s |
| 8 | <a id="ADD"></a>**ADD** | cls=01, fn=00, cin=0: d = d + s |
| 9 | <a id="ADC"></a>**ADC** | cls=01, fn=00, cin=C: d = d + s + C |
| 10 | <a id="SUB"></a>**SUB** | cls=01, fn=01, cin=1: d = d - s; C = not borrow |
| 11 | <a id="SBC"></a>**SBC** | cls=01, fn=01, cin=C: d = d - s - (1-C) |
| 12 | <a id="ROR"></a>**ROR** | cls=10, fn=00: 16-bit rotate right by s[3:0] |
| 13 | <a id="reserved"></a>**reserved** | cls=10, fn=00, op[0]=1 — reserved |
| 14 | <a id="SHR"></a>**SHR** | cls=10, fn=01: ROR with zero fill |
| 15 | <a id="reserved"></a>**reserved** | cls=10, fn=01, op[0]=1 — reserved |
| 16 | <a id="SAR"></a>**SAR** | cls=10, fn=10: ROR with bit 15 fill (arithmetic) |
| 17 | <a id="reserved"></a>**reserved** | cls=10, fn=10, op[0]=1 — reserved |
| 18..23 | <a id="reserved"></a>**reserved** | cls=10, fn=11 and others — reserved |
| 24 | <a id="MUL"></a>**MUL** | cls=11, fn=00: d = (d * s)[15:0] signed; high 16 to MHI |
| 25..27 | <a id="reserved"></a>**reserved** | cls=11, fn=00, op[0]=1 or fn=01 — reserved |
| 28 | <a id="TST"></a>**TST** | cls=11, fn=10: d & s, result discarded, flags written |
| 29 | <a id="reserved"></a>**reserved** | cls=11, fn=10, op[0]=1 — reserved |
| 30 | <a id="CMP"></a>**CMP** | cls=11, fn=11: d - s, result discarded, flags written |
| 31 | <a id="reserved"></a>**reserved** | cls=11, fn=11, op[0]=1 — reserved |

**Notes:**

- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.


*Fig. 10. ALU opcode map.*

## CTRL Instructions

CTRL instructions (class `10`) control execution flow. `JMP`, `CALL`, `RET`, `JMPR` change `PC`. `HALT` stops the processor. `IRQ` sets the interrupt flag. `FLUSH` starts a background cache flush.

**Table 7 — CTRL OP (J=1, I=0)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="NOP"></a>**NOP** | Nothing |
| 1 | <a id="JMP"></a>**JMP** | PC = ADDR |
| 2 | <a id="CALL"></a>**CALL** | SHADOW[15:12] = flags, SHADOW[11:0] = PC+1; PC = ADDR |
| 3 | <a id="RET"></a>**RET** | PC = SHADOW[11:0]; flags not restored |
| 4 | <a id="JMPR"></a>**JMPR** | PC = operand[REG][11:0] |
| 5 | <a id="HALT"></a>**HALT** | ADDR=0 -> IDLE; ADDR!=0 -> ERROR(code) |
| 6 | <a id="IRQ"></a>**IRQ** | Raise IRQ, code = ADDR |
| 7 | <a id="FLUSH"></a>**FLUSH** | Flush cache channel imm12[1:0] |


*Fig. 11. CTRL opcode map.*

## Conditions

Conditions (`COND`) determine whether an instruction executes. If the condition is false, the instruction does not change state (except `PC`).

**Table 8 — COND (4 bits, ARM-style)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="AL"></a>**AL** | Always |
| 1 | <a id="EQ"></a>**EQ** | Z=1 |
| 2 | <a id="NE"></a>**NE** | Z=0 |
| 3 | <a id="CS"></a>**CS** | C=1 (unsigned >=) |
| 4 | <a id="CC"></a>**CC** | C=0 (unsigned <) |
| 5 | <a id="MI"></a>**MI** | N=1 |
| 6 | <a id="PL"></a>**PL** | N=0 |
| 7 | <a id="VS"></a>**VS** | V=1 |
| 8 | <a id="VC"></a>**VC** | V=0 |
| 9 | <a id="HI"></a>**HI** | C=1 and Z=0 |
| 10 | <a id="LS"></a>**LS** | C=0 or Z=1 |
| 11 | <a id="GE"></a>**GE** | N=V |
| 12 | <a id="LT"></a>**LT** | N!=V |
| 13 | <a id="GT"></a>**GT** | Z=0 and N=V |
| 14 | <a id="LE"></a>**LE** | Z=1 or N!=V |
| 15 | <a id="NV"></a>**NV** | Never (default=false) |


*Fig. 12. Condition code map.*
