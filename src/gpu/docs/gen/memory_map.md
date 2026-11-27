**Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})**

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x000000`–`0x00FFFF` | <a id="PAGE_0x00"></a>**PAGE 0x00** | 64 KiB | rw | Page 0 (64 KB) |
| `0x010000`–`0xFEFFFF` | <a id="..."></a>**...** | 16256 KiB | rw | Pages 1..254 (each 64 KB) |
| `0xFF0000`–`0xFFFFFF` | <a id="PAGE_0xFF"></a>**PAGE 0xFF** | 64 KiB | rw | Page 255 (last 64 KB) |

**Notes:**

- In RTL addr24 = {page[7:0], word[14:0], 1'b0}. Address space is 16 MB, divided into 256 pages of 64 KB each.
