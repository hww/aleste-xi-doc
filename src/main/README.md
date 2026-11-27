# XiAleste and Aleste LX — Architecture Documentation

This repository contains the architectural documentation of the XiAleste and Aleste LX computer platforms.

It describes the evolution of the Aleste architecture, the design principles behind the platform, and the hardware and software interfaces that define its operation.

The documentation covers the processor environment, memory management, system buses, hardware controllers, BIOS, system calls, and inter-process communication.

The goal is to provide a coherent description of the platform as a whole: its architecture, the relationships between its components, and the interfaces available to system software and applications.

## Architecture Overview

Aleste LX explores a design-first approach to retrocomputer development, combining the familiar programming model of an 8-bit processor with a more advanced FPGA-based hardware architecture.

The platform is built around several fundamental principles:

- **CPU-centric design.** The main processor remains responsible for application logic and general-purpose computation. Hardware accelerators assist the CPU with specific operations that are inefficient to perform in software rather than replacing it with autonomous specialised processors.
- **Hardware-assisted software.** Specialised hardware provides efficient low-level operations, allowing software to remain flexible while overcoming the performance limitations of an 8-bit processor.
- **Structured hardware architecture.** Internal components communicate through defined interfaces and system buses, allowing the architecture to evolve without tightly coupling individual subsystems.
- **Extended memory architecture.** Memory management and address translation extend the capabilities of the processor beyond its native logical address space.
- **Protected execution.** Supervisor and user execution modes provide a foundation for controlled access to system resources.
- **Software-defined hardware access.** The BIOS and driver architecture provide stable interfaces between applications and hardware implementations.
- **Virtual and physical platforms.** The architecture is intended to be supported consistently by the emulator and the FPGA implementation.

The platform combines the flexibility of software with specialised hardware assistance. The processor determines what needs to be done, while dedicated hardware helps it perform selected operations efficiently.

## Documentation Structure

The documentation is organised into the following chapters.


- [The Aleste Story](./docs/01-history.md)
- [Terminology](./docs/02-terminology.md)
- [Architecture Overview](./docs/03-overview.md)
- [Legacy: CPC 6128 and Aleste 520EX](./docs/04-legacy.md)
- [I/O: Native and Legacy I/O Map](./docs/05-io.md)
- [RTL: Reference](./docs/06-rtl-reference.md)
- [MMU: Native and Legacy Memory Management](./docs/07-mmu.md)
- [MMU: API](./docs/08-mmu-api.md)
- [SYSCALL: Mode Switching Mechanisms](./docs/09-syscall.md)
- [SYSCALL: Interrupts, Syscalls, Drivers, and Takeover Mode](./docs/10-syscall-details.md)
- [IPC: Mailbox — Legacy RTL Reference](./docs/11-ipc.md)
- [PIC Controller](./docs/12-pic.md)
- [PIC Controller](./docs/12-pic-v2.md)
- [DMA](./docs/13-dma.md) [WORK IN GPROGRESS]
  - [DMA: System DMA](./docs/13-sysdma.md)
  - [DMA: Blitter](./docs/13-blitter.md)
- [ALEX: Expansion Bus](./docs/14-alex.md)
- [BIOS: Driver Architecture Specification](./docs/15-bios-spec.md)
- [BIOS: Minimal Supervisor — example](./docs/16-bios-example.md)
- [TIME: Hardware System Timer](./docs/17-systime.md) [NOT IMPLEMENTED]
- [TIME: Hardware System Timer](./docs/17-systime-v2.md) [NOT IMPLEMENTED]

## Project Philosophy

The central idea behind Aleste LX is to preserve the flexibility of software while using FPGA technology to overcome the limitations of traditional 8-bit hardware.

The CPU remains the primary execution engine. Specialised hardware is introduced selectively, providing efficient low-level operations where software alone would be too slow.

This creates a platform in which classic 8-bit programming techniques can coexist with modern hardware architecture, structured software interfaces, and advanced development tools.

The objective is not simply to recreate a historical computer, but to explore what an 8-bit Aleste platform can become when designed with modern technology and architectural freedom.