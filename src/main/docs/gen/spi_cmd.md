**SPIn_CMD · 8 bits (write-only; START launches a job)**

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7] | 1 | — | — | Reserved |
| <a id="ABORT"></a>**ABORT** | [6] | 1 | wo | 0 | Abort the job and flush both FIFOs |
| <a id="START"></a>**START** | [5] | 1 | wo | 0 | Start the job |
| <a id="WAIT_DREQ"></a>**WAIT_DREQ** | [4] | 1 | wo | 0 | Wait for GPIO0_DREQ_N = 0 before the first byte |
| <a id="LAST"></a>**LAST** | [3] | 1 | wo | 0 | Release CS_N after the last byte (packet end) |
| <a id="FIRST"></a>**FIRST** | [2] | 1 | wo | 0 | Assert CS_N before the first byte (packet start) |
| <a id="MODE"></a>**MODE** | [1:0] | 2 | wo | 0x0 | Transfer mode [`alex_spi_modes`](alex_spi_modes.md) |
