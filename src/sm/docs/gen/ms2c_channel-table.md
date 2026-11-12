### Rev. C: Channel Registers (Base 0x20, 0x30, 0x40, 0x50)

| Offset | Name | R/W | Bits |
| --- | --- | --- | --- |
| +0 | CTRL | RW | [0] play; [1] loop; [2] 16-bit samples; [3] IRQ on EOF |
| +1 | START_0 | RW | [7:0] |
| +2 | START_1 | RW | [15:8] |
| +3 | START_2 | RW | [23:16] (applies) |
| +4 | END_0 | RW | [7:0] |
| +5 | END_1 | RW | [15:8] |
| +6 | END_2 | RW | [23:16] (applies) |
| +7 | LOOP_0 | RW | [7:0] |
| +8 | LOOP_1 | RW | [15:8] |
| +9 | LOOP_2 | RW | [23:16] (applies) |
| +A | VOL_L | RW | [7:0] channel left volume |
| +B | VOL_R | RW | [7:0] channel right volume |
| +C | STEP_0 | RW | [7:0] (fraction) |
| +D | STEP_1 | RW | [15:8] (fraction) |
| +E | STEP_2 | RW | [23:16] (integer) |
| +F | status | R | [0] playing; [1] EOF; [7:4] position |
