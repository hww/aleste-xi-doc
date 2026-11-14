# R18 — Video Control (0x12)

![R18 — Video Control (0x12)](gen/crtc_r18.svg)

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RESERVED"></a>**RESERVED** | [7:6] | 2 | Reserved |
| <a id="use_cpc_modes"></a>**use_cpc_modes** | [5] | 1 | 1=use CPC Gate Array bpp |
| <a id="linear_pixel"></a>**linear_pixel** | [4] | 1 | 0=CPC palette, 1=Linear RGB |
| <a id="bpp_mode"></a>**bpp_mode** | [1:0] | 2 | 00=1bpp, 01=2bpp, 10=4bpp, 11=8bpp |
