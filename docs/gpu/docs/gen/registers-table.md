**Register file · R0–R31 (24 bit)**

| Index | Name | Description | Group |
| --- | --- | --- | --- |
| R0 | DX | Destination X | destination |
| R1 | DY | Destination Y | destination |
| R2 | DW | Destination width | destination |
| R3 | DH | Destination height | destination |
| R4 | SX | Source X | source |
| R5 | SY | Source Y | source |
| R6 | SW | Source width | source |
| R7 | SH | Source height | source |
| R8 | DSTRIDE | Destination row stride | memory |
| R9 | SSTRIDE | Source row stride | memory |
| R10 | DBASE | Destination base address | memory |
| R11 | SBASE | Source base address | memory |
| R12 | FG | Foreground colour | pixel |
| R13 | BG | Background colour | pixel |
| R14 | MODE | Pixel formats and combine operation | pixel |
| R15 | CX0 | Clip window left | clipping |
| R16 | CY0 | Clip window top | clipping |
| R17 | CX1 | Clip window right | clipping |
| R18 | CY1 | Clip window bottom | clipping |
| R19 | SDX | Source delta X (12.12) | increment |
| R20 | SDY | Source delta Y (12.12) | increment |
| R21 | DDX | Destination delta X (12.12) | increment |
| R22 | DDY | Destination delta Y (12.12) | increment |
| R23 | T0 | Temporary register | temporary |
| R24 | T1 | Temporary register | temporary |
| R25 | T2 | Temporary register | temporary |
| R26 | T3 | Temporary register | temporary |
| R27 | T4 | Temporary register | temporary |
| R28 | T5 | Temporary register | temporary |
| R29 | T6 | Temporary register | temporary |
| R30 | T7 | Temporary register | temporary |
| R31 | T8 | Temporary register | temporary |

**Notes:**

- SDX, SDY, DDX, DDY are a microcode convention (affine mode, 12.12), not a hardware feature.
