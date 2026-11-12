**GLOBAL_CTRL (F0h) Bit Map**

| Поле | Биты | Ширина | Описание |
| --- | --- | --- | --- |
| **reserved** | [7:5] | 3 | Must be 0. |
| **mmio_userlock** | [4:4] | 1 | 0 = unlocked, 1 = locked. Blocks all MMU ports (E0–FF) in User mode, preventing unauthorised access. Only Supervisor can change this bit. |
| **reserved** | [3:3] | 1 | Must be 0. |
| **supervisor_hook** | [2:2] | 1 | 0 = disabled, 1 = enabled. Enables hardware entry into Supervisor mode on M1 at 0038h (IM 1) or 0066h (NMI). Allows the kernel to intercept interrupt handling. |
| **native_mode** | [1:1] | 1 | 0 = Legacy (CPC 6128 compatibility), 1 = Native (modern LX address space). Ignored in Supervisor mode (Native mechanism is always used). |
| **supervisor_mode** | [0:0] | 1 | 0 = User, 1 = Supervisor. In Supervisor mode, all system registers are accessible. In User mode, access is restricted. |
