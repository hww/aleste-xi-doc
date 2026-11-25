**Channel MODE (per channel; word written via SURF.MODE_PAGE)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSVD2"></a>**RSVD2** | [15] | 1 | reserved (0) |
| <a id="SHR_Y"></a>**SHR_Y** | [14] | 1 | operand Y >> 1 (logical) before the ALU; not applied to B or to REL operands |
| <a id="SHR_X"></a>**SHR_X** | [13] | 1 | operand X >> 1 (logical) before the ALU; not applied to B or to REL operands |
| <a id="CLIP_ON"></a>**CLIP_ON** | [12] | 1 | clip against the CLIP bank |
| <a id="RSVD"></a>**RSVD** | [11] | 1 | reserved (0); was WO. Whether D is read is derived from ALU_CTL |
| <a id="FMT"></a>**FMT** | [10:8] | 3 | pixel format (see v2_channel_format) |
| <a id="PAGE"></a>**PAGE** | [7:0] | 8 | page number (8 bits), 64 KB per page |

**Notes:**

- Reset 0 => FMT=16bpp, PAGE=0, CLIP_ON=0, SHR_X=0, SHR_Y=0.
