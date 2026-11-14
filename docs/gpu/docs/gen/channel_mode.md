# CHANNEL FORMAT (fmt, 3 bits)

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="1_bpp"></a>**1 bpp** | 16 pixels per word (k=4); SOURCE ONLY, writes forbidden |
| 1 | <a id="2_bpp"></a>**2 bpp** | 8 pixels per word (k=3) |
| 2 | <a id="4_bpp"></a>**4 bpp** | 4 pixels per word (k=2); pos 0 = high nibble |
| 3 | <a id="8_bpp"></a>**8 bpp** | 2 pixels per word (k=1); pos 0 = high byte |
| 4 | <a id="16_bpp"></a>**16 bpp** | 1 pixel per word (k=0) |
| 5 | <a id="PASS_LO8"></a>**PASS_LO8** | Low byte pass-through |
| 6 | <a id="PASS_HI8"></a>**PASS_HI8** | High byte pass-through |
| 7 | <a id="PASS16"></a>**PASS16** | Whole word pass-through |
