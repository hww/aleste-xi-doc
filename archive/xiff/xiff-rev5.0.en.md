# **XIFF v5.0 — COMPLETE INTERFACE FRAMEWORK SPECIFICATION**

## **Document: XIFF-SPEC-5.0**

**Status:** Final specification for implementation  
**Date:** 2026-01-11  
**Authors:** Xi Aleste BIOS Development Team

---

## **PART I: INTRODUCTION AND PHILOSOPHY**

### **1.1 Purpose of XIFF**

**XIFF (XI Interface Framework)** is a tool for **automatically generating interfaces** between Z80 assembly code and the C language within the context of the **Xi Aleste BIOS** operating system.

**The Problem XIFF Solves:**
Driver developers write assembly code for maximum performance, but:

- Applications want to use drivers via a C API
- Manually maintaining correspondence between ASM and C functions is labor-intensive and error-prone
- The BIOS specification requires strict formats (64-byte VTables, etc.)

**XIFF's Solution:**
The programmer adds **annotations directly to the ASM code**, and XIFF:

1. **Generates** C headers (.h) and wrappers (.asm, .c)
2. **Verifies** compliance with the BIOS specification
3. **Ensures** type safety between ASM and C

### **1.2 Design Philosophy**

XIFF is based on three principles:

#### **1. Minimalism (KISS)**

- Annotations are added **directly to existing ASM code**
- **No separate Interface Description Language** (IDL)
- **No complex configuration** — specifying output file paths is sufficient

#### **2. C Idiomaticity**

- Data types (`uint8_t`, `const char*`, `bool`) — standard from `stdint.h`
- Syntax (`arg`, `res`) — intuitive for C programmers
- Naming conventions follow Aleste BIOS standards

#### **3. Pragmatism**

- **Doesn't interfere with VS Code or other IDEs** — generates clean C code without inline asm
- **Idempotent generation** — manual code outside XIFF blocks is preserved
- **Phased adoption** — only part of the functions can be annotated

### **1.3 Architecture in the Context of Aleste BIOS**

```text
┌─────────────────────────────────────────────────────────┐
│           C APPLICATION                                 │
│  #include "video.h"                                     │
│  video_draw_pixel(x, y, color);                         │
└──────────────┬──────────────────────────────────────────┘
               │ C function call
┌──────────────▼──────────────────────────────────────────┐
│           GENERATED C CODE (video.c)                    │
│  void video_draw_pixel(uint8_t x, uint8_t y,            │
│                        uint16_t color) {                │
│    _video_draw_pixel_wrapper(x, y, color);              │
│  }                                                      │
└──────────────┬──────────────────────────────────────────┘
               │ ASM wrapper call
┌──────────────▼──────────────────────────────────────────┐
│           GENERATED ASM WRAPPER                         │
│  _video_draw_pixel_wrapper:                             │
│    ld h, iyl        ; x from stack                      │
│    ld l, iyh        ; y from stack                      │
│    ld de, (sp+4)    ; color from stack                  │
│    jp __draw_pixel  ; Jump to real implementation       │
└──────────────┬──────────────────────────────────────────┘
               │ Direct call (17 cycles!)
┌──────────────▼──────────────────────────────────────────┐
│           REAL ASM DRIVER                               │
│  __draw_pixel:                                          │
│    ; ... highly optimized code ...                      │
│    ret                                                  │
└─────────────────────────────────────────────────────────┘
```

---

## **PART II: ANNOTATION SYNTAX AND GRAMMAR**

### **2.1 Basic Format**

All annotations start with `;; XIFF:` and must be placed **immediately before** the annotated element:

```asm
;; XIFF:const -- Screen width in pixels
SCREEN_WIDTH: defc 320

public __draw_pixel
;; XIFF:func __draw_pixel
;;   :arg uint8_t  @h x
;;   :arg uint8_t  @l y
;;   :arg uint16_t @de color
__draw_pixel:
    ; ... implementation ...
    ret
```

### **2.2 Annotation Types**

