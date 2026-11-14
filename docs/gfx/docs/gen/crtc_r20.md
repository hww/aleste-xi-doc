# R20 — Address Mode (0x14)

![R20 — Address Mode (0x14)](gen/crtc_r20.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7] | 1 | Reserved |
| <a id="addr_mode"></a>**addr_mode** | [6:4] | 3 | 000=CPC 16KB, 001=EX 32KB, 010=LX 32KB, 011=LX 64KB, 100=Linear |
| <a id="address_rate"></a>**address_rate** | [2] | 1 | 1=two increments per char |
| <a id="address_step"></a>**address_step** | [1] | 1 | 0=increment by 2, 1=increment by 4 |
| <a id="linear_mode"></a>**linear_mode** | [0] | 1 | 0=CPC-style legacy, 1=linear counter |
