**Timer F6 bit layout**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | Reserved |
| <a id="FIRED"></a>**FIRED** | [4] | 1 | R: the request for the current target has been sent; cleared by the F5 commit. W: ignored |
| <a id="DUE"></a>**DUE** | [3] | 1 | R: live comparator output (ARMED & ~delta[15]). W: ignored |
| <a id="WINDOW"></a>**WINDOW** | [2] | 1 | R: COMPARE write in progress (F4 written, F5 not yet; blocks INT, not NMI). W: ignored |
| <a id="ARMED"></a>**ARMED** | [1] | 1 | R: target timestamp has been committed. W: ignored |
| <a id="ENABLE"></a>**ENABLE** | [0] | 1 | R: comparison enabled. W: 1 = enable, 0 = disable (supervisor only) |
