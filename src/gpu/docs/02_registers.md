# Register Map

There are 64 operand slots (6 bits) in total. Slots 0..31 are general-purpose registers (R0..R31), 32..41 are system registers, 42..43 are reserved, 44..47 are DATA[0..3], 48..63 are pixel engine channels.

## General-Purpose Registers

Registers R0..R31 serve as source and destination in most instructions. R0 is a normal register; the constant zero comes from the ZERO operand (`32`).

{{auto:registers}}

*Fig. 5. GPRs (6-bit operand field).*

A read takes one cycle (`q_a <= mem[ra]` on `posedge clk`), a write takes one cycle (`mem[wa] <= wdata`). Read-after-write in the same cycle is covered by bypass: `rdata_a = wdata_r` when `we && (wa == ra)`, so the new value is visible without waiting for the write to land.

{{auto:timing_regfile}}

## System Registers

System registers (32..41, 42..43 reserved) are available as a source in any instruction, and as a destination only in `MOV`. They provide access to flags, channel status, CALL/RET shadow, loop counter, ROM access, and the MUL high half.

{{auto:sysregs}}

*Fig. 6. System registers.*
