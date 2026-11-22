# AMEB-36 Modular Expansion Bus

## Preliminary hardware specification

## 1. Project philosophy

AMEB is a modular expansion interface for the Aleste LX computer. It is a computer expansion bus, not a synthesizer or modular synthesizer interface.

Goal: a compact, inexpensive, and universal slot that does not repeat the shortcomings of 50–60-pin retro slots (large board area, fragility, 5 V only).

The architecture rests on five principles:

1. Communication and control are handled by the host FPGA, while the Z80 processor works with slots as peripheral devices through I/O ports, without memory mapping: reads from such an area would block the processor.
2. Audio is transferred between the host and modules only in digital form.
3. Analog signal generation and processing are performed locally on the modules.
4. Analog power (±12 V) is supplied by the host. Analog signals and control voltages remain inside the module, and there are no DC/DC converters on the modules.
5. All interfaces are implemented in hardware, not by software emulation.

The design must not require extra equipment, complex connectors, or an expensive centralized analog section.

## 2. System architecture

The system consists of three subsystems.

### 2.1 Digital control plane

Communication and control between the host FPGA and the modules. Interfaces:

- SPI: one independent controller per slot (see section 5).
- I²C: one hardware byte controller with multiplexing to the slots (see section 6).
- Interrupt `INT_N` and data request `GPIO0_DREQ_N`.
- Module reset `PERIPH_RST_N` for each slot. There is no global `RESET_N`: the host resets all slots itself.
- Module detection `DETECT_N`.
- One more digital output `GPIO1`.

The control registers are accessible to the processor through I/O ports: {{ref:ameb_io}}.

{{auto:ameb_io}}

### 2.2 Digital audio plane

Synchronous multichannel audio transfer between the host FPGA and the modules (see section 7). The host FPGA performs:

- distribution and collection of audio streams;
- channel routing;
- digital mixing;
- DMA transfers between the audio interfaces and system memory.

### 2.3 Local analog subsystem

A module may contain its own analog circuits: filters, oscillators, effects, measurement circuits, ADCs, and DACs. The module generates all control voltages itself, for example from a multichannel DAC controlled over SPI. The host does not generate control voltages.

## 3. Physical interface

Each slot uses a PCIe x1 edge connector with {{const:PINS}} pins. All {{const:N_SLOTS}} slots are electrically identical. A module is a 1.6 mm board with gold fingers and a chamfer, installed vertically. An alternative: 1.27 mm pitch headers and sockets, 2×18; the pinout carries over unchanged, but there is no physical key, so labeling and protection against incorrect orientation are needed.

The PCIe key between positions 11 and 12 divides the slot into two zones:

- **Zone 1 (positions 1–11, 22 pins):** power, analog grounds, I²C, SPI_CS_N, control, and GPIO.
- **Zone 2 (positions 12–18, 14 pins):** the high-speed digital path: SPI_SCK, SPI_MOSI, SPI_MISO, and audio.

This gives a natural separation on the motherboard and on the module: analog stays on one edge, and the 24 MHz clock lines are behind the key.

{{auto:ameb_pcie_edge}}

The pin balance is described in {{table:pin_groups}}. There is no free reserve: four NC positions are occupied for protection reasons.

{{table:pin_groups}}

### 3.1 Protection against inserting a real PCIe card

A real PCIe card can be plugged into the slot, so:

- at positions where PCIe has +12 V and +3.3 V aux, AMEB has either the same voltage or NC, but not a signal;
- the negative voltage −12 V is placed on A5, i.e. on the JTAG position, which is not connected on ordinary cards;
- where possible, functions match PCIe, so signal directions do not conflict.

{{table:pcie_compat}}

The PCIe position assignments are from memory and must be verified against PCIe CEM and the datasheet of the chosen connector.

### 3.2 Electrical and mechanical protection

TVS arrays and 22–33 Ω series resistors are installed on the signals. With an edge connector, the pin mating sequence is implemented by the module's construction: ground pads are longer, and `DETECT_N` is shorter than the others.

## 4. Power distribution

### 4.1 Digital power

The host supplies +3.3 V to three slot pins. Current guideline: {{const:I_3V3_MA}} mA per slot (an estimate, not a calculation).

### 4.2 Analog power

The host supplies +12 V (two pins), −12 V (one pin), and AGND (three pins). Current guideline: {{const:I_12V_MA}} mA per slot on each rail (an estimate, not a calculation).