The anotation expression starts with XIFF then folowig the function name. After there are positioned arguments and key value pairs named *tags*.

```text
; XIFF:function argument1 ... argumentN :key value :key value
```

If there is a following comment line without XIFF there can be other *tags*.

```text
; XIFF:function argument1 ... argumentN :key value :key value
;     :key value :key value
```

There is a special policy, the key without value equals *true*

```text
; XIFF:sum 1 2 :print
```

The key :print returns true as it does not have arguments


#### **2.2.1 Module and File Declaration**

```asm
;; XIFF:export h "include/video.h"
;; XIFF:export inc "inc/video.inc"
;; XIFF:export wrap "src/video_wrap.asm"
;; XIFF:export c "src/video.c"
```

**Explanation:**

- `export h` — generates a C header for `#include`
- `export inc` — generates an ASM header with `extern` declarations
- `export wrap` — generates ASM wrappers for C calling convention
- `export c` — generates clean C proxy functions

#### **2.2.2 Constants**

```asm
;; XIFF:const -- Maximum number of sprites on screen
MAX_SPRITES: defc 128
```

XIFF looks for a label and `defc`/`equ` on the same or next line.

#### **2.2.3 Enumerations**

```asm
;; XIFF:enum VideoMode :type uint8_t
;;   :desc "Video controller operation modes"
VIDEO_MODE_0: defc 0  ;; 256x192, 16 colors
VIDEO_MODE_1: defc 1  ;; 320x200, 4 colors
VIDEO_MODE_2: defc 2  ;; 640x200, monochrome
```

**Attributes:**

- `:type` — C type for enum values (default `int`)
- `:desc` — description for documentation

#### **2.2.4 Structures**

**Method 1: Explicit Structure Declaration**

```asm
;; XIFF:struct Point
;;   :desc "Screen point coordinates"
public _my_point
_my_point:
_x: dw 0  ;; XIFF:field int16_t -- X coordinate
_y: dw 0  ;; XIFF:field int16_t -- Y coordinate
```

**Method 2: Instance Definition**

```asm
;; XIFF:define cursor Point
;;   :desc "Mouse cursor position"
_cursor:
cursor_x: dw 0  ;; XIFF:field int16_t -- X position
cursor_y: dw 0  ;; XIFF:field int16_t -- Y position
```

**Supported Field Types:**

- Basic: `uint8_t`, `int16_t`, `bool`
- Pointers: `const char*`, `void*`, `Point*`
- Arrays: `uint8_t[16]`, `Color[256]`
- Nested structures: `Rect bounds`

#### **2.2.5 Functions and Methods**

```asm
;; XIFF:func __detect_hardware
;;   :desc "Graphics chip detection"
;;   :arg uint8_t @b chip_id -- Chip ID to check
;;   :res bool @c :invert    -- CF=0: found, CF=1: not found
;;   :wrapper fastcall       -- Auto-generate fastcall wrapper
public __detect_hardware
__detect_hardware:
    ; Check chip_id in register B
    ; Set CF=0 if chip found
    ret
```

**Complete List of Function Attributes:**

| Attribute | Format | Description |
|-----------|--------|-------------|
| `:desc` | text | Function description for documentation |
| `:arg` | `type @register name` | Function parameter |
| `:res` | `type @register :attributes` | Return value |
| `:wrapper` | `type` | Type of wrapper to generate (see below) |

**Wrapper Types:**

- `fastcall` — standard fastcall convention (arguments in registers)
- `naked` — minimal wrapper (only `jp` to implementation)
- `z88dk` — compatibility with z88dk C compiler
- `sdcc` — compatibility with SDCC compiler
- `null` — do not generate wrapper (declaration only)

#### **2.2.6 Driver VTable (BIOS Specification)**

