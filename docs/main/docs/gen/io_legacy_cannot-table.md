**Legacy Software CANNOT**

| Capability | Why |
| --- | --- |
| Direct MMIO_LO access | No D0XX/D300 window |
| Direct access to PIC, Timer, RTC, Blitter, Sound | Not mapped in Legacy |
| Any modern LX device | Only via syscall |
