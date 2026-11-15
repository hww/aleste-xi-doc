**Loader packet headers**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="SIZE"></a>**SIZE** | Number of words in packet. |
| 1 | <a id="START"></a>**START** | Start address for programm in ROM |
| 2 | <a id="DATA0"></a>**DATA0** | Low 16-bits of opcode 0. |
| 3 | <a id="DATA0"></a>**DATA0** | Hi 16-bits of opcode 0. |
| 4 | <a id="DATA1"></a>**DATA1** | Low 16-bits of opcode 1. |
| 5 | <a id="DATA2"></a>**DATA2** | Hi 16-bits of opcode 1. |
| 6 | <a id="..."></a>**...** | Rest of opcodes. |
