### Rev. A: Global Registers

| Offset | Name | R/W | Bits |
| --- | --- | --- | --- |
| 0x00 | GLOBAL_CR | RW | [0] enable; [1] reset |
| 0x01 | GLOBAL_VOL_L | RW | [7:0] global left volume |
| 0x02 | GLOBAL_VOL_R | RW | [7:0] global right volume |
| 0x03 | STATUS | R | [0] global active; [1] any active; [2] any error; [3] any EOF; [4] DMA error; [5] timer IRQ |
| 0x04 | IRQ_CTRL | RW | [0] timer IRQ enable; [1] DMA error NMI enable |
| 0x05 | DMA_ERR_CLR | W | write 1 to clear |
| 0x10 | TIMER_VAL | RW | [7:0] timer value low |
| 0x11 | TIMER_VAL_H | RW | [7:0] timer value high |
| 0x12 | TIMER_CTRL | RW | [7:0] timer control |
