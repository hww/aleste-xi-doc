# Alex — Aleste LX Expansion Bus

## Preliminary Hardware Architecture Specification

## 1. Design Philosophy

Alex (Aleste LX eXpansion) is a modular expansion interface for the Aleste LX computer. It is a computer expansion bus, not a synthesizer or modular-synthesizer interface.

The goal is a compact, inexpensive and versatile slot that avoids the drawbacks of retro slots with 50–60 contacts: large board area, fragility and 5 V only.

The architecture follows five principles:

1. Digital communication and control are handled by the host FPGA. The Z80 treats the slots as peripheral devices through I/O ports; nothing is mapped into memory, because reads from such a window would block the CPU.
2. Audio is transferred digitally between the host and the modules.
3. Analog generation and processing are performed locally on the modules.
4. Analog power (±12 V) is supplied by the host. Analog signals and control voltages stay inside each module, and modules carry no DC/DC converters.
5. Every interface is a hardware block, not a software-emulated one.

The design avoids unnecessary hardware, complex connectors and expensive centralized analog circuitry.

## 2. System Architecture

Alex consists of three subsystems.

### 2.1 Digital Control Plane

Communication and control between the host FPGA and the modules:

- SPI: one independent controller per slot, fed by SysDMA (see section 5).
- I²C: one hardware byte-level controller behind a four-slot multiplexer (see section 6).
- Interrupt `INT_N` and the data-ready request `GPIO0_DREQ_N`.
- A per-slot module reset `PERIPH_RST_N`. There is no global `RESET_N`: the host resets all four slots itself.
- Module presence detection `DETECT_N`.
- One more general-purpose signal, `GPIO1`.

The registers are reached through I/O ports ({{ref:alex_io}}).

{{auto:alex_io}}

### 2.2 Digital Audio Plane

Synchronous multichannel audio between the host FPGA and the modules (see section 7). The host FPGA handles stream distribution and collection, channel routing, digital mixing and DMA between the audio interfaces and system memory.

### 2.3 Local Analog Subsystem

A module may contain its own analog circuitry: filters, oscillators, effects, instrumentation, ADCs and DACs. A module generates its own control voltages, for example with a multichannel DAC controlled over SPI. The host does not generate control voltages.

## 3. Physical Interface

Each slot is a PCIe x1 edge connector with {{const:PINS}} contacts. All {{const:N_SLOTS}} slots are electrically identical. A module is a 1.6 mm board with gold fingers and a chamfer, installed vertically. The fallback is a 1.27 mm pin/socket header, 2×18, which carries the same pinout but has no physical key, so it needs orientation marking and protection against reversed insertion.

The PCIe key between positions 11 and 12 divides the slot into two zones:

- **Zone 1 (positions 1–11, 22 contacts):** power, management and control signals and the reserve. The analog block (positions 1–3) sits at one end, followed by digital power, I²C and control, with the SPI handshake lines next to the key.
- **Zone 2 (positions 12–18, 14 contacts):** the fast digital path only (SPI_SCK, SPI_MOSI, SPI_MISO and audio), with signals alternating with DGND.

The placement was designed by function, independently of PCIe. The placement rules are listed in {{table:slot_zones}}.

{{table:slot_zones}}

{{auto:alex_pcie_edge}}

The contact budget is given in {{table:pin_groups}}. Three contacts (B6, A10, A11) are left in reserve; they can later become extra grounds or be used for extensions.

{{table:pin_groups}}

### 3.1 Inserting a Foreign Module or a PCIe Card

The slot shares only the mechanical form of a PCIe x1 connector. The pinout does not reuse PCIe pin functions, and inserting a real PCIe card is not supported: it may trip the slot protection and must not be attempted on purpose. Protection against faulty or foreign modules relies on host rules:

- +3.3 V is enabled in hardware only while `DETECT_N` is active (a logical AND with the FPGA enable);
- until the ID EEPROM has been read, all host outputs stay Hi-Z and ±12 V stays off;
- current-limiting switches are hardware and do not depend on software.

The position numbering and the key location must be verified against the datasheet of the selected connector.

### 3.2 Electrical and Mechanical Protection

Signals carry TVS arrays and 22–33 Ω series resistors. With an edge connector the mating sequence is provided by the module itself: ground fingers are longer and `DETECT_N` is shorter than the rest.

## 4. Power Distribution

### 4.1 Digital Power

The host supplies +3.3 V on three contacts of each slot. Planning figure: {{const:I_3V3_MA}} mA per slot (an estimate, not a calculation).

