**Loader packet headers**

| Code | Name | Arg | Description |
| --- | --- | --- | --- |
| 0 | END | - | End, IDLE |
| 1 | ENDI | IRQ code | End with interrupt |
| 2 | CODE | word count | Load microcode: start address, then 2 packet words per instruction |
| 3 | RUN | entry point | Start microprogram |
| 4 | JUMP | - | Next 2 words = new stream pointer |

**Notes:**

- End of task: MOV FLUSH, ZERO ; MOV IRQ, Rcode ; HALT 0.
