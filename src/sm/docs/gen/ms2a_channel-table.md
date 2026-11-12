### Rev. A: Channel Registers (Base 0x20, 0x30, 0x40, 0x50)

| Offset | Name | R/W | Bits |
| --- | --- | --- | --- |
| +0 | CH_CTRL | RW | [0] enable; [1] loop; [2] ping-pong; [3] IRQ on EOF; [7:4] vol L; [3:0] vol R |
| +1 | START_ADDR_0 | RW | [7:0] |
| +2 | START_ADDR_1 | RW | [15:8] |
| +3 | START_ADDR_2 | RW | [23:16] |
| +4 | END_ADDR_0 | RW | [7:0] |
| +5 | END_ADDR_1 | RW | [15:8] |
| +6 | END_ADDR_2 | RW | [23:16] |
| +7 | LOOP_START_0 | RW | [7:0] |
| +8 | LOOP_START_1 | RW | [15:8] |
| +9 | LOOP_START_2 | RW | [23:16] |
| +A | LOOP_END_0 | RW | [7:0] |
| +B | LOOP_END_1 | RW | [15:8] |
| +C | LOOP_END_2 | RW | [23:16] |
| +D | STEP_0 | RW | [7:0] |
| +E | STEP_1 | RW | [15:8] |
| +F | STEP_2 | RW | [23:16] |
