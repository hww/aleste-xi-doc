**Operating Modes**

| Mode | Supervisor | Native | Description |
| --- | --- | --- | --- |
| Reset | 1 | 1 | Initial state after reset (Supervisor + Native) |
| Trap | 1 | unchanged | Hardware transition to Supervisor |
| Software | from GLOBAL_CTRL | from GLOBAL_CTRL | Control through port F0h |
| User | 0 | 0 | CPC compatibility (User + Legacy) |
| User | 0 | 1 | Extended operating mode (User + Native) |