±12 V generation is done on the motherboard: one step-up and one inverting converter. No DC/DC is placed on the modules. Modules are recommended to use local LDOs on the analog rails. The ±12 V section can be made optionally populated (DNP) so that a board without analog modules is cheaper. Modules derive additional voltages from the available ones.

### 4.3 Grounding

DGND and AGND pins are separate, and every high-speed line has a DGND pin next to it. DGND and AGND are connected only on the motherboard, and the module does not short them, to avoid ground loops. Separate grounds do not mean galvanic isolation.

### 4.4 Protection and power-up sequence

Each slot has current limiting, short-circuit protection, and overload monitoring. For +12 V this is a current switch with an enable input from the FPGA; for −12 V it is a PTC fuse, enabled together with +12 V. Protection must not depend solely on the FPGA or software.

The slot powers up in sequence: first only +3.3 V with the module held in reset, then reading the ID-EEPROM over I²C, and only after a successful check is ±12 V applied. A real PCIe card will not respond to the EEPROM request and will not receive the analog rails.

{{auto:slot_power}}

{{auto:slot_power_seq}}

The state `{{ref:slot_power.ID_CHECK}}` is the only one where the module already receives +3.3 V but does not yet receive ±12 V. The `{{ref:slot_ctrl.EN12}}` enable takes effect only after a successful identifier check. When protection trips, the slot transitions to `{{ref:slot_power.FAULT}}`; the reset is performed by writing to `{{ref:slot_stat.FAULT}}`.

{{auto:ameb_slots}}

## 5. SPI interface

Each slot has its own SPI controller with signals `SPI_SCK`, `SPI_MOSI`, `SPI_MISO`, `SPI_CS_N`. The physical lines are not shared between slots. Mode 0 (CPOL = 0, CPHA = 0), the speed is set by the `{{ref:spi_ctrl.DIV}}` divider independently for each slot.

SPI is the primary interface for module configuration, programming local DACs and ADCs, accessing registers, and controlling microcontrollers on the module. It is not intended for continuous audio.

{{auto:spi_mode0}}

{{auto:ameb_spi}}

For block data transfers the controller uses DMA. The module's readiness for exchange is reported by the `GPIO0_DREQ_N` signal; its level is visible in `{{ref:spi_status.DREQ}}`. Holding `SPI_CS_N` between bytes is set by the `{{ref:spi_ctrl.CSA}}` bit.

## 6. I²C interface

One hardware controller performs a minimal set of operations: START, STOP, byte transmit, byte receive, and ACK/NACK. Assembling multi-byte packets is done by the processor. This is a deliberate compromise between die size and convenience.

The controller connects to the slots through a multiplexer: the slot number is set in `{{ref:i2c_ctrl.SLOT}}`. This avoids ID-EEPROM address conflicts, and a hung module does not block the others. The multiplexer is implemented in the FPGA (four SDA/SCL pairs) or as an external chip; the pinout on the connector is the same for both options. The speed is fixed: {{const:I2C_KHZ}} kHz.

Typical uses: identification EEPROMs, configuration memory, temperature sensors, power monitoring, simple peripheral controllers.

{{auto:ameb_i2c}}

{{auto:i2c_byte_write}}

An operation is started by writing to the command register; the set of commands is described in {{ref:i2c_cmd}}. The start of a packet is set by the `{{ref:i2c_cmd.START}}` flag, and the end by `{{ref:i2c_cmd.STOP}}`.

## 7. Digital audio interface

### 7.1 General requirements

Digital audio is a mandatory part of AMEB. The interface is logically independent of SPI and I²C, provides a continuous stream, and does not depend on periodic SPI transactions.

### 7.2 Architecture

Synchronous serial TDM interface:

- `AUDIO_BCLK` — bit clock, {{const:BCLK_MHZ}} MHz;
- `AUDIO_FS` — frame sync, {{const:FS_KHZ}} kHz;
- `AUDIO_MCLK` — master clock, {{const:MCLK_MHZ}} MHz (256·fs);
- `AUDIO_DOUT` — data from host to module;
- `AUDIO_DIN` — data from module to host.

The clock signals are common to all slots; the data lines are individual for each slot. This provides common synchronization, independent streams, no electrical conflicts, and flexible routing in the FPGA.

A frame contains {{const:TDM_SLOTS}} time slots of {{const:SLOT_BITS}} bits each, i.e. {{const:FRAME_BITS}} bits. The bus operates only in the {{const:FS_KHZ}} kHz family; modules that need 44.1 kHz will require rate conversion on their side (e.g., a codec ASRC).