```asm
;; XIFF:vtable VideoDriver :size 64
;;   :desc "Video driver virtual method table"
public __video_vtable
__video_vtable:
__video_detect: jp _detect_impl  ;; XIFF:method detect
__video_init:   jp _init_impl    ;; XIFF:method init
; ... remaining methods ...
__video_vtable_end:

;; XIFF:method detect
;;   :desc "Video adapter detection"
;;   :res bool @c :invert  ; CF=0: success
_detect_impl:
    ; Detection implementation
    ret
```

**Key Features:**

- `:size 64` — XIFF verifies table size (BIOS requirement)
- `__video_vtable_end` — label for automatic size calculation
- XIFF verifies presence of 5 mandatory methods: `detect`, `init`, `deinit`, `get_info`, `command`

#### **2.2.7 Driver Events (Commands)**

```asm
;; XIFF:event power_on
;;   :via __video_command    ; Via command() method
;;   :command 0x01           ; POWER_ON command code
;;   :arg uint8_t @a mode    ; Power mode
;;   :res bool @c :invert    ; Execution result
_power_on_handler:
    ; Handle POWER_ON command
    ; A contains mode code
    ret
```

Corresponds to commands from **Section 5 of the BIOS specification**.

---

## **PART III: TYPE SYSTEM AND CONVERSIONS**

### **3.1 Supported Data Types**

XIFF uses standard C99 types:

| XIFF Type              | C Type                           | Size        | Valid Z80 Registers |
|------------------------|----------------------------------|-------------|---------------------|
| `void`                 | `void`                           | 0           | -                   |
| `bool`                 | `bool` (`#include <stdbool.h>`)  | 8 bits      | Flags (Z, C), register A |
| `uint8_t`, `int8_t`    | `uint8_t`, `int8_t`              | 8 bits      | A, B, C, D, E, H, L |
| `uint16_t`, `int16_t`  | `uint16_t`, `int16_t`            | 16 bits     | HL, DE, BC, IX, IY  |
| `uint32_t`, `int32_t`  | `uint32_t`, `int32_t`            | 32 bits     | Register pairs (DE:HL) |
| `void*`, `T*`          | `void*`, `T*`                    | 16 bits     | HL, DE, BC, IX, IY  |
| `const T*`             | `const T*`                       | 16 bits     | HL                  |
| `T[N]`                 | `T name[N]`                      | N*sizeof(T) | HL (address)        |

### **3.2 Register Conventions**

#### **3.2.1 Registers for Parameters**

```asm
;; XIFF:func example
;;   :arg uint8_t  @a first    ; 8-bit in A
;;   :arg uint16_t @hl second  ; 16-bit in HL
;;   :arg uint16_t @de third   ; 16-bit in DE
```

**Rules:**

1. 8-bit types → 8-bit registers (A, B, C, D, E, H, L)
2. 16-bit types → 16-bit registers (HL, DE, BC)
3. Pointers → HL (recommended) or other 16-bit registers

#### **3.2.2 Registers for Return Values**

```asm
;; XIFF:func example
;;   :res uint8_t  @a          ; 8-bit in A
;;   :res uint16_t @hl         ; 16-bit in HL
;;   :res bool @c :invert      ; Logic flag in CF
```

### **3.3 Conversion Attributes**

Attributes are specified after the return type:

```asm
:res type @register :attribute1 :attribute2
```

#### **3.3.1 `:invert` — Logic Inversion**

```asm
;; BIOS: CF=0 means success, but in C true = 1
;; XIFF:func detect
;;   :res bool @c :invert  ; CF=0 → true, CF=1 → false
_detect:
    ; ... detect device
    or a        ; Device found, CF=0
    ret         ; XIFF converts to: return true;
```

#### **3.3.2 `:expand-sign` — Sign Extension**

```asm
;; XIFF:func read_temperature
;;   :res int8_t @a :expand-sign  ; -20..100 → -20..100 (16 bits)
_read_temperature:
    ld a, -20   ; Temperature -20°C
    ret         ; XIFF generates: int16_t, where -20 → 0xFFEC
```

#### **3.3.3 `:saturate` — Saturation on Overflow**

