# CHANNEL MODE_PAGE (11 bits, логическая склейка MODE[2:0] + PAGE[7:0])

![CHANNEL MODE_PAGE (11 bits, логическая склейка MODE[2:0] + PAGE[7:0])](gen/channel_mode_page.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="FMT"></a>**FMT** | [10:8] | 3 | Channel format (3 bits) |
| <a id="PAGE"></a>**PAGE** | [7:0] | 8 | Page number (8 bits) |

**Notes:**

- В RTL MODE и PAGE — два отдельных регистра: mode_r[ch] (3 бита) и page_ebr[ch] (8 бит). MODE_PAGE — это их логическая склейка для удобства записи через один операнд.
