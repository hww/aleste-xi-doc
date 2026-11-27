**SysDMA channel allocation**

| Channel | Name | Use |
| --- | --- | --- |
| 0 | <a id="CPU0"></a>**CPU0** | Memory to memory, programmed by the CPU |
| 1 | <a id="CPU1"></a>**CPU1** | Memory to memory, programmed by the CPU |
| 2 | <a id="CPU2"></a>**CPU2** | Memory to memory, programmed by the CPU |
| 3 | <a id="CPU3"></a>**CPU3** | Memory to memory, programmed by the CPU |
| 4 | <a id="SPI0"></a>**SPI0** | Slot 0: SRC_ADDR feeds the TX FIFO, the RX FIFO drains to DST_ADDR |
| 5 | <a id="SPI1"></a>**SPI1** | Slot 1: same scheme |
| 6 | <a id="SPI2"></a>**SPI2** | Slot 2: same scheme |
| 7 | <a id="SPI3"></a>**SPI3** | Slot 3: same scheme |

**Notes:**

- An SPI channel uses the same SRC_ADDR and DST_ADDR registers as a CPU channel; the peripheral side is hard-wired.
- For SPI channels COUNT is ignored: the job length comes from SPI_LEN.
- One channel carries both directions: in DUPLEX mode it raises a TX request and an RX request, and each grant moves one burst in one direction.
- SRC_CTRL / DST_CTRL codes of the existing SysDMA are not decoded in the register map yet (see open items).
