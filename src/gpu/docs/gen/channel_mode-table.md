**CHANNEL FORMAT (fmt, 3 bits)**

| Fmt | Name | Description |
| --- | --- | --- |
| 0 | 1 bpp | 16 pixels per word; SOURCE ONLY, unpacked to 4/8 bpp colours; writes forbidden |
| 1 | reserved | - |
| 2 | 4 bpp | 4 pixels per word; pos 0 = high nibble |
| 3 | 8 bpp | 2 pixels per word; pos 0 = high byte |
| 4 | 16 bpp | 1 pixel per word |
| 5 | PASS_LO8 | Low byte |
| 6 | PASS_HI8 | High byte |
| 7 | PASS16 | Whole word |
