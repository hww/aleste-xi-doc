**Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0}); 64 KB per page**

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x000000`–`0x00FFFF` | <a id="PAGE_0x00"></a>**PAGE 0x00** | 64 KiB | rw | Page 0 (64 KB) |
| `0x010000`–`0xFEFFFF` | <a id="..."></a>**...** | 16256 KiB | rw | Pages 1..254 (each 64 KB) |
| `0xFF0000`–`0xFFFFFF` | <a id="PAGE_0xFF"></a>**PAGE 0xFF** | 64 KiB | rw | Page 255 (last 64 KB) |

**Notes:**

- 8 + 15 + 1 = 24 bits: 256 pages x 32768 words x 2 bytes = 16 MB. The previous text (128 KB per page) contradicted the formula.