### 4.2 Analog Power

The host supplies +12 V and −12 V on one contact each, with four AGND contacts around the pair. Planning figure: {{const:I_12V_MA}} mA per slot on each rail (an estimate, not a calculation).

The ±12 V rails are generated on the motherboard by one boost and one inverting converter; modules carry no DC/DC. Modules are encouraged to add local LDOs on their analog rails. The ±12 V stage can be made optional (DNP) so that a board without analog modules costs less. Any additional voltages are generated locally on the module.

### 4.3 Grounding

DGND and AGND contacts are separate, and every fast line has a DGND contact beside it. DGND and AGND are joined only on the motherboard; a module must not join them, to avoid ground loops. Separate ground contacts do not imply galvanic isolation.

### 4.4 Protection and Power Sequencing

Each slot has current limiting, short-circuit protection and overcurrent detection. +12 V uses a current-limiting switch with an FPGA enable input, and −12 V uses a PTC fuse and is enabled together with +12 V. Protection must not depend only on the FPGA or on software.

+3.3 V is enabled in hardware only while `DETECT_N` is low. The slot is then powered up in order: first +3.3 V alone with the module held in reset, then a read of the ID EEPROM over I²C, and only after a successful check are ±12 V applied.

{{auto:slot_power}}

{{auto:slot_power_seq}}

`{{ref:slot_power.ID_CHECK}}` is the only state in which the module has +3.3 V but not yet ±12 V. `{{ref:slot_ctrl.EN12}}` takes effect only after the identifier has been verified. When protection trips, the slot enters `{{ref:slot_power.FAULT}}`, and the fault is cleared by writing `{{ref:slot_stat.FAULT}}`.

{{auto:alex_slots}}

## 5. SPI Interface

Each slot has its own SPI controller with `SPI_SCK`, `SPI_MOSI`, `SPI_MISO` and `SPI_CS_N`. The physical lines are not shared between slots. The SCK divider (`{{ref:spi_ctrl.DIV}}`) and the clock mode (`{{ref:spi_ctrl.CPOL}}`, `{{ref:spi_ctrl.CPHA}}`) are set per slot. Bit order is MSB first and the word is 8 bits; wider frames are sent as several bytes.

{{auto:spi_mode0}}

### 5.1 Architecture

The SPI controller does not run a protocol. It exchanges blocks of memory with the module and leaves everything above the byte level to the CPU and the module. The controller is a client of the system DMA: the CPU describes a job as "from where, to where, how many", and the hardware executes it.

- **From where / to where:** `SRC_ADDR` of the slot's SysDMA channel is the TX buffer, `DST_ADDR` is the RX buffer.
- **How many:** `SPI_LEN` (16 bits, in bytes).
- **What to do with CS_N:** the `FIRST` and `LAST` flags of `SPI_CMD`.

The controller owns a {{const:FIFO_BYTES}}-byte FIFO for each direction on logic, not block RAM. A DMA request is raised when a FIFO is half empty (TX) or half full (RX), and one grant moves up to {{const:BURST_BYTES}} bytes. The FIFOs connect to SysDMA through an internal port, so SPI traffic does not cross the 8-bit bus; only the memory accesses are charged to the system.

### 5.2 Transfer Modes

{{auto:alex_spi_modes}}

Full-duplex SPI is the natural mode of the pins. On the DMA side, TX_ONLY and RX_ONLY use one stream each, and DUPLEX uses two streams carried by the same DMA channel.

In RX_ONLY the controller sends the byte held in `SPI_FILL` (0xFF by default) for the whole job, so no "repeat one byte" feature is needed in DMA.

### 5.3 Packets

A packet is one or more jobs. The `FIRST` flag asserts `CS_N` before the first byte, and `LAST` releases it after the last byte. A job with neither flag continues the current packet. A short transaction is a single job with both flags.

{{auto:spi_packet}}

A typical register read from a module is two jobs: job 1 (`FIRST`, TX_ONLY) sends the command bytes, job 2 (`LAST`, RX_ONLY) receives the answer. The pause between jobs is harmless because the host owns SCK.

`WAIT_DREQ` makes the job wait for `GPIO0_DREQ_N = 0` before the first byte; the pin level can be read in `{{ref:spi_status.DREQ}}`. The condition is evaluated once per job, not before every byte; a module that needs gaps inside a transfer should be served with several short jobs.

### 5.4 Job Controller

{{auto:spi_job}}

