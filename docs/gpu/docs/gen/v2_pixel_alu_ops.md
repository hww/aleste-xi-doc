**Pixel ALU OP (4 bits), W-bit unsigned**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="PASS"></a>**PASS** | R = X |
| 1 | <a id="AND"></a>**AND** | R = X & Y |
| 2 | <a id="OR"></a>**OR** | R = X \| Y |
| 3 | <a id="XOR"></a>**XOR** | R = X ^ Y (NOT = XOR with B = all ones) |
| 4 | <a id="ANDN"></a>**ANDN** | R = X & ~Y |
| 5 | <a id="ADD"></a>**ADD** | R = (X + Y) mod 2^W |
| 6 | <a id="ADDS"></a>**ADDS** | R = min(X + Y, 2^W - 1) |
| 7 | <a id="SUBS"></a>**SUBS** | R = max(X - Y, 0) |
| 8 | <a id="MSK"></a>**MSK** | R = (X & B) \| (Y & ~B); third operand B from PEN (not shifted by SHR) |
| 9..15 | <a id="RESERVED"></a>**RESERVED** | SUB (mod 2^W) etc. MIN/MAX come from REL gating, NOT from XOR |
