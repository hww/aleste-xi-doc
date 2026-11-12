**R20 — Address Mode (0x14)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **RESERVED** | [7:7] | 1 | Reserved |
| **addr_mode** | [6:4] | 3 | 000=CPC 16KB, 001=EX 32KB, 010=LX 32KB, 011=LX 64KB, 100=Linear |
| **RESERVED** | [3:3] | 1 | Reserved |
| **address_rate** | [2:2] | 1 | 1=two increments per char |
| **address_step** | [1:1] | 1 | 0=increment by 2, 1=increment by 4 |
| **linear_mode** | [0:0] | 1 | 0=CPC-style legacy, 1=linear counter |