If DMA cannot keep up, the controller does not lose data: it stops SCK at a byte boundary (`STALL`) and resumes when the FIFOs allow. Most SPI slaves tolerate such pauses. `{{ref:spi_status.STALL}}` tells the driver that the bus is saturated so that it can lower the clock. Modules that cannot tolerate gaps in SCK must be listed as such in their ID data and driven with a clock that leaves enough margin.

### 5.5 Registers

{{auto:alex_spi}}

A job is launched by writing `{{ref:spi_cmd.START}}`; `{{ref:spi_cmd.ABORT}}` stops it and flushes both FIFOs. `{{ref:spi_status.DONE}}` is set only after the RX FIFO has been drained to memory, so the CPU can use the buffer as soon as the flag is raised. For occasional single bytes (for example configuring a DAC) the CPU can use `SPI_DATA` directly instead of DMA.

## 6. I²C Interface

One hardware controller performs the minimal operation set: START, STOP, byte transmit, byte receive and ACK/NACK. The CPU assembles multibyte packets. This is a deliberate compromise between FPGA area and convenience.

The controller reaches the slots through a multiplexer; the slot number is set in `{{ref:i2c_ctrl.SLOT}}`. This avoids address conflicts between ID EEPROMs and keeps a hung module from blocking the others. The multiplexer is built either in the FPGA (four SDA/SCL pairs) or as an external chip; the connector pinout is the same in both cases. The speed is fixed at {{const:I2C_KHZ}} kHz.

Typical uses: ID EEPROMs, configuration memory, temperature sensors, power monitors and simple peripheral controllers.

{{auto:alex_i2c}}

{{auto:i2c_byte_write}}

An operation is launched by a write to the command register; the commands are described in {{ref:i2c_cmd}}. A packet starts with `{{ref:i2c_cmd.START}}` and ends with `{{ref:i2c_cmd.STOP}}`.

## 7. Digital Audio Interface

### 7.1 General Requirements

Digital audio is an essential part of Alex. The interface is logically independent of SPI and I²C, provides a continuous stream and does not depend on periodic SPI transactions.

### 7.2 Architecture

A synchronous serial TDM interface:

- `AUDIO_BCLK` — bit clock, {{const:BCLK_MHZ}} MHz;
- `AUDIO_FS` — frame sync, {{const:FS_KHZ}} kHz;
- `AUDIO_MCLK` — master clock, {{const:MCLK_MHZ}} MHz (256·fs);
- `AUDIO_DOUT` — host-to-module data;
- `AUDIO_DIN` — module-to-host data.

The clocks are common to all slots and the data lines are individual per slot. This gives common synchronization, independent streams, no electrical contention and flexible routing in the FPGA.

A frame holds {{const:TDM_SLOTS}} time slots of {{const:SLOT_BITS}} bits, that is {{const:FRAME_BITS}} bits. The bus runs in the {{const:FS_KHZ}} kHz family only; a module that needs 44.1 kHz must convert the rate on its own side (for example with the ASRC of a codec).

{{auto:tdm_frame}}

The frame format (DSP mode A, bit depth, channels per slot) is preliminary.

### 7.3 Routing

Audio never has to pass physically from one module to another. The host FPGA builds the processing chain, for example: host stream → module A → FPGA → module B → FPGA → main audio output. Modules are not connected to each other.

### 7.4 Audio Processing on Modules

A module may receive audio from the host, process it, return the result, generate sound independently or return several channels. Processing may be digital, analog or hybrid. A module with analog processing contains its own ADCs and DACs; a purely digital module needs none.

### 7.5 Clocking

All frequencies come from the 48 kHz family, so no switchable oscillator is needed. Each clock line (BCLK, FS, MCLK) sits between DGND contacts or opposite a DGND contact. If modules never need a separate MCLK, contact B18 can be given to DGND and zone 2 becomes a perfect checkerboard of signals and grounds.

## 8. System Control Signals

The signal set is shown in {{ref:alex_connector}}:

- `PERIPH_RST_N` — independent reset of the module in each slot. There is no global `RESET_N`.
- `INT_N` — interrupt request; its level is visible in `{{ref:slot_stat.INT}}`.
- `DETECT_N` — physical presence; its level is visible in `{{ref:slot_stat.PRESENT}}`. The signal works before power is applied and does not depend on I²C.
- `GPIO0_DREQ_N` — the module is ready for data exchange.
- `GPIO1` — a general-purpose line.

A separate NMI is not needed in the baseline architecture. `DETECT_N` means physical presence only: readiness is determined through the management interface and recorded in `{{ref:slot_stat.READY}}`.

