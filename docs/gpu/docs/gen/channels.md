**Pixel Engine Channels (48..63)**

| Value | Name | Description |
| --- | --- | --- |
| 48 | <a id="CH0_IDX"></a>**CH0_IDX** | Pixel index, low 16 bits, in pixels (signed). Clears IDXH |
| 49 | <a id="CH1_IDX"></a>**CH1_IDX** | Pixel index, low 16 bits, in pixels (signed). Clears IDXH |
| 50 | <a id="CH2_IDX"></a>**CH2_IDX** | Pixel index, low 16 bits, in pixels (signed). Clears IDXH |
| 51 | <a id="CH3_IDX"></a>**CH3_IDX** | Pixel index, low 16 bits, in pixels (signed). Clears IDXH |
| 52 | <a id="CH0_IDXH"></a>**CH0_IDXH** | Pixel index, bits 18..16 (write before IDX) |
| 53 | <a id="CH1_IDXH"></a>**CH1_IDXH** | Pixel index, bits 18..16 (write before IDX) |
| 54 | <a id="CH2_IDXH"></a>**CH2_IDXH** | Pixel index, bits 18..16 (write before IDX) |
| 55 | <a id="CH3_IDXH"></a>**CH3_IDXH** | Pixel index, bits 18..16 (write before IDX) |
| 56 | <a id="CH0_STEP"></a>**CH0_STEP** | Step in pixels (signed 16 bits) |
| 57 | <a id="CH1_STEP"></a>**CH1_STEP** | Step in pixels (signed 16 bits) |
| 58 | <a id="CH2_STEP"></a>**CH2_STEP** | Step in pixels (signed 16 bits) |
| 59 | <a id="CH3_STEP"></a>**CH3_STEP** | Step in pixels (signed 16 bits) |
| 60 | <a id="CH0_MODE_PAGE"></a>**CH0_MODE_PAGE** | MODE [10:8] and PAGE [7:0] |
| 61 | <a id="CH1_MODE_PAGE"></a>**CH1_MODE_PAGE** | MODE [10:8] and PAGE [7:0] |
| 62 | <a id="CH2_MODE_PAGE"></a>**CH2_MODE_PAGE** | MODE [10:8] and PAGE [7:0] |
| 63 | <a id="CH3_MODE_PAGE"></a>**CH3_MODE_PAGE** | MODE [10:8] and PAGE [7:0] |

**Notes:**

- The operand code is {2'b11, register[1:0], channel[1:0]}: IDX 48..51, IDXH 52..55, STEP 56..59, MODE_PAGE 60..63.
- IDX, IDXH and STEP are written in whole pixels; the channel shifts them by the format (>>> k) into its 20-bit internal index (word + 4-bit position + page-overflow bit).
- IDXH must be written before IDX: writing IDX consumes IDXH and clears it.
- The pixel index is a signed 19-bit value, so a 1 bpp channel only reaches the first 32 KB of its page.
