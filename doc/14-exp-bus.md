# LX Modular Expansion Bus (AMEB)

## Preliminary Hardware Architecture Specification

**Version 0.2 — Architectural Revision**

**Status:** Preliminary design specification  
**Physical interface:** 40-pin connector per expansion slot  
**Target system:** Aleste LX  
**Maximum number of expansion slots:** 4

---

## 1. Design Philosophy

AMEB is a modular expansion interface for the Aleste computer.

The primary objective is to provide a compact, economical and versatile expansion bus that allows the computer to use a variety of digital and hybrid expansion modules.

AMEB is designed as a computer expansion bus, not as a dedicated synthesizer or modular synthesizer interface.

The architecture follows four principles:

1. Digital communication and control are handled by the host FPGA.
2. Audio data is transferred digitally between the host and expansion modules.
3. Analog signal generation and processing are performed locally on expansion modules.
4. Analog power is supplied by the host, while analog audio signals and control voltages remain local to each module.

The design should avoid unnecessary hardware duplication, excessive connector complexity and expensive centralized analog circuitry.

## 2. System Architecture

AMEB consists of three functional subsystems.

### 2.1 Digital Control Plane

Provides communication and control between the host FPGA and expansion modules.

Interfaces:
- SPI — primary module control interface.
- I²C — shared auxiliary management interface.
- Interrupt signals.
- Reset signals.
- Module presence detection.
- General-purpose digital I/O.

### 2.2 Digital Audio Plane

Provides synchronous multichannel digital audio communication between the host FPGA and expansion modules.

The host FPGA handles:
- Audio stream distribution.
- Audio stream collection.
- Channel routing.
- Digital mixing.
- DMA transfers between audio interfaces and system memory.

Expansion modules may process audio independently and return their processed streams to the host.

Audio processing does not require analog audio connections between the host and modules.

### 2.3 Local Analog Subsystem

Each expansion module may contain its own analog circuitry.

Examples include:
- Analog filters.
- Analog oscillators.
- Analog audio effects.
- Instrumentation circuits.
- ADC and DAC circuits.
- Analog signal generators.

Modules requiring analog circuitry generate their own local analog voltages and signals.

The host provides bipolar analog power rails, but does not centrally generate control voltages for expansion modules.

## 3. Physical Interface

Each expansion slot uses an independent 40-pin connector.

The same electrical interface is used for all four slots.

The connector must provide:
- Digital power.
- Analog power.
- Digital ground.
- Analog ground.
- Independent SPI communication.
- Shared I²C communication.
- Digital audio.
- Reset and interrupt signals.
- Module detection.
- General-purpose digital signals.

The final connector type, contact numbering, current ratings and electrical characteristics remain subject to further validation.

## 4. Power Distribution

### 4.1 Digital Power

The host supplies +3.3 V to each expansion module.

This rail powers:
- Digital logic.
- Microcontrollers.
- FPGA interfaces.
- Digital audio circuitry.
- SPI and I²C peripherals.

### 4.2 Analog Power

The host supplies bipolar analog power:

- +12 V
- −12 V
- AGND

These rails are intended for analog circuitry on expansion modules.

The ±12 V supply is the preliminary preferred configuration. ±15 V may be considered if specific module requirements justify the additional power-system complexity.

No dedicated +5 V analog rail is required by the baseline specification. Modules requiring additional voltages should generate them locally.

### 4.3 Grounding

Digital and analog ground contacts are provided separately.

The motherboard must implement a controlled grounding strategy, including an appropriate connection between digital and analog ground domains.

Grounding must take into account:
- Digital switching currents.
- Analog signal integrity.
- Audio noise.
- Return-current paths.
- Power distribution impedance.

Separate ground contacts do not imply galvanic isolation.

### 4.4 Power Protection

Each slot should provide:
- Current limiting.
- Short-circuit protection.
- Controlled power sequencing.
- Overcurrent detection.
- Protection against reverse current where required.

The protection mechanism must not depend exclusively on FPGA or software intervention.

Maximum current per slot and total power budgets must be defined before hardware implementation.

## 5. SPI Interface

Each expansion slot has its own independent SPI interface.

Signals:
- SPI_SCK
- SPI_MOSI
- SPI_MISO
- SPI_CS_N

The four slots must not share the physical SPI signal lines.

The FPGA provides independent SPI control for each slot, allowing different communication speeds and device configurations.

SPI is the primary interface for:
- Module configuration.
- Peripheral control.
- Local DAC programming.
- Local ADC configuration.
- Register access.
- Control of onboard microcontrollers.
- Management of module-specific hardware.

