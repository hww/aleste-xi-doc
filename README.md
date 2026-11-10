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

### 01. History

[The Aleste Story](./doc/01-history.md)

Describes the historical development of the Aleste architecture, from the original Aleste 520EX through XiAleste to the Aleste LX design.

Explains the background, motivations, and architectural decisions that influenced the evolution of the platform.

### 02. Terminology

[LX Terminology](./doc/02-terminology.md)

Defines the terminology, concepts, and naming conventions used throughout the documentation.

Provides a common vocabulary for understanding the architecture and its components.

### 03. Architecture Overview

[LX — Architecture Overview](./doc/03-overview.md)

Introduces the overall Aleste LX architecture and its fundamental design principles.

Describes the relationships between the processor, memory system, hardware subsystems, firmware, and applications.

This is the recommended starting point for understanding the platform.

### 04. Legacy Architecture

[LX Legacy: CPC 6128 and Aleste 520EX](./doc/04-legacy.md)

Describes the legacy architecture and compatibility mechanisms inherited from earlier Aleste and CPC systems.

Explains how the original programming environment and hardware capabilities relate to the extended LX architecture.

### 05. Input/Output Architecture

[LX I/O: Native and Legacy I/O Map](./doc/05-io.md)

Describes the I/O architecture and the mechanisms used to access hardware resources and peripheral devices.

### 06. RTL Reference

[LX RTL Reference](./doc/06-rtl-reference.md)

Provides a reference to the hardware description and RTL-level architectural elements.

Documents the relevant hardware structures and their organisation.

### 07. Memory Management Unit

[LX MMU: Native and Legacy Memory Management](./doc/07-mmu.md)

Describes the Memory Management Unit (MMU), including address translation, memory mapping, and the organisation of the extended memory space.

### 08. MMU API

[LX MMU API](./doc/08-mmu-api.md)

Describes the software interface for memory management.

Defines the mechanisms available to system software for configuring and accessing the MMU.

### 09. System Calls

[LX Mode Switching Mechanisms](./doc/09-syscall.md)

Describes the system call architecture and the interface through which applications request operating system and BIOS services.

### 10. System Call Details

[Aleste LX: Interrupts, Syscalls, Drivers, and Takeover Mode](./doc/10-syscall-details.md)

Provides a detailed reference for individual system calls, including their parameters, operation, and expected results.

### 11. Inter-Process Communication

[LX IPC Mailbox — Legacy RTL Reference](./doc/11-ipc.md)

Describes the Inter-Process Communication (IPC) mechanisms used for communication between software components and independent execution contexts.

### 12. Programmable Interrupt Controller

[LX PIC Controller](./doc/12-pic.md)

Describes the interrupt controller architecture and the mechanisms used to manage hardware interrupts.

### 13. Direct Memory Access

[LX DMA / Blitter](./doc/13-dma.md)

Describes the DMA architecture and hardware-assisted data transfers.

Explains how data can be moved between system resources without requiring the processor to perform every transfer operation itself.

### 14. Expansion Bus

[LX Modular Expansion Bus (AMEB)](./doc/14-exp-bus.md)

Describes the expansion bus architecture and the mechanisms for connecting external hardware devices to the platform.

### 15. BIOS Specification

[LX BIOS: Driver Architecture Specification](./doc/15-bios-spec.md)

Defines the BIOS architecture and its software-facing interfaces.

Describes the driver model, method dispatch, and the contracts between applications, firmware, and hardware services.

### 16. BIOS Examples

[LX Minimal Supervisor BIOS — example](./doc/16-bios-example.md)

Provides practical examples illustrating the BIOS interfaces and their use by software components.

### Appendixes 

[Aleste LX Video Subsystem — Programmer's Documentation](./gfx/README.md)

[Aleste LX Video Subsystem — Programmer's Documentation](./gfx-coprocessor/README.md)

## Reading Order

For readers approaching the architecture for the first time, the recommended reading order is:

1. **History** — understand how the architecture evolved.
2. **Terminology** — become familiar with the concepts and naming conventions.
3. **Architecture Overview** — understand the overall system.
4. **Legacy Architecture** — explore compatibility with earlier systems.
5. **Subsystem documentation** — study memory management, I/O, interrupts, DMA, IPC, and expansion interfaces.
6. **BIOS documentation** — understand how applications access hardware functionality through software interfaces.

The individual chapters can also be consulted independently when investigating a particular subsystem.

## Documentation Scope and Status

The documentation describes the intended architecture and its software and hardware interfaces.

Not every architectural feature necessarily has the same implementation status in the emulator and the physical FPGA platform.

Architectural descriptions, implementation references, and examples should therefore be considered in their respective contexts.

The documentation is intended to evolve together with the hardware, firmware, emulator, and development tools.

## Project Philosophy

The central idea behind Aleste LX is to preserve the flexibility of software while using FPGA technology to overcome the limitations of traditional 8-bit hardware.

The CPU remains the primary execution engine. Specialised hardware is introduced selectively, providing efficient low-level operations where software alone would be too slow.

This creates a platform in which classic 8-bit programming techniques can coexist with modern hardware architecture, structured software interfaces, and advanced development tools.

The objective is not simply to recreate a historical computer, but to explore what an 8-bit Aleste platform can become when designed with modern technology and architectural freedom.