**Bank 2 CLIP - inclusive signed clip rectangle on integer position (per window)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 48..51 | <a id="XMIN_0..3_"></a>**XMIN[0..3]** | - | clip X min (inclusive) |
| 52..55 | <a id="YMIN_0..3_"></a>**YMIN[0..3]** | - | clip Y min (inclusive) |
| 56..59 | <a id="XMAX_0..3_"></a>**XMAX[0..3]** | - | clip X max (inclusive) |
| 60..63 | <a id="YMAX_0..3_"></a>**YMAX[0..3]** | - | clip Y max (inclusive) |

**Notes:**

- Active only when MODE.CLIP_ON = 1. Clipped write: no cache access, no overflow error, position still advances. Clipped read returns KEY.
