# LX IPC Mailbox — Legacy RTL Reference

**Author:** hww (LX platform)  
**Status:** Legacy / Not part of the OS architecture  
**Address:** `lx_rtl_reference.md`  
**Scope:** Historical reference for the currently implemented RTL mailbox block.

---

## 0. Purpose and status

This document describes the legacy hardware IPC Mailbox implemented in `ipc_mailbox.sv`.

**The IPC Mailbox is not part of the LX OS architecture.**

The architectural design does not require or use a hardware mailbox for communication between the Supervisor (kernel) and drivers.

Kernel-to-driver and driver-to-kernel communication is handled through the OS mechanisms defined in the architecture documentation, including system calls, interrupt handling, and shared memory.

This document is retained solely as a reference for the existing RTL implementation. It does not define an OS interface or impose any software compatibility requirements.

## 1. Architectural status

- The hardware IPC Mailbox is not required by the LX OS.
- Kernel and driver implementations must not depend on its registers or protocol.
- No mailbox-based interrupt or command exchange is part of the OS architecture.
- The mailbox may be removed from a future RTL revision without requiring changes to the OS architecture.
- If the block remains in the current RTL, its register layout and behaviour are documented below for implementation reference only.

### 1.1 Supervisor execution context and software IPC

The current Supervisor execution model permits interrupt handlers to execute within the same execution context as the kernel.

Consequently, interrupt handlers can communicate with the kernel directly through software IPC mechanisms, using any appropriate software-defined communication method.

This capability is already supported by the current execution model and does not require a dedicated hardware IPC Mailbox.

The hardware mailbox described in this document is therefore neither architecturally required nor necessary for interrupt-handler-to-kernel communication.

## 2. Existing RTL implementation

The following sections describe the current implementation of `ipc_mailbox.sv`. They are historical hardware-reference material, not an architectural specification.

[Retain the existing register map, RTL behaviour, and protocol description here.]

## 3. Related documents

- **RTL address:** `lx_rtl_reference.md` §2.
- **OS architecture:** The LX architecture document defines the supported kernel/driver communication mechanisms.
- **Legacy I/O:** `lx_io.md` should not describe the mailbox as an OS communication mechanism.

---

*End of document.*