**AMEB-36 parameters**

| Name | Value | Description |
| --- | --- | --- |
| <a id="N_SLOTS"></a>**N_SLOTS** | 4 | Number of expansion slots |
| <a id="PINS"></a>**PINS** | 36 | Pins in the connector (PCIe x1) |
| <a id="BCLK_MHZ"></a>**BCLK_MHZ** | 24.576 | Clock frequency of the AUDIO_BCLK bit, MHz |
| <a id="MCLK_MHZ"></a>**MCLK_MHZ** | 12.288 | AUDIO_MCLK = 256·fs, MHz (ASSUMPTION: separate frequency) |
| <a id="FS_KHZ"></a>**FS_KHZ** | 48 | Frame rate AUDIO_FS, kHz (48 kHz family only) |
| <a id="TDM_SLOTS"></a>**TDM_SLOTS** | 16 | TDM time slots in a frame on each data line |
| <a id="SLOT_BITS"></a>**SLOT_BITS** | 32 | Bits in a time slot |
| <a id="FRAME_BITS"></a>**FRAME_BITS** | 512 | Bits in a frame (16 × 32) |
| <a id="I2C_KHZ"></a>**I2C_KHZ** | 100 | I2C speed, kHz (fixed) |
| <a id="I_3V3_MA"></a>**I_3V3_MA** | 300 | Guideline current +3.3 V per slot, mA (ASSUMPTION, not a calculation) |
| <a id="I_12V_MA"></a>**I_12V_MA** | 50 | Guideline current of each ±12 V rail per slot, mA (ASSUMPTION, not a calculation) |
