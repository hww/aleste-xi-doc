**Bank 3 PEN - pen & ALU (per primitive)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 48..51 | <a id="B_0..3_"></a>**B[0..3]** | - | pen constant: fill colour / mask for MSK / compare reference (low W bits) |
| 52..55 | <a id="KEY_0..3_"></a>**KEY[0..3]** | - | colour key / compare reference (arbitrary, 0 is legal); also the value returned by a clipped read |
| 56..59 | <a id="ALU_CTL_0..3_"></a>**ALU_CTL[0..3]** | - | pixel ALU control (see v2_alu_ctl_bitfield) |
| 60..63 | <a id="RESERVED"></a>**RESERVED** | - | reserved |
