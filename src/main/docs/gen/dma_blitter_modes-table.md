**Blitter Modes**

| Mode | Val | Desc |
| --- | --- | --- |
| Copy | 0 | Read from SRC, write to DST |
| Fill | 1 | Write KEY to DST |
| Copy with transparent | 2 | Read from SRC; if byte == KEY, skip the write |