{{auto:tdm_frame}}

The frame format (DSP mode A, word length, number of channels per slot) is preliminary and subject to clarification.

### 7.3 Routing

Audio must not physically pass from module to module. The processing chain is built by the host FPGA, for example: host stream → module A → FPGA → module B → FPGA → main audio output. Modules do not connect to each other.

### 7.4 Audio processing on modules

A module can receive audio from the host, process it, return the result, generate sound on its own, or return several channels. Processing can be digital, analog, or hybrid. A module with analog processing contains its own ADCs and DACs; a purely digital module does not need them.

### 7.5 Clocking

All frequencies are derived from the 48 kHz family, so a switchable oscillator is not needed. BCLK ({{const:BCLK_MHZ}} MHz) and MCLK ({{const:MCLK_MHZ}} MHz) are next to each other on the connector (position 18), with no ground between them. If modules do not need a separate MCLK, pin A18 can be returned to DGND, and then zone 2 becomes an alternation of signals and grounds.

## 8. Control signals

The set of signals is given in {{ref:ameb_connector}}:

- `PERIPH_RST_N` — independent module reset in each slot. There is no global `RESET_N`.
- `INT_N` — interrupt request; its level is visible in `{{ref:slot_stat.INT}}`.
- `DETECT_N` — physical presence of the module; its level is visible in `{{ref:slot_stat.PRESENT}}`. The signal works before power is applied and does not depend on I²C.
- `GPIO0_DREQ_N` — module readiness for data exchange (DMA request).
- `GPIO1` — general-purpose output.

A separate NMI is not needed in the base architecture. `DETECT_N` means only physical presence: module readiness is determined through the control interface and recorded by the `{{ref:slot_stat.READY}}` bit.

## 9. DMA architecture

DMA is a logical function of the host FPGA; there is no physical signal for it on the connector, except `GPIO0_DREQ_N`. It services audio streams, module data transfers, and SPI exchange. A shared internal DMA engine with sufficient bandwidth and guaranteed scheduling is acceptable. Four independent physical controllers are not required.

## 10. General-purpose digital pins

Two pins are allocated: `GPIO0` (fixed as `DREQ_N`) and `GPIO1` (module-specific). GPIO must not duplicate the functions of SPI, I²C, and the standard control signals.

## 11. Local DACs and ADCs

The motherboard does not need centralized banks of DACs and ADCs. For example, an analog filter module may contain a multichannel DAC controlled over SPI for cutoff frequency, resonance, gain, modulation depth, or pitch. The resolution, reference voltage, calibration, and update rate are determined by the module itself.

## 12. Analog audio and CV connections

The base connector contains no analog audio inputs, audio outputs, or CV outputs. This eliminates centralized mixing, input buffers, an analog routing matrix, inter-slot analog routing, and a large number of pins.

## 13. Module identification and initialization

Each module contains an ID-EEPROM accessible over I²C. Data: module identifier and type, hardware version, supported audio formats and rates, number of channels, SPI requirements, current consumption, driver compatibility. Physical presence and readiness are different states, and the order in which they are checked is defined in section 4.4.

## 14. Power management and safety

The motherboard manages the power of each slot: monitoring, current limiting, inrush current, short-circuit protection, temperature, safe state on reset and startup. "Hot" insertion is not guaranteed by the connector design alone: modules are installed and removed with power off unless otherwise provided and separately verified. Future hot-plug will require verification of the pin mating sequence, power switching, and signal isolation.

## 15. Project priorities

1. Low overall cost.
2. Minimum number of components on the motherboard.
3. Simple and repeatable module design.
4. Independent operation of modules.
5. Reliable multichannel digital audio.
6. Local analog processing.
7. Efficient use of FPGA resources.
8. Expandability without complicating the connector.

A simple digital module must remain inexpensive, and a complex hybrid module must implement any analog circuit locally, without additional analog sections on the motherboard.

## 16. Open questions

{{auto:open_items}}

---

**Architecture summary**

AMEB-36 is a digital expansion bus on a {{const:PINS}}-pin PCIe x1 connector with independent SPI per slot, a hardware I²C controller with a multiplexer, multichannel digital audio ({{const:BCLK_MHZ}} MHz, {{const:FS_KHZ}} kHz), and bipolar analog power from the host. Analog processing is fully local to the modules, while the host FPGA provides digital communication, audio routing, DMA, and system coordination.