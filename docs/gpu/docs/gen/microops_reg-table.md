**REG_OP — Стек A/B/C и данные (5 бит, 32 кода)**

| Code | Name | Description | Cycles | Imm |
| --- | --- | --- | --- | --- |
| 0 | NOP | — | 1 | — |
| 1 | LDR | A = R[REG_ADDR] | 1 | — |
| 2 | LDR_PUSH | push; A = R[REG_ADDR] | 1 | — |
| 3 | STR | R[REG_ADDR] = A (без снятия) | 1 | — |
| 4 | STR_POP | R[REG_ADDR] = A; pop | 1 | — |
| 5 | CLR_A | A = 0 | 1 | — |
| 6 | CLR_AB | A = 0; B = 0 | 1 | — |
| 7 | CLR_C | C = 0 | 1 | — |
| 8 | LDD | A = mem.read16(DPTR); DPTR += 2 | 1 | — |
| 9 | LDD_PUSH | push; LDD | 1 | — |
| 10 | LDDS | A = (int16)mem.read16(DPTR); DPTR += 2 | 1 | — |
| 11 | LDDS_PUSH | push; LDDS | 1 | — |
| 12 | SETS | SIDX = A | 1 | — |
| 13 | SETD | DIDX = A | 1 | — |
| 14 | SETP | DPTR = A | 1 | — |
| 15 | LDCNT | loop_cnt_ = A | 1 | — |
| 16 | FLUSH | Сбросить dirty всех каналов | зависит | — |
| 17 | LDX | A = device[REG_ADDR] | 1 | — |
| 18 | LDX_PUSH | push; LDX | 1 | — |
| 19 | STX | device[REG_ADDR] = A (без снятия) | 1 | — |
| 20 | STX_POP | STX; pop | 1 | — |
| 21 | LDI | A = sign_extend(IMM) | 1 | константа[11:0] |
| 22 | LDI_PUSH | push; LDI | 1 | константа[11:0] |
| 23 | LDH | A[23:12] = IMM (младшие 12 не трогает) | 1 | константа[11:0] |
| 24 | LDL | A[11:0] = IMM (старшие 12 не трогает) | 1 | константа[11:0] |
| 25 | PACKER_RD | A = пиксель/слово (ADDR_ или DPTR для CH_DATA) | 1 | — |
| 26 | PACKER_RD_PUSH | push; PACKER_RD | 1 | — |
| 27 | PACKER_WR | пиксель/слово = A | 1 | — |
| 28 | PACKER_WR_POP | PACKER_WR; pop | 1 | — |
| 29 | SETMODE | ch_mode_[REG_ADDR[1:0]].fmt = A[2:0] | 1 | — |
| 30 | SETPAGE | set_page(REG_ADDR[1:0], A) | зависит | — |
| 31 | ADDR | ADDR ch=REG_ADDR[1:0]: A=(y<<12)|x → ADDR_ = addr24, pos | 1 | — |
| 32 | IRQ | irq_pending_=1, irq_code_=A[11:0] | 1 | — |

**Примечания:**

- LDR/STR — регистры R0..R31 (REG_ADDR 0..31).
- LDX/STX — устройства (DeviceMap 0..31).
- PACKER_RD/WR — пиксели через ADDR_ (AddrPacker), CH_DATA — через DPTR.
- LDH/LDL — сборка 24-битного адреса: LDL (младшие 12), LDH (старшие 12).
