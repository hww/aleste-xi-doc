**CHANNEL FORMAT (fmt, 3 bits; 8bpp is primary)**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="16_bpp"></a>**16 bpp** | 1 pixel per word (k=0) |
| 1 | <a id="8_bpp"></a>**8 bpp** | 2 pixels per word (k=1); pos 0 = low byte (even address) — PRIMARY |
| 2 | <a id="4_bpp"></a>**4 bpp** | 4 pixels per word (k=2); pos 0 = low nibble |
| 3 | <a id="2_bpp"></a>**2 bpp** | 8 pixels per word (k=3); SOURCE ONLY, writes forbidden |
| 4 | <a id="1_bpp"></a>**1 bpp** | 16 pixels per word (k=4); SOURCE ONLY, writes forbidden |
| 5 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 6 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
| 7 | <a id="RESERVED"></a>**RESERVED** | Reserved, writes forbidden |
