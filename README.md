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

## Aleste LX

- [Terminology](./docs/main/docs/02-terminology.md)
- [Architecture Overview](./docs/main/docs/03-overview.md)
- [Legacy: CPC 6128 and Aleste 520EX](./docs/main/docs/04-legacy.md)
- [I/O: Native and Legacy I/O Map](./docs/main/docs/05-io.md)
- [RTL: Reference](./docs/main/docs/06-rtl-reference.md)
- [MMU: Native and Legacy Memory Management](./docs/main/docs/07-mmu.md)
- [MMU: API](./docs/main/docs/08-mmu-api.md)
- [SYSCALL: Mode Switching Mechanisms](./docs/main/docs/09-syscall.md)
- [SYSCALL: Interrupts, Syscalls, Drivers, and Takeover Mode](./docs/main/docs/10-syscall-details.md)
- [IPC: Mailbox — Legacy RTL Reference](./docs/main/docs/11-ipc.md)
- [PIC Controller](./docs/main/docs/12-pic.md)
- [DMA](./docs/main/docs/13-dma.md) [WORK IN GPROGRESS]
  - [DMA: System DMA](./docs/main/docs/13-sysdma.md)
  - [DMA: Blitter](./docs/main/docs/13-blitter.md)
- [ALEX: Expansion Bus](./docs/main/docs/14-alex.md)
- [BIOS: Driver Architecture Specification](./docs/main/docs/15-bios-spec.md)
- [BIOS: Minimal Supervisor — example](./docs/main/docs/16-bios-example.md)
- [TIME: Hardware System Timer](./docs/main/docs/17-systime.md) [NOT IMPLEMENTED]

### Magic Sound 2

- [SM2: Magic Sound 2 (rev. A)](./docs/sm/docs/lx_ms2_rev_a.md)
- [SM2: Magic Sound 2 (rev. C)](./docs/sm/docs/lx_ms2_rev_c.md)

### Graphics and Video

- [GFX: Video Subsystem — Programmer's Documentation](./docs/gfx/docs/README.md)
- [GPU: LX Graphics Processing Unit — Programmer's Documentation](./docs/gpu/docs/README.md)

## Documentation Build System

The documentation is not edited directly in the final Markdown files. It is generated from a set of source files using a custom Python build script (`build.py`). This approach allows for automatic diagram generation, dynamic table insertion, and consistent cross-referencing.

### Directory Structure

The repository is structured to separate source files, generated content, and the final output:

```text
├── build.py              # The main build script
├── src/                  # Source files
│   ├── <project>/        # e.g., gfx, gpu, main
│   │   ├── docs/         # Markdown templates
│   │   │   ├── images/   # Hand-drawn images (e.g., .webp, .png)
│   │   │   └── gen/      # Generated content (e.g., .svg, .md)
│   │   └── spec/         # YAML specifications for diagrams and tables
└── out/                  # Final compiled documents and assets
```

### How It Works

1. **YAML Specifications (`spec/*.yaml`)**:
   Diagrams (bitfields, timing, register maps) and data tables are defined in YAML format. This ensures a single source of truth for hardware specifications.

2. **Generation (`docs/gen/`)**:
   The build script reads the YAML files and generates:
   - SVG vector graphics (`*.svg`).
   - Markdown tables (`*.md`).
   These files are placed in `docs/gen/`, allowing VS Code to display them directly in the editor.

3. **Templating (`docs/*.md`)**:
   Source Markdown files contain special include tags, such as:
   - `![](gen/alu.svg)` — inserts a generated image.
   - `[include](gen/registers.md)` — injects a generated table directly into the text.
   - `![](images/foo.webp)` — inserts a manually created image.

4. **Assembly (`out/`)**:
   The build script processes the templates, resolves the `[include]` tags, and writes the final, self-contained Markdown files to `out/`. It also copies all required images into `out/<project>/images/`, ensuring the final directory is ready for publishing.

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

