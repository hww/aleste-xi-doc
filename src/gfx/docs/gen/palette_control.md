# Palette Control Register (0x05)

![Palette Control Register (0x05)](gen/palette_control.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="mod_en"></a>**mod_en** | [7] | 1 | 1=Включить модификацию индекса |
| <a id="mod_type"></a>**mod_type** | [6] | 1 | 0=OR, 1=XOR |
| <a id="auto_inc"></a>**auto_inc** | [5] | 1 | 1=Авто-инкремент индекса |
| <a id="RESERVED"></a>**RESERVED** | [4:2] | 3 | Резерв (должно быть 0) |
| <a id="write_mode"></a>**write_mode** | [1:0] | 2 | 00=12-bit, 01=CPC, 10=MSX, 11=YJK |
