**ALU OP (5 bits, class = op[4:3], fn = op[2:1], flag = op[0])**

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
| 8 | <a id="ADD"></a>**ADD** | cls=01, fn=00, sub=0, cin_sel=0: d = d + s |
| 10 | <a id="ADC"></a>**ADC** | cls=01, fn=01, sub=0, cin_sel=1: d = d + s + C |
| 13 | <a id="SUB"></a>**SUB** | cls=01, fn=10, sub=1, cin_sel=0: d = d - s; C = not borrow |
| 15 | <a id="SBC"></a>**SBC** | cls=01, fn=11, sub=1, cin_sel=1: d = d - s - (1-C) |
| 16 | <a id="ROR"></a>**ROR** | cls=10, fn=00: 16-bit rotate right by s[3:0] |
| 18 | <a id="SHR"></a>**SHR** | cls=10, fn=01: logical shift right |
| 20 | <a id="SAR"></a>**SAR** | cls=10, fn=10: arithmetic shift right |
| 24 | <a id="MUL"></a>**MUL** | cls=11, fn=00: d = (d * s)[15:0] signed; high 16 to MHI |

**Notes:**

- Writing to ZERO discards the result. NOP = MOV ZERO, ZERO.
- TST/CMP are encoded in the assembler with WRITE=0; dedicated opcodes 28/30 are equivalent to AND/SUB with WRITE=0.
