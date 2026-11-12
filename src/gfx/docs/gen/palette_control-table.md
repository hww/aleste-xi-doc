**Palette Control Register (0x05)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| **mod_en** | [7:7] | 1 | 1=Включить модификацию индекса |
| **mod_type** | [6:6] | 1 | 0=OR, 1=XOR |
| **auto_inc** | [5:5] | 1 | 1=Авто-инкремент индекса |
| **RESERVED** | [4:2] | 3 | Резерв (должно быть 0) |
| **write_mode** | [1:0] | 2 | 00=12-bit, 01=CPC, 10=MSX, 11=YJK |