```asm
;; XIFF:func add_safe
;;   :arg uint8_t @a x
;;   :arg uint8_t @b y  
;;   :res uint8_t @a :saturate  ; 200+100 → 255, not 44
_add_safe:
    add a, b    ; 200 + 100 = 44 (with carry)
    ret         ; XIFF generates saturation to 255
```

#### **3.3.4 `:truncate` — Truncation**

```asm
;; XIFF:func get_high_byte
;;   :res uint16_t @hl
;;   :res uint8_t @a :truncate  ; Take only low byte
_get_high_byte:
    ld hl, 0x1234
    ld a, h     ; = 0x12
    ret
```

### **3.4 Naming Conventions (Prefixes)**

**Key Rule:** The prefix determines how XIFF handles a function.

| Prefix | Example | XIFF Handling | Usage |
|--------|---------|---------------|-------|
| `_` (single) | `_init` | **Declaration only** in C | Function already C-compatible |
| `__` (double) | `__detect` | **Generate wrapper** | Pure ASM function |
| (none) | `local_func` | Ignored | Module internal function |

**Examples:**

```asm
;; 1. Already C-compatible (e.g., compiled by z88dk)
public _c_compatible_func
;; XIFF:func _c_compatible_func
;;   :arg uint16_t @hl value
_c_compatible_func:
    ; ... code compatible with C calling convention ...
    ret

;; 2. Pure ASM, needs wrapper
public __pure_asm_func  
;; XIFF:func __pure_asm_func
;;   :arg uint8_t @a param
__pure_asm_func:
    ; ... pure ASM, can clobber any registers ...
    ret  ; XIFF will generate wrapper
```

---

## **PART IV: FILE GENERATION AND FORMATS**

### **4.1 Generation Process**

```text
Driver source file (driver.asm)
        │
        ▼ (Parsing XIFF annotations)
        │
        ├───▶ inc/driver.inc      (extern declarations)
        ├───▶ include/driver.h    (C header)  
        ├───▶ src/driver_wrap.asm (ASM wrappers)
        └───▶ src/driver.c        (C proxy functions)
```

### **4.2 Generated File Formats**

#### **4.2.1 ASM Header (.inc)**

```asm
; File: inc/video.inc
; GENERATED BY XIFF. DO NOT EDIT MANUALLY.
; XIFF:start "drivers/video/video.asm"

extern SCREEN_WIDTH
extern SCREEN_HEIGHT  
extern __video_detect
extern __video_init

; XIFF:end
```

#### **4.2.2 C Header (.h)**

```c
/* File: include/video.h */
/* GENERATED BY XIFF. DO NOT EDIT MANUALLY. */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include <stdint.h>
#include <stdbool.h>

/* XIFF:start "drivers/video/video.asm" */

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 200

typedef enum {
    VIDEO_MODE_0 = 0,
    VIDEO_MODE_1 = 1
} VideoMode;

bool video_detect(uint8_t chip_id);
bool video_init(VideoMode mode);

/* XIFF:end */

#endif /* _VIDEO_H_ */
```

#### **4.2.3 ASM Wrapper (_wrap.asm)**

```asm
; File: src/video_wrap.asm
; GENERATED BY XIFF. DO NOT EDIT MANUALLY.
; XIFF:start "drivers/video/video.asm"

.module video_wrap
.include "video.inc"

; bool video_detect(uint8_t chip_id)
_video_detect_wrapper:
    pop hl          ; Save return address
    pop bc          ; Get chip_id from stack
    push hl         ; Restore return address
    ld b, c         ; chip_id in B for __video_detect
    call __video_detect
    ld a, 0         ; Assume false
    jr c, .no_detect
    inc a           ; true = 1
.no_detect:
    ld l, a
    ret

; XIFF:end
```

#### **4.2.4 C Proxy File (.c)**

```c
/* File: src/video.c */
/* GENERATED BY XIFF. DO NOT EDIT MANUALLY. */
/* XIFF:start "drivers/video/video.asm" */

#include "video.h"

extern bool _video_detect_wrapper(uint8_t chip_id);

bool video_detect(uint8_t chip_id) {
    return _video_detect_wrapper(chip_id);
}

/* XIFF:end */
```

