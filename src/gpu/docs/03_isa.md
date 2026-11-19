# Instruction Set Architecture (ISA)

Instructions are 32-bit, fixed-format. The instruction class is determined by field (J, I). Within a class, field `REG_OP` (ALU / CTRL op) determines the operation.

## Instruction Format

The format is fixed; all fields have strict positions. This simplifies decoding: all fields are available combinationally from `insn`.

{{auto:insn}}

## Instruction Kinds

{{auto:insn_reg}}

{{auto:insn_imm11}}

{{auto:insn_ctrl_jmp}}

{{auto:insn_ctrl_jmpr}}

*Fig. 9. Instruction format.*

## ALU Instructions

ALU instructions (formats reg-reg, LDI16 and reg-imm11; control class excluded) perform logical, arithmetic, shift and multiply operations. The result is written to `DST` if `WRITE = 1` (bit `[24]`; LDI16 always writes). Flags (`Z`, `N`, `C`, `V`) are updated according to `F` and the opcode.

{{auto:alu_ops}}

*Fig. 10. ALU opcode map.*

## CTRL Instructions

CTRL instructions (class `10`) control execution flow. `JMP`, `CALL`, `RET` change `PC`; `JMPR` is the register-indirect form of `JMP` (`REG = 1`). `HALT` stops the processor. `IRQ` raises an interrupt event with an 8-bit code. `FLUSH` writes back one selected channel and stalls the sequencer until the flush completes (not a background operation).

{{auto:ctrl_ops}}

*Fig. 11. CTRL opcode map.*

## Conditions

Conditions (`COND`) determine whether an instruction executes. If the condition is false, the instruction does not change state: no register write, no port access, no flag update. The hardware loop update (`L` bit) still runs, so `PC` and `LOOP_CNT` can change on a false-condition word.

{{auto:conditions}}

*Fig. 12. Condition code map.*