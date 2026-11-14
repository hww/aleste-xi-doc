# Instruction Set Architecture (ISA)

Instructions are 32-bit, fixed-format. The instruction class is determined by field (J, I). Within a class, field `REG_OP` (ALU / CTRL op) determines the operation.

## Instruction Format

The format is fixed; all fields have strict positions. This simplifies decoding: all fields are available combinationally from `insn`.

{{auto:insn_reg}}

{{auto:insn_imm11}}

{{auto:insn_ctrl_jmp}}

{{auto:insn_ctrl_jmpr}}

*Fig. 9. Instruction format.*

## ALU Instructions

ALU instructions (class `00` and `01`) perform logical and arithmetic operations. The result is written to `DST` if `nowrite = 0`. Flags (`Z`, `N`, `C`, `V`) are updated according to `F` and the opcode.

{{auto:alu_ops}}

*Fig. 10. ALU opcode map.*

## CTRL Instructions

CTRL instructions (class `10`) control execution flow. `JMP`, `CALL`, `RET`, `JMPR` change `PC`. `HALT` stops the processor. `IRQ` sets the interrupt flag. `FLUSH` starts a background cache flush.

{{auto:ctrl_ops}}

*Fig. 11. CTRL opcode map.*

## Conditions

Conditions (`COND`) determine whether an instruction executes. If the condition is false, the instruction does not change state (except `PC`).

{{auto:conditions}}

*Fig. 12. Condition code map.*
