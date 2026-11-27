**Slot power-up sequence**

| State | Output | Description |
| --- | --- | --- |
| <a id="False"></a>**False** (initial) | 3V3=0 12V=0 RST=0 | Slot unpowered, host outputs Hi-Z |
| <a id="DETECTED"></a>**DETECTED** | 3V3=0 12V=0 | Module detected |
| <a id="P3V3"></a>**P3V3** | 3V3=1 RST=0 | +3.3 V applied, module held in reset |
| <a id="ID_CHECK"></a>**ID_CHECK** | 3V3=1 RST=1 | Reading the ID EEPROM over I2C |
| <a id="P12"></a>**P12** | 3V3=1 12V=1 | +/-12 V applied |
| <a id="READY"></a>**READY** | ready=1 | Slot ready, signals active |
| <a id="FAULT"></a>**FAULT** | 3V3=0 12V=0 fault=1 | Hardware protection tripped |

| From | To | Condition | Action |
| --- | --- | --- | --- |
| False | DETECTED | DETECT_N == 0 | — |
| DETECTED | P3V3 | EN3V3 = 1 & DETECT_N == 0 | enable +3.3 V |
| DETECTED | False | DETECT_N == 1 | — |
| P3V3 | ID_CHECK | PG3V3 & RST_REL = 1 | release PERIPH_RST_N |
| P3V3 | False | DETECT_N == 1 | — |
| ID_CHECK | P12 | id_ok & EN12 = 1 | enable +/-12 V |
| ID_CHECK | False | id_bad \| timeout | disable +3.3 V |
| P12 | READY | PG12 & PG3V3 | — |
| P12 | FAULT | overcurrent | — |
| READY | FAULT | overcurrent | — |
| READY | False | DETECT_N == 1 | — |
| FAULT | False | clear | — |
