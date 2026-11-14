# Aleste LX: The Philosophy of Programmable Graphics

### Why Software Solutions Can Surpass Hardware

There has always been one interesting fundamental idea in the Aleste architecture: **software solutions can surpass hardware**.

Today this statement may seem quite natural, but in the days of eight-bit computers it was rather controversial. Nevertheless, this is precisely the conclusion we gradually reached during the development process.

At the very beginning, we were, of course, captivated by the hardware capabilities of the MSX video processor. It seemed like a practically ideal solution: specialized logic performed graphics operations quickly, in hardware, and without significant load on the main processor. It seemed to be exactly what was needed.

But over time our attitude changed.

We began to see the other side of hardware specialization. The capabilities of the video processor, however impressive they seemed, were rigidly limited by its architecture. Game developers wanted more: to go beyond the provided hardware capabilities, but they encountered an insurmountable wall — the closed set of functions of the video controller.

Of course, software tricks existed: sprite virtualization, various ways of increasing their number on screen, and other workarounds. But all of this remained an attempt to circumvent the limitations of the hardware.

The turning point for us was the implementation of an MSX VDP simulator on Aleste, which allowed MSX games to be run by emulating the video processor in software on the main processor.

That was when we truly saw how far one can go if, instead of a fixed set of hardware functions, you provide the developer with computational resources and the freedom to use them.

Since then our philosophy has changed: **a good architecture should provide the programmer with a sufficiently powerful computing machine, rather than predetermining which graphical effects they can create.**

This is precisely the principle underlying the graphics subsystem of Aleste LX.

### Not a Video Controller, but an Additional Processor

We did not design a traditional video controller with hardware layers, tile graphics, sprites, and a cursor.

Instead, we decided to offer the developer an additional graphics processor. Moreover, not merely a device performing a fixed set of graphics operations, but a full-fledged programmable processor for which one can write and run custom programs.

Its main task is to receive data from graphics memory, process it according to the program being executed, and write the result back.

This approach opens up far more possibilities than traditional specialized graphics logic.

### Evolution of the Architecture

The initial version of the graphics processor was implemented entirely in hardware. It contained separate functional units, each performing its own task: some interpolated coordinates, others converted coordinates into memory addresses, others converted pixels, and still others performed image blending.

It was a complex and rather large design. As the project developed, we began to look for more universal architectural solutions.

All subsequent variants shared one idea: the graphics subsystem should be an additional processor that independently executes a program and works with the graphics buffer.

The first programmable version was built on the principles of a signal processor. It had a large register file and dedicated operand and result registers. The word size was 24 bits, which allowed efficient computation of addresses across the entire memory space.

The next version used a stack architecture. The processor had a small three-register stack and a separate register file. This allowed very compact program code, but limitations emerged related to pipeline organization: while the arithmetic-logic unit was computing a result, the stack could not be modified.

Therefore we moved to the next architecture — also 24-bit, but with a two-operand instruction system. One operand was read from a register, and the result of the computation was written back to the register file. Instruction execution in the pipeline took two cycles.

All three architectures used a 36-bit instruction field and belonged to the VLIW class.

However, synthesis in FPGA showed that such an architecture places too high demands on hardware resources.

As a result, we made an important decision: to move to a more compact core with a 16-bit external memory bus and a 32-bit instruction, which fits within FPGA resources without sacrificing performance in graphics tasks. This also made it possible to store graphics processor programs in compact form and load them by means of the Z80.

Thus the architecture that formed the basis of Aleste LX came into being.

### Design of the Graphics Processor

In its final form, this is a processor with 32 general-purpose registers 24 bits wide and another 32 peripheral registers. The core operates on 24-bit data; with external memory the processor communicates over a 16-bit bus.

The peripheral registers serve as an interface to the processor's devices. In concept they resemble the input/output ports of traditional computers.

The microprogram memory is loaded through a streaming port: a new program can be loaded at any moment, without the involvement of any additional logic.

Memory access ports play a particularly important role.

The port takes upon itself all the "low-level" work with memory: the processor reads or writes a pixel with a single instruction, while the port itself converts the pixel index into the address of a 16-bit memory word, extracts or packs the required pixel, and buffers the accesses. The port automatically advances the index by a specified step (including in the reverse direction), so sequential arrays are processed naturally.

