# Loader packet headers

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="END"></a>**END** | End, IDLE (arg: -) |
| 1 | <a id="ENDI"></a>**ENDI** | End with interrupt (arg: IRQ code) |
| 2 | <a id="CODE"></a>**CODE** | Load microcode: start address, then 2 packet words per instruction (arg: word count) |
| 3 | <a id="RUN"></a>**RUN** | Start microprogram (arg: entry point) |
| 4 | <a id="JUMP"></a>**JUMP** | Next 2 words = new stream pointer (arg: -) |

**Notes:**

- Loader is not implemented in RTL. Reserved for future extension.
