**Blitter Modes (CTRL[2:1])**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="Copy"></a>**Copy** | Read from SRC, write to DST |
| 1 | <a id="Fill"></a>**Fill** | Write KEY to DST |
| 2 | <a id="Copy_with_transparent"></a>**Copy with transparent** | Read from SRC; if byte == KEY, skip the write |
