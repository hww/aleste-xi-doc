# Aleste LX — Architecture and BIOS Documentation

**Technical documentation for the Aleste LX 8-bit computer platform, its BIOS architecture, and its driver interface.**

Aleste LX explores a design-first approach to retrocomputer development: define the platform architecture, establish the software interfaces, and develop the firmware before the physical hardware is ready.

This repository documents the architectural decisions behind that approach, with a particular focus on the BIOS, the driver model, and the contracts that connect applications to hardware services.

The goal is not simply to document a collection of registers. It is to explain how the platform is structured, how its components interact, and how software can be developed against a stable interface.

---

## Start Here

There are two primary documents.

### Aleste LX Platform Architecture

**[Read the platform documentation](https://github.com/hww/aleste-xi-doc/blob/main/aleste-lx/aleste-xi.en.md)**

Describes the architecture of the Aleste LX platform and the design concepts behind the system.

- [PDF version](https://github.com/hww/aleste-xi-doc/blob/main/bios/aleste-bios.pdf)

### BIOS and Driver Architecture

**[Read the BIOS architecture document](./bios/aleste-bios.org)**

Explains the architectural foundation of the BIOS and the model used to expose hardware functionality through software interfaces.

- [PDF version](./bios/aleste-bios.pdf)
- [BIOS architecture diagram](./bios/states_simplified.png)

The BIOS document is the recommended starting point for understanding the relationship between the BIOS, driver implementations, and application-facing interfaces.

---

## The Architecture Behind the Documentation

### A Contract Between Software and Hardware

An important design principle in Aleste LX is the separation between an application's view of the system and the implementation of its hardware.

Applications should not need to know the internal details of every peripheral. Instead, they should access system functionality through interfaces defined by the BIOS and its drivers.

This creates a clear architectural boundary:

1. **Applications** request services through public interfaces.
2. **The BIOS** provides the common entry points and dispatches requests.
3. **Drivers** implement the functionality associated with individual hardware components.
4. **The hardware platform** provides the underlying resources used by those implementations.

The purpose of this separation is to reduce coupling between applications and hardware details.

### Drivers as Explicit Interfaces

A driver is more than a collection of routines that manipulate hardware registers. It is a component with a defined interface.

The driver model uses a structured call-table approach: driver methods are described through declared interfaces, and the BIOS dispatches requests through those interfaces.

This approach is intended to provide several benefits:

- **A stable application interface.** Applications can depend on declared methods rather than scattered hardware addresses.
- **Explicit contracts.** Driver methods and error codes define how software components communicate.
- **Replaceable implementations.** A driver can be modified without necessarily changing the applications that use it.
- **Testability.** Implementations can be exercised in an emulator before the physical hardware is available.
- **A path to hardware independence.** Application code can be reused across compatible implementations of the platform.

These benefits depend on maintaining compatibility between the declared interfaces, the BIOS implementation, and the underlying hardware.

### Why the Emulator Matters

A virtual platform provides an environment in which firmware and drivers can be developed before the target hardware is available.

The emulator is therefore more than a convenience for running Z80 programs. It can serve as an executable reference for the platform's memory mapping, peripheral behavior, and software-visible interfaces.

This makes it possible to investigate architectural decisions and test software while the hardware implementation is still evolving.

The long-term objective is to keep the software contract consistent between the virtual platform and the physical implementation.

---

## Documentation Map

The repository is organized into three groups of material.

### 1. Platform Documentation

Directory: [`aleste-lx Documentation`](https://github.com/hww/aleste-xi-doc/blob/main/aleste-lx/aleste-xi.pdf)

Contains the main architectural document for Aleste LX in Org format and PDF.

Use this document to explore the platform as a whole and understand the broader architectural context.

### 2. BIOS Documentation

Directory: [`bios/`](./bios/)

Contains the BIOS architecture document in Org format and PDF, together with a simplified state diagram.

This is the primary reference for readers interested in firmware structure, driver interfaces, and the organization of the BIOS.

### 3. Working Notes and Research

Directory: [`import/`](./import/)

Contains research notes, exploratory designs, and preliminary technical material.

Topics include:

- Memory management and MMU design.
- System buses and DMA.
- GPU and video architecture.
- I/O interfaces.
- Inter-process communication.
- System calls.
- Interrupt controllers.
- Audio architecture and retro sound effects.
- Memory libraries and firmware design considerations.

These files preserve design exploration and technical reasoning that may not yet be reflected in the main documentation.

**Important:** Working notes are not necessarily normative specifications. Their contents may be incomplete, experimental, or superseded by later design decisions.

See the [working-notes README](./import/README.md) for additional context.

### 4. Legacy XIFF Specifications

Directory: [`xiff/`](./xiff/)

Contains historical versions of XIFF, a metalinguage originally intended to describe driver programs.

The directory includes several versions of the specification, including English-language documents for XIFF 5.0 and XIFF 6.0.

**XIFF is deprecated.** These documents are retained for historical reference and to preserve the evolution of the original design. They should not be treated as the current definition of the Aleste LX driver architecture.

---

## How to Read This Repository

The recommended reading order depends on your interests.

| If you want to... | Start with... |
|---|---|
| Understand the overall platform | Aleste LX platform documentation |
| Understand the BIOS design | BIOS and Driver Architecture |
| Explore the design of the driver interfaces | BIOS architecture documentation and the corresponding source code |
| Investigate memory, video, sound, or I/O | Relevant notes in `import/` |
| Study the history of the driver-description language | Legacy XIFF specifications |

For firmware development, read the BIOS documentation alongside the [Aleste LX BIOS source repository](https://github.com/hww/aleste-xi-bios).

For the hardware implementation, see the [Aleste LX FPGA project](https://github.com/hww/aleste-lx-fpga-sv).

---

## Documentation Status

This repository contains material at different stages of maturity.

- **Main documents** describe the platform and BIOS architecture.
- **Working notes** capture ongoing or exploratory design work.
- **Legacy specifications** document historical approaches that have since been deprecated.

The presence of a document in this repository does not necessarily mean that every described feature has been implemented or that every proposal has been adopted.

Where implementation status matters, consult the relevant source code and project documentation.

---

## Contributing and Using the Documentation

When updating the documentation, keep the distinction between architectural decisions, implementation details, and exploratory ideas explicit.

In particular:

- Update the main documents when an architectural decision becomes established.
- Keep experimental proposals identifiable as working notes.
- Mark superseded specifications as deprecated rather than silently treating them as current.
- Keep diagrams and PDF exports consistent with their corresponding source documents.

The aim is to maintain a useful record of both the platform's architecture and the reasoning behind its design.

---

## Related Projects

- [Aleste LX BIOS](https://github.com/hww/aleste-xi-bios) — BIOS, drivers, and the virtual development platform.
- [Aleste LX FPGA](https://github.com/hww/aleste-lx-fpga-sv) — hardware implementation of the Aleste platform.

---

*Aleste LX is an evolving architectural project. This repository documents its design, implementation concepts, and development history.*
