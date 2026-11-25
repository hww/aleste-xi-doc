**Bank 1 STEP - added to position after every DATA access (per primitive)**

| Code | Name | Read | Write |
| --- | --- | --- | --- |
| 48..51 | <a id="DXI_0..3_"></a>**DXI[0..3]** | - | step X integer part (signed) |
| 52..55 | <a id="DYI_0..3_"></a>**DYI[0..3]** | - | step Y integer part (signed) |
| 56..59 | <a id="DXF_0..3_"></a>**DXF[0..3]** | - | step X fractional part |
| 60..63 | <a id="DYF_0..3_"></a>**DYF[0..3]** | - | step Y fractional part |

**Notes:**

- Old STEP (12.4) maps to DXI = STEP >> 4, DXF = (STEP & 15) << 12, DYI = DYF = 0.
