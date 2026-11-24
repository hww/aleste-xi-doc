**Pixel ALU OP (4 bits)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="PASS"></a>**PASS** | R = X |
| 1 | <a id="AND"></a>**AND** | R = X & Y |
| 2 | <a id="OR"></a>**OR** | R = X \| Y |
| 3 | <a id="XOR"></a>**XOR** | R = X ^ Y (NOT via XOR with 0xFF) |
| 4 | <a id="ANDN"></a>**ANDN** | R = X & ~Y |
| 5 | <a id="ADD"></a>**ADD** | R = (X + Y) mod 2^8 |
| 6 | <a id="ADDS"></a>**ADDS** | R = sat_8(X + Y); 8bpp only (see note) |
| 7 | <a id="SUBS"></a>**SUBS** | R = sat_8(X - Y); 8bpp only (see note) |
| 8 | <a id="MSK"></a>**MSK** | R = (X & B) \| (Y & ~B); third operand B from PEN |
| 9..15 | <a id="RESERVED"></a>**RESERVED** | SUB, MIN, MAX, NOT, AVG, HALF — future |

**Notes:**

- ADDS/SUBS saturate to 255/0 for 8bpp. For 1/2/4bpp they behave as ADD/SUB mod 2^W (no saturation).
