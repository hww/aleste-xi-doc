# CHANNEL MODE_PAGE (11 bits: MODE[2:0] + PAGE[7:0])

![CHANNEL MODE_PAGE (11 bits: MODE[2:0] + PAGE[7:0])](gen/channel_mode_page.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="FMT"></a>**FMT** | [10:8] | 3 | Channel format (3 bits) |
| <a id="PAGE"></a>**PAGE** | [7:0] | 8 | Page number (8 bits) |

**Notes:**

- In RTL, MODE and PAGE are two separate registers: mode_r[ch] (3 bits) and page_ebr[ch] (8 bits). MODE_PAGE is their logical concatenation.