### **4.3 Idempotent Generation (Smart Merge)**

**Problem:** A programmer edits a `.h` file, adding manual definitions, and XIFF overwrites the file.

**Smart Merge Solution:**

1. **XIFF reads the target file** (e.g., `video.h`)
2. **Looks for blocks** `/* XIFF:start "source.asm" */` ... `/* XIFF:end */`
3. **If found:**
   - Replaces block contents
   - Preserves everything outside blocks
4. **If not found:**
   - Adds a new block at the end of the file
5. **Always preserves:**
   - `#ifndef` guards
   - `#include` directives outside blocks
   - Comments outside blocks

**Example Operation:**

```c
/* video.h BEFORE generation */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include "common.h"  <!-- Preserved

/* Manual optimization for ARM */
#ifdef __ARM_ARCH
#define FAST_MODE 1
#endif

/* XIFF:start "drivers/video/video.asm" */
// OLD generated code
/* XIFF:end */

// Additional manual functions
void manual_helper(void);  <!-- Preserved

#endif
```

After generation:

```c
/* video.h AFTER generation */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include "common.h"  <!-- Preserved!

/* Manual optimization for ARM */
#ifdef __ARM_ARCH
#define FAST_MODE 1
#endif

/* XIFF:start "drivers/video/video.asm" */
// NEW generated code (updated)
#define SCREEN_WIDTH 320
bool video_detect(uint8_t chip_id);
/* XIFF:end */

// Additional manual functions
void manual_helper(void);  <!-- Preserved!

#endif
```

---

## **PART V: INTEGRATION WITH ALESTE BIOS SPECIFICATION**

### **5.1 Support for BIOS Driver Architecture**

XIFF ensures compliance with **Section 2** of the BIOS specification:

#### **5.1.1 Singleton vs Polymorphic Drivers**

```asm
;; SINGLETON driver (e.g., system timer)
;; XIFF:vtable SystemTimer :size 64
;;   :singleton            ; Only one implementation
__sys_timer_vtable:
    jp _timer_init
    ; ...

;; POLYMORPHIC driver (e.g., video)
;; XIFF:vtable VideoDriver :size 64
;;   :polymorphic          ; Multiple implementations
;;   :parent Graphics      ; Inherits Graphics methods
__video_vtable:
    jp _video_detect
    ; ...
```

#### **5.1.2 Mandatory Methods (Section 2.2 of Specification)**

XIFF **automatically verifies** the presence of 5 mandatory methods:

1. **detect()** — device detection
2. **init()** — initialization
3. **deinit()** — deinitialization
4. **get_info()** — get information
5. **command()** — execute commands

**Example Declaration:**

```asm
;; XIFF:vtable StorageDriver :size 64
__storage_vtable:
__storage_detect:   jp _storage_detect
;; XIFF:method detect
;;   :desc "SD card detection"
;;   :res bool @c :invert
_storage_detect:
    ; ... check for SD card presence ...
    ret
```

### **5.2 VTable Size Verification**

The BIOS specification requires **64-byte VTables**. XIFF verifies:

```asm
;; XIFF:vtable AudioDriver :size 64  <!-- Explicit specification
public __audio_vtable
__audio_vtable:
    ; 21 slots × 3 bytes = 63 bytes
    ; XIFF will warn about mismatch
__audio_vtable_end:

public __audio_vtable_size
__audio_vtable_size: defc __audio_vtable_end-__audio_vtable
```

**Rules:**

- If `:size` is specified — exact match is verified
- If not specified — verified that size ≥ required
- Warning if there are unused bytes

### **5.3 Support for MemoryContext (Section 4 of Specification)**

