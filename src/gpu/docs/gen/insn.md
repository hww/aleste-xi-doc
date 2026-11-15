**INSTRUCTION · 32 BIT**

| Format | Selector | Description |
| --- | --- | --- |
| <a id="reg-reg"></a>**REG-REG** | `J=0 I=0` | — |
| <a id="reg-imm11"></a>**REG-IMM11** | `J=1 I=1` | — |
| <a id="ldi16"></a>**LDI16** | `J=0 I=1` | — |
| <a id="control"></a>**CONTROL** | `J=1 I=0 R=0` | — |
| <a id="control_rjump"></a>**CONTROL RJUMP** | `J=1 I=0 R=1` | — |

**REG-REG** (`J=0 I=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="COND"></a>**COND** | [28:25] | 4 | — | [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | — | 1 = write result; 0 = do not write, disables only write back |
| <a id="F"></a>**F** | [23] | 1 | — | 1 = update flags |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | — | Destination operand (6 bits) |
| <a id="ALU_OP"></a>**ALU_OP** | [16:12] | 5 | — | [`alu_ops`](alu_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | — | [`operand_map`](operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | — | Reserved |

**REG-IMM11** (`J=1 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="COND"></a>**COND** | [28:25] | 4 | — | [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | — | 1 = write result; 0 = do not write, disables only write back |
| <a id="F"></a>**F** | [23] | 1 | — | 1 = update flags |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | — | Destination operand (6 bits) |
| <a id="ALUOP"></a>**ALUOP** | [16:12] | 5 | — | [`alu_ops`](alu_ops.md) |
| <a id="SX"></a>**SX** | [11] | 1 | — | 1 = sign-extend, 0 = zero-extend |
| <a id="IMM"></a>**IMM** | [10:0] | 11 | — | 11-bit immediate |

**LDI16** (`J=0 I=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 0 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 1 | Format selector, low |
| <a id="COND"></a>**COND** | [28:25] | 4 | — | [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | — | Unused for LDI, must be 1 |
| <a id="F"></a>**F** | [23] | 1 | — | Unused for LDI, must be 0 |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | — | Destination operand (6 bits) |
| <a id="RSV"></a>**RSV** | [16] | 1 | — | Reserved |
| <a id="IMM16"></a>**IMM16** | [15:0] | 16 | — | 16-bit constant |

**CONTROL** (`J=1 I=0 R=0`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="COND"></a>**COND** | [28:25] | 4 | — | [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | — | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | — | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | — | Destination operand (6 bits) |
| <a id="R"></a>**R** | [16] | 1 | 0 | Jump/Call by register |
| <a id="CTRL_OP"></a>**CTRL_OP** | [15:12] | 4 | — | [`ctrl_ops`](ctrl_ops.md) |
| <a id="ADDR"></a>**ADDR** | [11:0] | 12 | — | Target address (JMP/CALL), halt/IRQ code, channel (FLUSH) |

**CONTROL RJUMP** (`J=1 I=0 R=1`)

| Field | Bits | Width | Fixed | Description |
| --- | --- | --- | --- | --- |
| <a id="L"></a>**L** | [31] | 1 | — | Loop flag |
| <a id="J"></a>**J** | [30] | 1 | 1 | Format selector, high |
| <a id="I"></a>**I** | [29] | 1 | 0 | Format selector, low |
| <a id="COND"></a>**COND** | [28:25] | 4 | — | [`conditions`](conditions.md) |
| <a id="WRITE"></a>**WRITE** | [24] | 1 | — | Unused for CTRL, must be 0 |
| <a id="F"></a>**F** | [23] | 1 | — | Unused for CTRL (must be 0) |
| <a id="DST_CODE"></a>**DST_CODE** | [22:17] | 6 | — | Destination operand (6 bits) |
| <a id="R"></a>**R** | [16] | 1 | 1 | Jump/Call 0-by immediate, 1-by src register |
| <a id="CTRLOP"></a>**CTRLOP** | [15:12] | 4 | — | [`ctrl_ops`](ctrl_ops.md) |
| <a id="SRC"></a>**SRC** | [11:6] | 6 | — | [`operand_map`](operand_map.md) |
| <a id="RSV"></a>**RSV** | [5:0] | 6 | — | Reserved |