## 9. DMA Architecture

### 9.1 One Master, Eight Channels

All SPI traffic goes through the single system DMA (SysDMA). The architecture deliberately has no per-slot DMA masters and no blitter: every additional bus master brings arbitration, address counters and a risk of starvation. Rectangle copy and blend belong to the GPU, which has direct memory access and a cache.

SysDMA has {{const:DMA_CHANNELS}} channels. Channel state lives in block RAM, so the number of channels barely affects logic. All register banks fit in 8-bit registers (for example one bit per channel in the interrupt mask registers).

{{auto:alex_dma_channels}}

An SPI channel uses the same `SRC_ADDR` and `DST_ADDR` registers as a CPU channel; the peripheral side is hard-wired and needs no address. In TX_ONLY mode only the transmit stream runs, in RX_ONLY only the receive stream, and in DUPLEX both are carried by the same channel. The transfer length comes from `SPI_LEN`, so `COUNT` is ignored for SPI channels.

### 9.2 Arbitration

{{auto:dma_arb}}

Priority is programmable per channel through the extension register.

{{auto:alex_dma_ext}}

With all masks at zero, the lowest channel number wins, so CPU copy channels outrank SPI channels. SPI tolerates this because of the stall mechanism described in section 5.4; when a driver needs the opposite, it raises the mask of the SPI channel.

### 9.3 Bandwidth

The theoretical bandwidth of the SysDMA path is {{const:BUS_PEAK_MBPS}} MB/s; a sustained {{const:BUS_SUSTAINED_MBPS}} MB/s is a planning estimate. The specification does not promise a fixed SPI speed: the controller transfers as much as the bus allows, and the driver chooses the clock. The load of a duplex slot is shown below.

{{auto:spi_load}}

### 9.4 Not a Physical Signal

DMA is a logical function of the host FPGA; the only related line on the connector is `GPIO0_DREQ_N`, which the module uses to say that data is ready. Audio and the GPU remain separate bus masters; their arbitration against SysDMA is an open item.

## 10. General-Purpose Digital I/O

Two signals are provided: `GPIO0` (assigned as `DREQ_N`) and `GPIO1` (module specific). GPIO must not duplicate functions already provided by SPI, I²C and the standard control signals.

## 11. Local DAC and ADC Architecture

The motherboard does not need centralized banks of DACs and ADCs. For example, an analog filter module can contain a multichannel DAC controlled over SPI for cutoff frequency, resonance, gain, modulation depth or oscillator pitch. Resolution, reference voltage, calibration and update rate are determined by the module.

## 12. Analog Audio and CV Connections

The baseline connector has no analog audio inputs, audio outputs or CV connections. This avoids centralized mixing, input buffers, analog routing matrices, analog cross-slot wiring and a large number of contacts.

## 13. Module Identification and Initialization

Each module carries an ID EEPROM reachable over I²C. The data includes the module identifier and type, hardware revision, supported audio formats and sample rates, channel count, SPI requirements (including tolerance for gaps in SCK), current consumption and driver compatibility. Physical presence and readiness are separate states; the order in which they are checked is given in section 4.4.

## 14. Power Management and Safety

The motherboard manages the power of each slot: monitoring, current limiting, inrush current, short-circuit protection, temperature and a safe state during reset and start-up. Hot-plug operation is not guaranteed by the connector alone: modules are installed and removed with the power off unless hot-plug is designed and validated separately. A future hot-plug revision would need validated mating sequence, power switching and signal isolation.

## 15. Design Priorities

1. Low overall system cost.
2. Minimal motherboard component count.
3. Simple and repeatable module design.
4. Independent operation of the modules.
5. Reliable multichannel digital audio.
6. Local analog processing.
7. Efficient FPGA resource use.
8. Expandability without connector complexity.

A simple digital module stays cheap, and a sophisticated hybrid module implements any analog circuit locally, without extra analog hardware on the motherboard.

## 16. Open Items

{{auto:open_items}}

---

**Architectural Summary**

Alex is a digital expansion bus on a {{const:PINS}}-contact PCIe x1 connector. Each slot has an independent SPI controller that exchanges blocks of memory through the system DMA, a shared hardware I²C controller with a multiplexer, multichannel digital audio ({{const:BCLK_MHZ}} MHz bit clock, {{const:FS_KHZ}} kHz frames) and bipolar analog power supplied by the host. Analog processing is local to the modules, while the host FPGA provides digital communication, audio routing, DMA and system coordination.