```asm
;; XIFF:struct MemoryContext
public _video_context
_video_context:
_hash:      db 0  ;; XIFF:field uint8_t  -- XOR hash of configuration
_slot_reg:  db 0  ;; XIFF:field uint8_t  -- Slot register
_window0:   db 0  ;; XIFF:field uint8_t  -- Window 0 bank
_window1:   db 0  ;; XIFF:field uint8_t  -- Window 1 bank
_window2:   db 0  ;; XIFF:field uint8_t  -- Window 2 bank
_window3:   db 0  ;; XIFF:field uint8_t  -- Window 3 bank
_flags:     db 0  ;; XIFF:field uint8_t  -- Context flags
_reserved:  db 0  ;; XIFF:field uint8_t  -- Alignment
```

XIFF generates the corresponding C struct:

```c
typedef struct {
    uint8_t hash;
    uint8_t slot_reg;
    uint8_t window0;
    uint8_t window1;
    uint8_t window2;
    uint8_t window3;
    uint8_t flags;
    uint8_t reserved;
} MemoryContext;

extern MemoryContext video_context;
```

### **5.4 Support for Commands (Section 5 of Specification)**

```asm
;; XIFF:event set_video_mode
;;   :via __video_command      ; Called via command()
;;   :command 0x40            ; SET_MODE command code
;;   :arg uint8_t @a mode     ; Video mode
;;   :res bool @c :invert     ; Result
_set_video_mode:
    ; Handle command 0x40
    ; A contains video mode
    ret
```

XIFF generates the C function:

```c
bool video_set_mode(uint8_t mode);
```

And verifies that command codes are in the correct ranges (0x40-0x5F for video).

---

## **PART VI: COMMAND LINE INTERFACE**

### **6.1 Main Commands**

```
xiff <command> [options] <files>
```

#### **6.1.1 `parse` — Parsing and Syntax Checking**

```
xiff parse driver.asm
xiff parse --verbose *.asm
xiff parse --output errors.txt drivers/
```

**Checks:**

- Annotation syntax correctness
- Type and register compatibility
- Presence of required labels (`public`, `defc`)

#### **6.1.2 `generate` — File Generation**

```
xiff generate driver.asm
xiff generate --force driver.asm    # Overwrite without Smart Merge
xiff generate --inc-only driver.asm # Only .inc files
```

#### **6.1.3 `validate` — BIOS Specification Verification**

```
xiff validate driver.asm
xiff validate --strict driver.asm  # Errors instead of warnings
```

**Checks:**

- VTable size = 64 bytes
- Presence of 5 mandatory methods
- MemoryContext structure correctness
- Command code range compliance

#### **6.1.4 `diff` — Show Changes**

```
xiff diff driver.asm          # What will change on generation
xiff diff --color driver.asm  # Color output
```

### **6.2 Logging Levels**

```bash
xiff generate file.asm           # Level 1: Normal (errors only)
xiff generate file.asm -v        # Level 2: Verbose (+ warnings)
xiff generate file.asm -vv       # Level 3: Debug (+ parsing details)
xiff generate file.asm -vvv      # Level 4: Trace (for development)
```

**Message Format:**

```
[level][component] message
[info][parser] Processing video.asm
[warn][vtable] VTable video_driver: 63 bytes, expected 64
[error][type] Incompatible type: uint16_t in 8-bit register A
```

### **6.3 Configuration File**

XIFF looks for `.xiffrc` in the current directory or home directory:

```json
{
  "version": "5.0",
  "output": {
    "inc_dir": "inc",
    "h_dir": "include",
    "wrap_dir": "src",
    "c_dir": "src",
    "backup": true
  },
  "validation": {
    "check_vtable_size": true,
    "check_mandatory_methods": true,
    "warnings_as_errors": false
  },
  "code_style": {
    "c_prefix": "",
    "asm_prefix": "__",
    "indent": "  ",
    "comment_style": "c"  // "c" or "asm"
  },
  "compiler": {
    "default_wrapper": "fastcall",
    "c_standard": "c99",
    "stdint_header": "<stdint.h>"
  }
}
```

---

## **PART VII: PRACTICAL EXAMPLES**

### **7.1 Complete Sound Driver Example**

