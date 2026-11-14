# Sync Strobe Generation

| Value | Name | Description |
| --- | --- | --- |
| 15..15 | <a id="0xF"></a>**0xF** | stb_char_o — one pulse every 16 pixel clocks |
| 3..3 | <a id="0x3"></a>**0x3** | stb_sync1_o — pulse at pixel 4 within a character |
| 11..11 | <a id="0xB"></a>**0xB** | stb_sync2_o — pulse at pixel 12 within a character |

**Notes:**

- Strobe is generated when `pix_x[3:0]` matches the `code` value.
- `stb_char_o` — one pulse every 16 pixel clocks.
