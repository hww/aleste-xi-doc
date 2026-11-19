**Loader packet headers**

| Value | Name | Description |
| --- | --- | --- |
| 0 | <a id="SIZE"></a>**SIZE** | Number of 16-bit payload words in packet |
| 1 | <a id="START"></a>**START** | Start address for program in ROM |
| 2 | <a id="DATA0_L"></a>**DATA0_L** | Low 16 bits of opcode 0 |
| 3 | <a id="DATA0_H"></a>**DATA0_H** | High 16 bits of opcode 0 |
| 4 | <a id="DATA1_L"></a>**DATA1_L** | Low 16 bits of opcode 1 |
| 5 | <a id="DATA1_H"></a>**DATA1_H** | High 16 bits of opcode 1 |
| 6 | <a id="..."></a>**...** | Rest of opcodes |