```asm
;; ============================================
;; sound.asm - AY-3-8910 Sound Driver
;; ============================================

;; XIFF:export h "include/sound.h"
;; XIFF:export inc "inc/sound.inc"
;; XIFF:export wrap "src/sound_wrap.asm"

;; Constants
;; XIFF:const -- Sampling frequency
SAMPLE_RATE: defc 44100

;; XIFF:enum Note :type uint8_t
;;   :desc "MIDI notes (0-127)"
NOTE_C4:  defc 60
NOTE_D4:  defc 62
NOTE_E4:  defc 64

;; State structure
;; XIFF:struct AYState
public _ay_state
_ay_state:
_registers: ds 16  ;; XIFF:field uint8_t[16] -- Register shadows
_volume:    db 15  ;; XIFF:field uint8_t     -- Volume 0-15
_muted:     db 0   ;; XIFF:field bool        -- Mute flag

;; Driver VTable
;; XIFF:vtable SoundDriver :size 64
;;   :polymorphic  ; Support for different chips
public __sound_vtable
__sound_vtable:
__sound_detect:   jp _sound_detect
__sound_init:     jp _sound_init
__sound_deinit:   jp _sound_deinit
__sound_get_info: jp _sound_get_info
__sound_command:  jp _sound_command
__sound_play:     jp _sound_play_note
; ... remaining 16 methods ...
__sound_vtable_end:

;; Detection method
;; XIFF:method detect
;;   :desc "AY-3-8910 detection"
;;   :res bool @c :invert
public __sound_detect
_sound_detect:
    ; ... detection code ...
    or a        ; CF=0 if found
    ret

;; Note playback method
;; XIFF:method play_note
;;   :desc "Play note on channel"
;;   :arg uint8_t @a note     ; MIDI note (0-127)
;;   :arg uint8_t @b channel  ; Channel (0-2)
;;   :res bool @c :invert     ; Operation success
public __sound_play_note
_sound_play_note:
    ; ... playback code ...
    or a        ; CF=0 if successful
    ret

;; Power control command
;; XIFF:event power_control
;;   :via __sound_command
;;   :command 0x01            ; POWER_ON/POWER_OFF
;;   :arg uint8_t @a state    ; 1=on, 0=off
;;   :res bool @c :invert
_power_control:
    ; ... power handling ...
    or a
    ret
```

### **7.2 Generation and Usage**

```bash
# Generate interfaces
xiff generate sound.asm

# Verify BIOS compliance
xiff validate sound.asm

# Use in C program
```

**C Program:**

```c
#include "sound.h"

int main() {
    // Detect sound chip
    if (!sound_detect()) {
        printf("Sound chip not found\n");
        return 1;
    }
    
    // Initialization
    if (!sound_init()) {
        printf("Sound initialization error\n");
        return 1;
    }
    
    // Play note
    sound_play_note(NOTE_C4, 0);  // Note C4 on channel 0
    
    // Power control
    sound_power_control(0);  // Turn power off
    
    return 0;
}
```

---

## **PART VIII: REQUIREMENTS AND LIMITATIONS**

### **8.1 System Requirements**

- **Python 3.8+** or **C++17 compiler** (for native version)
- **Assembler:** sjasmplus (primary), z80asm (alternative)
- **File Encoding:** UTF-8 (recommended) or CP866
- **Operating System:** Any (Windows, Linux, macOS)

### **8.2 MVP Limitations**

**First version (MVP) supports:**

1. Basic data types (`uint8_t`, `uint16_t`, `bool`, pointers)
2. Functions with up to 3 parameters
3. VTable size verification
4. Generation of `.inc`, `.h`, `_wrap.asm` files
5. Smart Merge for idempotent generation

**Future versions will add:**

1. Support for `float` and `double` types
2. Callback functions (function pointers)
3. Documentation generation (Doxygen, Markdown)
4. Plugins for VS Code and other IDEs
5. Support for other assemblers (NASM, AS)

### **8.3 Error Handling**

XIFF distinguishes three levels of issues:

