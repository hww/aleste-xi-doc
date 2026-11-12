**Device map — devices accessible via LDX/STX/WAIT_FLAG (REG_ADDR 0..31)**

| Code | Name | Description |
| --- | --- | --- |
| 0 | ZERO | Constant 0 |
| 1 | A | Stack register A |
| 2 | B | Stack register B |
| 3 | C | Stack register C |
| 4 | SPIX | Source pixel (via PACKER_RD CH_SOURCE) |
| 5 | DPIX | Destination pixel (via PACKER_RD/WR CH_DEST) |
| 6 | SIDX | Source index |
| 7 | DIDX | Destination index |
| 8 | DPTR | Data stream pointer |
| 9 | FLAG | Flags Z, N, C |
| 10 | CNT | Loop counter |
| 11 | FLAG_BUSY | 1 if busy (model: always 0) |
| 12 | FLAG_IRQ | 1 if irq_pending_ |
| 13 | FLAG_DMA | Stub, 0 |
| 14 | FLAG_CNT_ZERO | 1 if loop_cnt_ == 0 |
| 15 | FLAG_BUSY_NOT | Inverse of FLAG_BUSY |
| 16 | FLAG_IRQ_NOT | Inverse of FLAG_IRQ |
| 17 | FLAG_DMA_NOT | Inverse of FLAG_DMA |
| 18 | FLAG_CNT_ZERO_NOT | Inverse of FLAG_CNT_ZERO |
| 19..31 | reserved | — |

**Примечания:**

- R0..R31 are addressed separately via LDR/STR (REG_ADDR 0..31).
- LDX/STX/WAIT_FLAG use REG_ADDR as a device number (0..31).
- SPIX/DPIX are accessed through PACKER_RD/WR, not LDX/STX.
- Flag inverses are separate devices (FLAG_*_NOT), no inversion bit.
