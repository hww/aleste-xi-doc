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

[The Aleste Story](01-history.md)

Describes the historical development of the Aleste architecture, from the original Aleste 520EX through XiAleste to the Aleste LX design.

Explains the background, motivations, and architectural decisions that influenced the evolution of the platform.

### 02. Terminology

[Xi/LX Terminology](02-terminology.md)

Defines the terminology, concepts, and naming conventions used throughout the documentation.

Provides a common vocabulary for understanding the architecture and its components.

### 03. Architecture Overview

[](03-overview.md)

Introduces the overall Aleste LX architecture and its fundamental design principles.

Describes the relationships between the processor, memory system, hardware subsystems, firmware, and applications.

This is the recommended starting point for understanding the platform.

### 04. Legacy Architecture

[](04-legacy.md)

Describes the legacy architecture and compatibility mechanisms inherited from earlier Aleste and CPC systems.

Explains how the original programming environment and hardware capabilities relate to the extended LX architecture.

### 05. Input/Output Architecture

[](05-io.md)

Describes the I/O architecture and the mechanisms used to access hardware resources and peripheral devices.

### 06. RTL Reference

[](06-rtl-reference.md)

Provides a reference to the hardware description and