| Level | Example | Action |
|-------|---------|--------|
| **Error** | Unknown directive, incompatible types | Stop generation |
| **Warning** | VTable 63 bytes instead of 64, unused methods | Continue, report |
| **Information** | Generated X files, used Y annotations | Only in verbose mode |

---

## **PART IX: DEVELOPMENT PLAN**

### **Phase 1: Basic Parser**

- [ ] Parsing `;; XIFF:` annotations
- [ ] Support for `export`, `const`, `enum`
- [ ] Generation of `.inc` files
- [ ] `parse` command

### **Phase 2: C Interface Generation**

- [ ] Support for `func`, `arg`, `res`
- [ ] Generation of `.h` and `_wrap.asm`
- [ ] Conversion attributes (`:invert`, `:expand-sign`)
- [ ] `generate`, `diff` commands

### **Phase 3: BIOS Specification Support**

- [ ] Structures and `struct`
- [ ] VTable and `vtable`, `method`
- [ ] 64-byte size verification
- [ ] Mandatory driver methods
- [ ] `validate` command

### **Phase 4: Advanced Capabilities**

- [ ] Smart Merge (idempotent generation)
- [ ] Configuration file `.xiffrc`
- [ ] Events (`event`) and commands
- [ ] MemoryContext structures

### **Phase 5: Testing and Documentation**

- [ ] Tests on real Aleste BIOS drivers
- [ ] Documentation with examples
- [ ] Build process integration
- [ ] Release v1.0.0

---

## **PART X: CONCLUSION AND STATUS**

### **10.1 Current Status**

✅ **Specification complete** — all aspects covered  
✅ **Syntax defined** — annotations, types, attributes  
✅ **Architecture clear** — parser → generator → validator  
✅ **Integration defined** — with BIOS, C compilers, CI/CD  

### **10.2 Key Innovations**

1. **C Idiomaticity in ASM annotations** — natural for developers
2. **Smart Merge** — protects manual code during generation
3. **Automatic BIOS specification verification** — compatibility guarantee
4. **Pragmatic design** — solves real problems without excess

### **10.3 Next Steps**

1. **Approve specification** as team standard
2. **Create repository** on GitHub with this documentation
3. **Begin implementation** of parser in Python 3.10+
4. **Test** on sound driver from Appendix A of original specification

---

## **APPENDIX A: COMPARISON WITH ALTERNATIVES**

| Characteristic | **XIFF** | SWIG | CTypes | Manual Development |
|----------------|----------|------|--------|--------------------|
| **Target Platform** | Z80 + Aleste BIOS | Cross-platform | Python + C | Any |
| **Syntax** | Annotations in ASM | Separate IDL file | Descriptions in Python | C and ASM code |
| **BIOS Verification** | **Yes, automatic** | No | No | Manual |
| **Wrapper Generation** | **Automatic** | Yes | Runtime | Manual |
| **Implementation Complexity** | Low | Medium | Low | High |
| **Performance** | **Maximum** (optimized for Z80) | Medium | Low | Depends on developer |

---

## Small Nuances to Keep in Mind (For Implementation)

- `:via` directive in events: In the `set_video_mode` example, `:via __video_command` is used. Ensure the generator will verify that this `__video_command` function exists in the current module, otherwise the linker will throw an error.
- `bool` type in Z80: Since C's `stdbool.h` typically defines `true` as 1, and in ASM we often use flags, your idea with the `:invert` attribute remains key. It should be strictly fixed in the generator code that `:invert` for the Carry flag (`@c`) means: CF=0 -> `return true`.
- Register pairs for 32-bit: Table 3.1 mentions `uint32_t` and the DE:HL pair. This is very useful for working with LBA sectors on SD cards. The parser should account for `@dehl` as a single composite register.

**XIFF v5.0 is ready for implementation.** This specification provides a complete, self-contained guide for creating a tool that will significantly simplify driver development for Xi Aleste BIOS while preserving all the advantages of hand-optimized assembly code.
