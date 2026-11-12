**Sync Strobe Generation**

| Code | Strobe | Desc |
| --- | --- | --- |
| 0xF | stb_char_o | One pulse every 16 pixel clocks |
| 0x3 | stb_sync1_o | Pulse at pixel 4 within a character |
| 0xB | stb_sync2_o | Pulse at pixel 12 within a character |

**Notes:**

- Строб генерируется, когда `pix_x[3:0]` совпадает со значением `code`.
- `stb_char_o` — один импульс каждые 16 пиксельных тактов.
