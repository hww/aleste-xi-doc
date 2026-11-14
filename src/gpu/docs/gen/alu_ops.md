# ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="MOV"></a>**MOV** | cls=00, fn=00, inv=0: d = s |
| 1 | <a id="MVN"></a>**MVN** | cls=00, fn=00, inv=1: d = ~s |
| 2 | <a id="AND"></a>**AND** | cls=00, fn=01, inv=0: d = d & s |
| 3 | <a id="BIC"></a>**BIC** | cls=00, fn=01, inv=1: d = d & ~s |
| 4 | <a id="OR"></a>**OR** | cls=00, fn=10, inv=0: d = d \| s |
| 5 | <a id="ORN"></a>**ORN** | cls=00, fn=10, inv=1: d = d \| ~s |
| 6 | <a id="XOR"></a>**XOR** | cls=00, fn=11, inv=0: d = d ^ s |
| 7 | <a id="XNOR"></a>**XNOR** | cls=00, fn=11, inv=1: d = d ^ ~s |
| 8 | <a id="ADD"></a>**ADD** | cls=01, fn=00, cin=0: d = d + s |
| 9 | <a id="ADC"></a>**ADC** | cls=01, fn=00, cin=C: d = d + s + C |
| 10 | <a id="SUB"></a>**SUB** | cls=01, fn=01, cin=1: d = d - s; C = not borrow |
| 11 | <a id="SBC"></a>**SBC** | cls=01, fn=01, cin=C: d = d - s - (1-C) |
| 12 | <a id="ROR"></a>**ROR** | cls=10, fn=00: 16-bit rotate right by s[3:0] |
| 13 | <a id="reserved"></a>**reserved** | cls=10, fn=00, op[0]=1 — reserved |
| 14 | <a id="SHR"></a>**SHR** | cls=10, fn=01: ROR with zero fill |
| 15 | <a id="reserved"></a>**reserved** | cls=10, fn=01, op[0]=1 — reserved |
| 16 | <a id="SAR"></a>**SAR** | cls=10, fn=10: ROR with bit 15 fill (arithmetic) |
| 17 | <a id="reserved"></a>**reserved** | cls=10, fn=10, op[0]=1 — reserved |
| 18..23 | <a id="reserved"></a>**reserved** | cls=10, fn=11 and others — reserved |
| 24 | <a id="MUL"></a>**MUL** | cls=11, fn=00: d = (d * s)[15:0] signed; high 16 to MHI |
| 25..27 | <a id="reserved"></a>**reserved** | cls=11, fn=00, op[0]=1 or fn=01 — reserved |
| 28 | <a id="TST"></a>**TST** | cls=11, fn=10: d & s, result discarded, flags written |
| 29 | <a id="reserved"></a>**reserved** | cls=11, fn=10, op[0]=1 — reserved |
| 30 | <a id="CMP"></a>**CMP** | cls=11, fn=11: d - s, result discarded, flags written |
| 31 | <a id="reserved"></a>**reserved** | cls=11, fn=11, op[0]=1 — reserved |

**Notes:**

- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.
