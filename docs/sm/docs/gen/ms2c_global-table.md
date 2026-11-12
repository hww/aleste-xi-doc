### Rev. C: Global Registers

| Offset | Name | R/W | Bits |
| --- | --- | --- | --- |
| 0x00 | CTRL | RW | [0] enable MS2 |
| 0x01 | VOL_L | RW | [7:0] global left volume |
| 0x02 | VOL_R | RW | [7:0] global right volume |
| 0x03 | STATUS | R | [3:0] EOF per channel; [7:4] playing per channel |
| 0x03 | STATUS (write) | W | [3:0] 1 = clear EOF |
| 0x04 | IRQ_CTRL | RW | [0] EOF IRQ enable; [1] timer IRQ enable |
| 0x05 | IRQ_STAT | R | [0] EOF pending; [1] timer pending |
| 0x05 | IRQ_STAT (write) | W | [1:0] 1 = clear |
| 0x10 | TIMER_LO | RW | [7:0] timer period low |
| 0x11 | TIMER_HI | RW | [15:8] timer period high |
