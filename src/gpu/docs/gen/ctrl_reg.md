# CTRL · 32 BIT

![CTRL · 32 BIT](gen/ctrl_reg.svg)

| Field | Bits | Width | Access | Reset | Description |
| --- | --- | --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [31:16] | 16 | — | — | Reserved |
| <a id="DIV"></a>**DIV** | [15:8] | 8 | rw | 0x10 | Clock divider |
| <a id="IRQ"></a>**IRQ** | [4] | 1 | w1c | 0 | Interrupt pending |
| <a id="MODE"></a>**MODE** | [3:1] | 3 | rw | 0x0 | Mode |
| <a id="EN"></a>**EN** | [0] | 1 | rw | 0 | Enable |