Formats of 1, 4, 8, and 16 bits per pixel are supported, as well as pass-through modes for byte-by-byte operation. The 1-bit-per-pixel format is available for reading only.

For example, when reading a monochrome image, the port automatically converts each bit of the source data into the color format understood by the graphics processor. Similar conversions are performed when writing.

Thus the processor itself works with pixels and does not concern itself with how they are physically packed in memory.

For affine transformations — rotations, scaling, skewing — the microcode uses a fixed-point representation (16 bits of integer part and 16 bits of fractional part). This is a programming convention, not a separate hardware function: the processor remains simple, and complex behavior is defined by the program.

### Caching and Memory Operation

Accesses to external memory are cached. The cache stores data, tags, and dirty bits that allow clean lines to be distinguished from modified ones.

The main purpose of caching is to reduce the number of accesses to main memory. Data does not need to be immediately written back after every change: writing is performed when it is truly necessary, and an explicit flush command makes memory coherent.

The ports operate independently of each other and halt the core in hardware if data is not yet ready — the program does not waste time waiting for memory.

### How the Whole System Works

Let us imagine a typical usage scenario.

The main Z80 processor loads the graphics processor program by passing it to the loader as a stream of packets: a code packet contains the load address and the instructions themselves, a separate command starts the program at a given entry point, and completion may be accompanied by an interrupt for the Z80.

Inside the graphics processor there is a small loader. It receives the stream, writes the microprogram into instruction memory, and, if so specified, transfers control to the loaded code.

After that, control is transferred to the main program.

Suppose we want to draw a set of sprites. In memory there is a list of objects with their sizes, graphics data addresses, coordinates, rotation angles, and scale.

The GPU program sequentially reads these descriptions and performs the drawing.

To do this it uses the ports as follows:

- The source port reads the graphics data of the sprites, automatically unpacking it from the source format.
- The destination port writes the result to the framebuffer, automatically packing pixels into the screen memory format.
- The streaming port, through which the microcode is loaded, can be used to read object descriptions and any other sequential data.

Thus the processor independently performs all the work of transforming coordinates, processing graphics data, and forming the image.

Moreover, the described scenario is only one of the possible ways of using the architecture.

In total the processor has four such streams, and therefore the fourth one can be used by the programmer to create more complex effects, such as pixel deformation or a drawing mask.

### Not Only Graphics

Although we call this device a graphics processor, its capabilities are significantly broader.

On board there is a hardware 16 × 16 bit multiplier (two operations: lower and upper bits of the product), a fairly powerful arithmetic-logic unit, and programmable memory access ports.

This allows it to be used not only for image processing, but also for any other tasks that lend themselves well to parallel or batch processing.

For example, it can perform operations on data arrays, work as a DMA processor, process audio streams, or perform specialized computations.

In essence, it is an additional computational resource that the developer can use at their discretion.

### Why Not More Powerful?

One may ask a legitimate question: why did we not make the processor more powerful — with a larger word size, a more complex instruction system, and a rich set of hardware functions?

The answer is quite practical: FPGA has a limited amount of hardware resources, and the bottleneck of any graphics system is memory, not arithmetic.

Our task was not to create the most powerful processor at any cost, but to place an additional computational resource that genuinely benefits the entire system. A simple core executing one instruction per cycle, a multiplier on DSP blocks, and ports that take upon themselves address arithmetic and pixel packing provide exactly the performance that memory is able to "feed."

Even in this form, this processor surpasses the Z80 many times over in the tasks for which it is intended.

The Z80, running at 16 MHz, executes one instruction over several cycles. Its computational resources are also spent on servicing interrupts, running system software, and maintaining the functioning of the entire system.

The graphics processor is free from these duties. It has a more productive memory bus, specialized data access mechanisms, and an instruction system oriented toward efficient graphics processing.

Therefore even a relatively simple coprocessor is capable of providing a completely different level of performance in its area of application.

### In Lieu of a Conclusion

At the heart of Aleste LX lies a simple idea: there is no need to limit the developer in advance by the capabilities of the hardware.

It is better to provide them with a computing machine, access to memory, and tools for efficient data processing.

We do not know in advance what graphical effects developers will want to create. And that is precisely why we do not want to limit them to a set of functions provided for during the design of the video controller.

**A good graphics processor can draw many different things. But a magnificent one is the one that can draw things its creators did not even suspect.**