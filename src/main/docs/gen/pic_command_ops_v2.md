**PIC COMMAND opcodes (bit7 = 0)**

| Op | Name | Effect |
| --- | --- | --- |
| — | <a id="NOP"></a>**NOP** | No operation |
| — | <a id="COMPLETE"></a>**COMPLETE** | Clear IN_SERVICE for the selected channel |
| — | <a id="ENABLE"></a>**ENABLE** | Set ENABLE for the selected channel |
| — | <a id="DISABLE"></a>**DISABLE** | Clear ENABLE for the selected channel |
| — | <a id="CLEAR_PENDING"></a>**CLEAR_PENDING** | Clear PENDING; a simultaneous new edge is preserved |
| — | <a id="CLEAR_REPEAT"></a>**CLEAR_REPEAT** | Clear REPEAT; a simultaneous new overrun is preserved |
| — | <a id="CLEAR_BOTH"></a>**CLEAR_BOTH** | Clear PENDING and REPEAT; a simultaneous new edge becomes fresh PENDING |
| — | <a id="RESERVED"></a>**RESERVED** | Reserved |
