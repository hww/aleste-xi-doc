# Memory map

![Memory map](gen/map.svg)

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x0000`–`0x3FFF` | <a id="ROM"></a>**ROM** | 16 KiB | ro | Boot code |
| `0x8000`–`0x9FFF` | <a id="RAM"></a>**RAM** | 8 KiB | rw | — |
| `0xF000`–`0xF0FF` | <a id="IO"></a>**IO** | 256 B | rw | Peripherals |
