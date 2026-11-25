**ALU_CTL (16 bits, PEN bank group 2)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSVD"></a>**RSVD** | [15] | 1 | reserved (0) |
| <a id="DPAR"></a>**DPAR** | [14] | 1 | screen-door parity: write only if (XI^YI)[0] == DPAR (pre-advance integer parts) |
| <a id="DEN"></a>**DEN** | [13] | 1 | screen-door gating enable |
| <a id="REL"></a>**REL** | [12:10] | 3 | write condition on CS pair, unsigned: 0=always, 1===, 2=!=, 3=<, 4=>=, 5=>, 6=<=, 7=never |
| <a id="CS"></a>**CS** | [9:8] | 2 | compare pair (first ? second): 0=A?K, 1=D?K, 2=A?D, 3=D?B |
| <a id="SY"></a>**SY** | [7:6] | 2 | Y source: 0=A, 1=B, 2=D, 3=K |
| <a id="SX"></a>**SX** | [5:4] | 2 | X source: 0=A, 1=B, 2=D, 3=K |
| <a id="OP"></a>**OP** | [3:0] | 4 | ALU operation (see v2_pixel_alu_ops) |

**Notes:**

- Reset 0x0000 => OP=PASS, SX=A, REL=always, DEN=0: copy-A default.
- NEED_D = (SX==D) | (SY==D) | (REL in 1..6 & CS != 0). If 0 and W=16: one cache access, no RMW.
- All operands are unsigned W-bit values (W by FMT: 16/8/4/2/1; LO8/HI8 = 8); datapath 16 bits wide, bits above W forced to 0.