SPI is not intended to carry continuous high-bandwidth audio streams.

The FPGA may schedule SPI transactions independently for each slot.

## 6. I²C Interface

One shared I²C bus is provided across all expansion slots.

Signals:
- I2C_SDA
- I2C_SCL

I²C is intended for low-bandwidth auxiliary communication.

Typical applications:
- Module identification EEPROMs.
- Configuration memory.
- Temperature sensors.
- Power monitoring devices.
- Simple peripheral controllers.

Modules must follow a defined address allocation policy.

The motherboard should provide appropriate pull-up resistors and account for total bus capacitance.

The possibility of isolating a malfunctioning module from the shared I²C bus should be considered.

## 7. Digital Audio Interface

### 7.1 General Requirements

Digital audio is an essential feature of AMEB.

The interface must support multichannel audio communication between the host FPGA and expansion modules.

Audio communication is logically independent of SPI and I²C.

The audio interface is intended for continuous audio streaming and must not depend on periodic SPI transactions.

### 7.2 Proposed Interface Architecture

The preferred architecture is a synchronous multichannel serial audio interface based on TDM or a compatible multichannel serial audio format.

The preliminary signal set is:

- AUDIO_BCLK — bit clock.
- AUDIO_LRCLK / FS — frame synchronization.
- AUDIO_MCLK — master audio clock.
- AUDIO_DOUT — host-to-module audio data.
- AUDIO_DIN — module-to-host audio data.

The clock signals are distributed to all slots.

The audio data connections are independent for each slot.

This arrangement provides:
- Common audio synchronization.
- Independent audio streams for each module.
- No electrical contention between module outputs.
- Flexible routing by the host FPGA.

The host FPGA can distribute audio to selected modules and collect their processed audio streams.

### 7.3 Audio Routing

The architecture must support four expansion slots without requiring audio to pass physically from one module to another.

The host FPGA is responsible for digital audio routing.

For example:

Host audio stream → Module A → Host FPGA → Module B → Host FPGA → Main audio output.

This processing chain is implemented digitally through the FPGA.

A module does not need to be physically connected to another module.

### 7.4 Audio Processing on Expansion Modules

An expansion module may:
- Receive audio from the host.
- Process audio internally.
- Return processed audio.
- Generate audio independently.
- Return multiple audio channels if supported by the selected TDM configuration.

A module may use digital signal processing, analog processing or a hybrid architecture.

Modules performing analog processing must include their own required ADC and DAC circuitry.

Modules processing audio entirely digitally do not require analog converters.

### 7.5 Audio Clocking

A programmable or selectable audio clock source should support the common 44.1 kHz and 48 kHz sample-rate families.

A 12.288 MHz clock alone is insufficient for both families.

The exact master-clock frequencies, TDM frame format, channel count, sample width and timing requirements remain to be specified.

## 8. System Control Signals

The preliminary control signal set is:

- RESET_N — host/system reset.
- PERIPH_RST_N — independent reset for the module in each slot.
- INT_N — module interrupt request.
- DETECT_N — physical module presence detection.

Each slot has its own peripheral reset and module detection connection.

Interrupt handling may be implemented independently per slot.

A separate NMI signal is not required in the baseline architecture.

DETECT_N indicates physical presence only. Module initialization and operational readiness must be determined through the management interface.

## 9. DMA Architecture

DMA is implemented as a logical function of the host FPGA.

It is not a dedicated physical signal on the expansion connector.

The FPGA provides DMA access for:
- Audio input streams.
- Audio output streams.
- Module data transfers.
- Peripheral communication where appropriate.

The architecture should support independent logical DMA endpoints for the expansion slots.

A shared DMA engine may be used internally, provided it offers adequate bandwidth and scheduling guarantees.

The design does not require four independent physical DMA controllers.

## 10. General-Purpose Digital I/O

A small number of GPIO signals should be available per slot.

Possible applications:
- Module-specific status signals.
- Hardware synchronization.
- Additional control signals.
- Experimental peripheral interfaces.

The final number of GPIO contacts must be determined during pin allocation.

GPIO should not duplicate functionality already provided efficiently by SPI, I²C or the standard control signals.

## 11. Local DAC and ADC Architecture

AMEB does not require centralized CV DAC or ADC banks on the motherboard.

Expansion modules generate their own analog control voltages when required.

For example, an analog filter module may contain a multichannel DAC controlled through SPI.

