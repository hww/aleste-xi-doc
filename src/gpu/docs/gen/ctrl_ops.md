**CTRL OP (J=1, I=0)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="NOP"></a>**NOP** | Nothing |
| 1 | <a id="JMP"></a>**JMP** | PC = ADDR (11 bits) |
| 2 | <a id="CALL"></a>**CALL** | SHADOW[15:12] = flags, SHADOW[11:0] = PC+1; PC = ADDR |
| 3 | <a id="RET"></a>**RET** | PC = SHADOW[11:0]; flags not restored |
| 4 | <a id="HALT"></a>**HALT** | ADDR=0 -> IDLE; ADDR!=0 -> ERROR(code) |
| 5 | <a id="IRQ"></a>**IRQ** | Raise IRQ, code = ADDR |
| 6 | <a id="FLUSH"></a>**FLUSH** | Flush cache channel ADDR[1:0] |
| 7 | <a id="RESERVED"></a>**RESERVED** | Nothing |
