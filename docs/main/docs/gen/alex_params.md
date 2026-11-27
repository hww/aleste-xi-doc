**Alex parameters**

| Name | Value | Description |
| --- | --- | --- |
| <a id="N_SLOTS"></a>**N_SLOTS** | 4 | Number of expansion slots |
| <a id="PINS"></a>**PINS** | 36 | Connector contacts (PCIe x1 edge connector) |
| <a id="BCLK_MHZ"></a>**BCLK_MHZ** | 24.576 | AUDIO_BCLK frequency, MHz |
| <a id="MCLK_MHZ"></a>**MCLK_MHZ** | 12.288 | AUDIO_MCLK = 256*fs, MHz (ASSUMPTION: separate frequency) |
| <a id="FS_KHZ"></a>**FS_KHZ** | 48 | AUDIO_FS frame rate, kHz (48 kHz family only) |
| <a id="TDM_SLOTS"></a>**TDM_SLOTS** | 16 | TDM time slots per frame on each data line |
| <a id="SLOT_BITS"></a>**SLOT_BITS** | 32 | Bits per TDM time slot |
| <a id="FRAME_BITS"></a>**FRAME_BITS** | 512 | Bits per frame (16 x 32) |
| <a id="I2C_KHZ"></a>**I2C_KHZ** | 100 | I2C clock, kHz (fixed) |
| <a id="I_3V3_MA"></a>**I_3V3_MA** | 300 | Planning figure: +3.3 V current per slot, mA (ASSUMPTION, not calculated) |
| <a id="I_12V_MA"></a>**I_12V_MA** | 50 | Planning figure: current per slot on each of the +/-12 V rails, mA (ASSUMPTION, not calculated) |
| <a id="DMA_CHANNELS"></a>**DMA_CHANNELS** | 8 | SysDMA channels |
| <a id="DMA_CPU_CHANNELS"></a>**DMA_CPU_CHANNELS** | 4 | SysDMA channels left to the CPU (0..3) |
| <a id="DMA_SPI_CHANNELS"></a>**DMA_SPI_CHANNELS** | 4 | SysDMA channels bound to the SPI slots (4..7) |
| <a id="FIFO_BYTES"></a>**FIFO_BYTES** | 16 | SPI FIFO depth per direction, bytes |
| <a id="BURST_BYTES"></a>**BURST_BYTES** | 8 | Maximum bytes moved per DMA grant |
| <a id="BUS_PEAK_MBPS"></a>**BUS_PEAK_MBPS** | 10 | Theoretical SysDMA bus bandwidth, MB/s |
| <a id="BUS_SUSTAINED_MBPS"></a>**BUS_SUSTAINED_MBPS** | 3 | Planning figure: sustained bus bandwidth, MB/s (author's estimate) |
