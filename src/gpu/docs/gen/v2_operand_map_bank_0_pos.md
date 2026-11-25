**Bank 0 POS - position (per scanline). 16.16 two's complement integer / unsigned fraction**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 48..51 | <a id="XI_0..3_"></a>**XI[0..3]** | - | X integer part (signed). With PITCH=0: pixel index [15:0] (old IDX) |
| 52..55 | <a id="YI_0..3_"></a>**YI[0..3]** | - | Y integer part (signed). With PITCH=0: bits [2:0] = pixel index [18:16] (old IDXH) |
| 56..59 | <a id="XF_0..3_"></a>**XF[0..3]** | - | X fractional part |
| 60..63 | <a id="YF_0..3_"></a>**YF[0..3]** | - | Y fractional part |
