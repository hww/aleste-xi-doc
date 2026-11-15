**GLOBAL_CTRL (F0h)**

| Field | Bits | Width | Description |
| --- | --- | --- | --- |
| <a id="RSV"></a>**RSV** | [7:5] | 3 | Reserved |
| <a id="mmio_userlock"></a>**mmio_userlock** | [4] | 1 | 0 = unlocked, 1 = locked. Blocks all MMU ports (E0–FF) in User mode. Only Supervisor can change this bit. |
| <a id="interrupt_hold"></a>**interrupt_hold** | [3] | 1 | 1 = block INT to CPU (set on syscall entry/exit, released by kernel or on RET) |
| <a id="supervisor_hook"></a>**supervisor_hook** | [2] | 1 | 0 = disabled, 1 = enabled. Enables hardware entry into Supervisor mode on M1 at 0038h (IM 1) or 0066h (NMI). |
| <a id="native_mode"></a>**native_mode** | [1] | 1 | 0 = Legacy (CPC 6128), 1 = Native (LX). Ignored in Supervisor mode. [`native_mode_vals`](native_mode_vals.md) |
| <a id="supervisor_mode"></a>**supervisor_mode** | [0] | 1 | 0 = User, 1 = Supervisor. Hardware trap entry on 0038h/0066h. [`supervisor_mode_vals`](supervisor_mode_vals.md) |
