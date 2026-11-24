**Channel MODE (per channel; word written via SURF.MODE_PAGE)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSVD"></a>**RSVD** | [15] | 1 | reserved (0) |
| <a id="SHR_Y"></a>**SHR_Y** | [14] | 1 | shift operand Y right by 1 before ALU |
| <a id="SHR_X"></a>**SHR_X** | [13] | 1 | shift operand X right by 1 before ALU |
| <a id="CLIP_ON"></a>**CLIP_ON** | [12] | 1 | clipping enabled against CLIP bank |
| <a id="WO"></a>**WO** | [11] | 1 | write-without-read |
| <a id="FMT"></a>**FMT** | [10:8] | 3 | pixel format (see channel_format) |
| <a id="PAGE"></a>**PAGE** | [7:0] | 8 | page number (8 bits) |

**Notes:**

- Reset 0 => FMT=16bpp, PAGE=0, WO=0, CLIP_ON=0, SHR_X=0, SHR_Y=0.
