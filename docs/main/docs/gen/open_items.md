**Open items**

| # | Name | To be decided |
| --- | --- | --- |
| 1 | <a id="Connector"></a>**Connector** | Verify PCIe position assignments, current per contact and insertion cycle rating against the datasheet |
| 2 | <a id="Power"></a>**Power** | Real +/-12 V and +3.3 V currents per slot and the +5 V budget |
| 3 | <a id="Audio"></a>**Audio** | TDM frame format, bit depth, channels per slot; I2S as baseline profile; whether MCLK is needed |
| 4 | <a id="SysDMA"></a>**SysDMA** | Decode SRC_CTRL / DST_CTRL, Demand-mode handshake per burst, internal FIFO port width, DONE/ERROR semantics for SPI channels |
| 5 | <a id="Arbitration"></a>**Arbitration** | Priority of SysDMA against the audio engine and the GPU on the shared memory path |
| 6 | <a id="Blitter"></a>**Blitter** | Removal of the blitter and compatibility with the MiSTer port |
| 7 | <a id="I2C"></a>**I2C** | Four-pair multiplexer in the FPGA or an external one; EEPROM addresses |
| 8 | <a id="ESD"></a>**ESD** | TVS arrays, 22-33 ohm series resistors, contact mating sequence |
