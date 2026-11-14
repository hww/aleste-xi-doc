# Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})

![Memory Map (24-bit physical address = {PAGE[7:0], WORD[14:0], 1'b0})](gen/memory_map.svg)

| Range | Name | Size | Access | Purpose |
| --- | --- | --- | --- | --- |
| `0x000000`–`0x01FFFF` | <a id="PAGE_0x00"></a>**PAGE 0x00** | 128 KiB | rw | Page 0 (128 KB) |
| `0x020000`–`0xFDFFFF` | <a id="..."></a>**...** | 16128 KiB | rw | Pages 1..254 (each 128 KB) |
| `0xFE0000`–`0xFFFFFF` | <a id="PAGE_0xFF"></a>**PAGE 0xFF** | 128 KiB | rw | Page 255 (last 128 KB) |

**Notes:**

- In RTL addr24 = {page[7:0], word[14:0], 1'b0}. Address space is 16 MB, divided into 256 pages of 128 KB each.
