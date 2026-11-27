# Pixel Engine Channels (V1)

Channels (48..63) are 4 sets of 4 registers each: IDX (48..51), IDXH (52..55), STEP (56..59), MODE_PAGE (60..63), one slot per channel CH0..CH3 (the low two bits of the operand select the channel). They are write-only via `MOV`.

IDX, IDXH and STEP are given in whole pixels; the channel shifts them by its format into the internal index. Two rules:

- **IDXH must be written before IDX.** Writing IDX consumes IDXH and clears it.
- **A 1 bpp channel only reaches the first 32 KB of its page**, because the pixel index is a signed 19-bit value.

{{auto:channels}}

*Fig. 7. Pixel engine channels.*

## DATA[0..3]

DATA[0..3] (44..47) are the pixel ports of channels CH0..CH3 (the low two bits of the operand select the channel). Reading triggers a pixel read operation; writing triggers a pixel write operation.

{{auto:data_regs}}

*Fig. 8. DATA registers.*