Its DAC channels may control:
- Filter cutoff.
- Resonance.
- Gain.
- Modulation depth.
- Oscillator pitch.
- Other module-specific parameters.

Local ADCs may be used to measure external analog signals or module parameters.

DAC resolution, ADC resolution, reference voltage, calibration and update requirements are determined by each module's application.

The motherboard does not need to provide a fixed number of CV outputs for every possible expansion module.

## 12. Analog Audio and CV Connections

The baseline AMEB connector does not provide dedicated analog audio input/output connections.

It also does not provide dedicated CV input/output connections.

Analog audio processing takes place locally on expansion modules.

Digital audio streams are used to exchange audio between the host and modules.

This avoids:
- Centralized analog mixing circuits.
- Multiple analog input buffers.
- Analog routing matrices.
- Analog audio cross-slot wiring.
- A large number of analog connector contacts.

Modules requiring analog audio processing must implement their own local conversion and analog signal paths.

## 13. Module Identification and Initialization

Each module should provide identification and configuration information.

The preferred mechanism is an identification EEPROM or equivalent device accessible through I²C.

The identification data may include:
- Module identifier.
- Hardware revision.
- Module type.
- Supported audio formats.
- Supported sample rates.
- Available audio channels.
- SPI configuration requirements.
- Power requirements.
- Firmware or driver compatibility information.

Physical presence detection and module readiness are separate states.

## 14. Power Management and Safety

The motherboard must manage the power supplied to each slot.

The design should consider:
- Per-slot power monitoring.
- Current limits.
- Inrush current.
- Short-circuit protection.
- Thermal considerations.
- Safe reset and startup states.

Hot-plug operation is not guaranteed by the connector alone.

Unless explicitly designed and validated, modules should be installed and removed with system power disabled.

If hot-plug capability is required in a future revision, connector sequencing, power switching and signal isolation must be designed accordingly.

## 15. Preliminary 40-Pin Allocation

The following is a functional pin budget, not a final numbered connector pinout.

| Group | Signals | Contacts |
|---|---|---:|
| Digital power | +3.3 V ×2 | 2 |
| Digital ground | DGND ×4 | 4 |
| Analog power | +12 V ×2, −12 V ×2 | 4 |
| Analog ground | AGND ×4 | 4 |
| SPI | SCK, MOSI, MISO, CS_N | 4 |
| I²C | SDA, SCL | 2 |
| Control | RESET_N, PERIPH_RST_N, INT_N, DETECT_N | 4 |
| Digital audio | BCLK, LRCLK/FS, MCLK, DOUT, DIN | 5 |
| GPIO | GPIO0–GPIO3 | 4 |
| Reserved | Future use | 7 |
| **Total** | | **40** |

Duplicated power and ground contacts are preliminary provisions for current capacity and return-path quality. Their final number must be verified against the connector specifications and electrical load calculations.

Reserved contacts should not be assigned prematurely. They may later be used for additional grounds, hardware requests, synchronization or future interface extensions.

## 16. Design Priorities

The AMEB standard should prioritize:

1. Low overall system cost.
2. Minimal motherboard component count.
3. Simple and repeatable module design.
4. Independent operation of expansion modules.
5. Reliable multichannel digital audio.
6. Local analog processing.
7. Efficient FPGA resource utilization.
8. Expandability without unnecessary connector complexity.

The architecture should not require every module to implement every available feature.

A simple digital module should remain inexpensive.

A sophisticated hybrid audio module should be able to implement complex local analog circuitry without requiring additional centralized analog hardware on the motherboard.

## 17. Open Items for the Next Revision

The following parameters remain to be finalized:

- Exact connector type and pin numbering.
- Electrical current limits for each power rail.
- Total motherboard power budget for four slots.
- Final choice between ±12 V and ±15 V analog power.
- Exact TDM or multichannel audio protocol.
- Audio sample rates and supported channel counts.
- Audio data width and frame format.
- Audio clock generation and distribution.
- GPIO count and electrical characteristics.
- Interrupt electrical configuration.
- I²C address allocation.
- Reset timing and power sequencing.
- Signal voltage levels and protection requirements.
- Whether hardware DMA request signals are needed.

---

**Architectural Summary**

AMEB is a digital expansion bus with multichannel digital audio, independent SPI control per slot, shared I²C management and centrally supplied bipolar analog power.

Analog audio generation, conversion and processing are local to expansion modules.

The host FPGA provides digital communication, audio routing, DMA and system coordination.

The objective is to create a flexible but economical expansion architecture for a general-purpose computer, without turning the motherboard into a centralized analog synthesizer system.