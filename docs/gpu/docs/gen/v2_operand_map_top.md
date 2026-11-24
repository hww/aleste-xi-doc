**Operand map (6 bits, 0..63)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 42 | <a id="BANK"></a>**BANK** | [2:0] active bank | [2:0] bank select (global, all channels) |
| 43 | <a id="SPARE"></a>**SPARE** | - | reserved |
| 44..47 | <a id="DATA_0..3_"></a>**DATA[0..3]** | pixel_out from channel ch | pixel_in to channel ch (triggers pixel op); operand[1..0] = channel |
| 48..63 | <a id="BANK_WINDOW"></a>**BANK_WINDOW** | - | write-only banked register; group=dst[3:2], channel=dst[1:0], bank=BANK |

**Notes:**

- 38..41 are ROM (ROML/ROMH/ROMA + spare), unchanged by this map; see architecture.yaml.
- BANK write takes effect on the next instruction (X-stage decode, in-order, no hold).
