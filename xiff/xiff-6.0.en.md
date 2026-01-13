# **XIFF v6.0 — COMPLETE INTERFACE FRAMEWORK SPECIFICATION (SOOT Edition)**

## **Document: XIFF-SPEC-6.0**

**Status:** Final draft for implementation (SOOT-based)  
**Date:** 2026-01-13  
**Authors:** Xi Aleste BIOS Development Team

---

## **PART I: INTRODUCTION AND PHILOSOPHY**

### **1.1 Purpose of XIFF**

**XIFF (XI Interface Framework)** is a tool for **automatically generating interfaces** between Z80 assembly code and the C language within the context of the **Xi Aleste BIOS** operating system.

**The Core Innovation:** Replace custom annotation syntax with a **LISP-based DSL** (SOOT language) embedded directly in assembly comments. This provides unprecedented flexibility while maintaining simplicity.

**The Problem XIFF Solves:**
Driver developers write optimized Z80 assembly, but applications need clean C APIs. Manual interface maintenance is error-prone and time-consuming.

**XIFF's Solution:**
Programmers add **SOOT expressions in assembly comments**, and XIFF:
1. **Executes** SOOT code to build an interface model
2. **Generates** C headers, wrappers, and proxy functions  
3. **Verifies** compliance with BIOS specification
4. **Ensures** type safety between assembly and C

### **1.2 Design Philosophy**

XIFF v6.0 is based on four core principles:

#### **1. Embedded LISP (SOOT)**
- **No custom syntax** — uses standard SOOT/LISP expressions
- **Full programming power** — conditions, loops, macros in annotations
- **Extensible** — users can define their own annotation functions

#### **2. Positional Binding**
- `;<` annotation binds to **previous** label
- `;!` annotation executes in **file context**  
- `;>` annotation binds to **next** label (rare)
- **Minimal duplication** — labels referenced from assembly, not re-typed

#### **3. Moderately Smart Parser**
- **Understands** basic ASM: labels, public/extern, data directives
- **Ignores** complex instructions — semantics in SOOT annotations
- **Context-aware** — tracks label positions for binding

#### **4. Pragmatic Generation**
- **Idempotent** via FileInjector
- **BIOS-compliant** — automatic VTable validation
- **Performance-first** — generates optimized Z80 wrappers

### **1.3 Architecture Overview**

```text
┌─────────────────────────────────────────────┐
│         ASM SOURCE WITH ANNOTATIONS         │
│   label:                                    │
│       dw 100                                │
│       ;< (x-field 'int16_t :signed #t)      │
└──────────────┬──────────────────────────────┘
               │ 1. Parsing & SOOT Execution
┌──────────────▼──────────────────────────────┐
│          XIFF CORE (SOOT ENVIRONMENT)       │
│   • Executes annotation expressions         │
│   • Maintains registry of interface objects │
│   • Validates against BIOS spec             │
└──────────────┬──────────────────────────────┘
               │ 2. Target Generation
┌──────────────▼──────────────────────────────┐
│           FILE GENERATION                   │
│   • C headers (.h)                          │
│   • ASM wrappers (.asm)                     │
│   • C proxy functions (.c)                  │
│   • ASM includes (.inc)                     │
└──────────────┬──────────────────────────────┘
               │ 3. Smart Injection
┌──────────────▼──────────────────────────────┐
│         FINAL OUTPUT FILES                  │
│   • Preserves manual code                   │
│   • Updates generated blocks                │
│   • Ready for compilation                   │
└─────────────────────────────────────────────┘
```

---

## **PART II: ANNOTATION SYNTAX AND GRAMMAR**

### **2.1 Annotation Types and Binding**

#### **2.1.1 Basic Annotation Format**

```asm
;! (x-module "video")                    ; File-level directive
label:                                  ; ASM label
    dw 100                              ; Data directive
    ;< (x-field 'int16_t :signed #t)    ; Bound to previous label
```

#### **2.1.2 Three Annotation Types**

| Prefix | Direction | Use Case | Example |
|--------|-----------|----------|---------|
| `;!` | File context | Module directives, exports, VTables | `;! (x-export-h "video.h")` |
| `;<` | Backward binding | Fields, constants, functions | `;< (x-const 'uint16_t)` |
| `;>` | Forward binding | Rare, for special cases | `;> (x-next-label 'foo)` |

#### **2.1.3 Multi-line Annotations**

```asm
;! (x-func '__draw_pixel
;!   :args '((x . uint8_t @h)
;!           (y . uint8_t @l))
;!   :return 'void
;!   :desc "Draws a pixel on screen")
```

**Parsing Rule:** XIFF concatenates consecutive annotation lines until a non-annotation line is encountered.

### **2.2 SOOT Language Primer for XIFF**

XIFF uses SOOT (Scheme-like Object-Oriented Toolkit) with these conventions:

#### **2.2.1 Core Functions (x- prefix)**

```lisp
; Constants and data
(x-const type &key name desc)           ; Define constant
(x-field type &key signed array-size name) ; Structure field

; Functions and methods  
(x-func name &key args return desc)     ; Function declaration
(x-method name &key args return desc)   ; VTable method

; Structures and types
(x-struct name &key fields size)        ; Structure definition
(x-enum name &key values type)          ; Enumeration

; Export directives
(x-export-h "path/to/header.h")         ; Export C header
(x-export-c "path/to/source.c")         ; Export C source
(x-export-asm "path/to/wrapper.asm")    ; Export ASM wrapper
(x-export-inc "path/to/include.inc")    ; Export ASM include

; VTable management
(x-begin-vtable name &key size type)    ; Start VTable definition
(x-vtable-method name &key target)      ; Add method to VTable
(x-end-vtable)                          ; End VTable definition
```

#### **2.2.2 Short Name Import**

For convenience, short names can be imported:

```asm
;! (using 'xiff/short)      ; Import short names (optional)

;< (const 'uint16_t)        ; Now works without x- prefix
;< (field 'int16_t :signed #t)
```

### **2.3 What the Parser Understands**

#### **2.3.1 Automatic Recognition**

```asm
; Labels (ends with :)
MY_LABEL:                 ; Recognized as label
ANOTHER_LABEL:            ; Another label

; Public/Extern directives  
public func1, func2       ; Recognized, names extracted
extern _external_func     ; Recognized

; Data directives
db 1, 2, 3                ; Byte data
dw 1000, 2000             ; Word data  
ds 100                    ; Space reservation
defc CONSTANT = 42        ; Constant definition
defw DATA_WORD = 0x1234   ; Word constant

; Module directive
module video_driver       ; Module name extracted
```

#### **2.3.2 Ignored (Left to SOOT Annotations)**

```asm
; Instructions - ignored by parser
ld a, 10
jr z, label
call subroutine

; Complex expressions - ignored
ld hl, (variable + 2)

; Macros - ignored
MY_MACRO arg1, arg2
```

### **2.4 Binding Rules**

#### **Rule 1: `;<` binds to the most recent label**

```asm
point:              ; Current label = 'point'
    dw 0            ; Data for point
    ;< (x-field 'int16_t :name 'x)    ; Bound to 'point'
    dw 0
    ;< (x-field 'int16_t :name 'y)    ; Also bound to 'point'
```

#### **Rule 2: Labels clear pending bindings**

```asm
data1:
    dw 100
    ;< (x-field ...)    ; Bound to data1

data2:                 ; New label, clears previous context
    db 1, 2, 3
    ;< (x-field ...)    ; Bound to data2
```

#### **Rule 3: `;!` executes immediately in file context**

```asm
;! (x-module "video")      ; Executes now
;! (x-export-h "video.h")  ; Executes now

code_start:              ; Doesn't affect ;! directives
    ; ... code ...
```

### **2.5 Complete Example: Minimal Driver**

```asm
; simple.asm - Example of XIFF v6.0 annotations

;! (x-module "simple")
;! (x-export-h "include/simple.h")
;! (x-export-c "src/simple.c")

; Constant definition
VERSION:
    defc 1
    ;< (x-const 'uint8_t :name 'VERSION :desc "Driver version")

; Structure definition  
public _point
_point:
    dw 0
    ;< (x-field 'int16_t :name 'x :signed #t)
    dw 0
    ;< (x-field 'int16_t :name 'y :signed #t)
;! (x-struct 'Point :fields '(x y))

; Function with arguments
public __add_numbers
__add_numbers:
    ;< (x-func '__add_numbers
    ;<   :args '((a . uint8_t @a)
    ;<           (b . uint8_t @b))
    ;<   :return '(uint8_t @a)
    ;<   :desc "Adds two numbers")
    add a, b
    ret
```

---

## **PART III: TYPE SYSTEM AND CONVERSIONS**

### **3.1 Supported Data Types**

XIFF maps SOOT type symbols to C types:

| SOOT Type | C Type | Size | Z80 Registers | Example |
|-----------|--------|------|---------------|---------|
| `'void` | `void` | 0 | - | `(x-func ... :return 'void)` |
| `'bool` | `bool` | 8 | A, flags | `'bool` |
| `'uint8_t` | `uint8_t` | 8 | A, B, C, D, E, H, L | `'uint8_t` |
| `'int8_t` | `int8_t` | 8 | A | `'int8_t` |
| `'uint16_t` | `uint16_t` | 16 | HL, DE, BC | `'uint16_t` |
| `'int16_t` | `int16_t` | 16 | HL | `'int16_t :signed #t` |
| `'uint32_t` | `uint32_t` | 32 | DE:HL | `'uint32_t` |
| `'int32_t` | `int32_t` | 32 | DE:HL | `'int32_t :signed #t` |
| `'void*` | `void*` | 16 | HL | `'void*` |
| `'T*` | `T*` | 16 | HL | `'Point*` |
| `'const T*` | `const T*` | 16 | HL | `'const char*` |
| `'T[N]` | `T[N]` | N*size | HL (address) | `'uint8_t[16]` |

### **3.2 Register Specification**

Registers are specified with `@` prefix in argument/return lists:

```lisp
; Function with register arguments
(x-func '__draw_pixel
  :args '((x . uint8_t @h)     ; x in H register
          (y . uint8_t @l)     ; y in L register
          (color . uint16_t @de)) ; color in DE
  :return 'void)

; Function with flag return
(x-func '__device_found
  :args '((id . uint8_t @b))
  :return '(bool @c :invert #t)) ; Result in Carry flag, inverted
```

### **3.3 Conversion Attributes**

Attributes modify how values are converted between Z80 and C:

#### **3.3.1 `:invert` — Boolean Inversion**

```asm
; BIOS convention: CF=0 means success
__detect:
    ; ... detection code ...
    or a        ; CF=0 if device found
    ret         ; Returns true to C

; Annotation:
;< (x-func '__detect
;<   :args '((chip_id . uint8_t @b))
;<   :return '(bool @c :invert #t)) ; CF=0 → true, CF=1 → false
```

#### **3.3.2 `:signed` — Signed Types**

```asm
value:
    dw -100
    ;< (x-field 'int16_t :signed #t :name 'temperature)
```

#### **3.3.3 `:expand-sign` — Sign Extension**

```lisp
; 8-bit signed → 16-bit signed with sign extension
:return '(int8_t @a :expand-sign #t)
```

#### **3.3.4 `:saturate` — Saturation**

```lisp
; Prevent overflow wrap-around  
:return '(uint8_t @a :saturate #t) ; 300 → 255
```

#### **3.3.5 `:array-size` — Array Dimensions**

```asm
buffer:
    ds 16
    ;< (x-field 'uint8_t :name 'buffer :array-size 16)
```

### **3.4 Type Validation Rules**

XIFF validates these constraints:

1. **Register size match**: `uint16_t` cannot be in 8-bit register
2. **Flag usage**: Only `bool` type can use flag registers (`@c`, `@z`, `@nz`)
3. **Pointer registers**: Pointers must be in 16-bit registers
4. **Array alignment**: Arrays should be properly sized in ASM data

---

# **XIFF v6.0 — COMPLETE INTERFACE FRAMEWORK SPECIFICATION (SOOT Edition)**  
*(Продолжение)*

---

## **PART IV: MODULE SYSTEM AND EXPORTS**

### **4.1 Module Declaration**

Every XIFF-annotated file should declare its module:

```asm
; At the top of the file
;! (x-module "video")
;! (x-export-h "include/video.h")
;! (x-export-c "src/video.c")
;! (x-export-asm "src/video_wrap.asm")
;! (x-export-inc "inc/video.inc")
```

### **4.2 Export Directives**

#### **4.2.1 Export Types**

| Directive | Output | Purpose |
|-----------|--------|---------|
| `(x-export-h "path.h")` | C header | Public C API declarations |
| `(x-export-c "path.c")` | C source | C wrapper implementations |
| `(x-export-asm "path.asm")` | ASM wrapper | Z80 calling convention adapters |
| `(x-export-inc "path.inc")` | ASM include | `extern` declarations for ASM |

#### **4.2.2 Export Scoping**

```asm
; Private to module (no export)
internal_data:
    dw 0
    ;< (x-field 'uint16_t)  ; Not exported

; Public C API (exported)
public api_function
api_function:
    ;< (x-func 'api_function ...)  ; Exported to C
```

### **4.3 File Generation Process**

```
source.asm
    │
    ├───▶ include/module.h    (C header)
    │        #ifndef _MODULE_H_
    │        #define _MODULE_H_
    │        // Generated declarations
    │        #endif
    │
    ├───▶ src/module.c        (C source)
    │        #include "module.h"
    │        // C wrapper functions
    │
    ├───▶ src/module_wrap.asm (ASM wrapper)
    │        .module module_wrap
    │        ; Wrapper functions
    │
    └───▶ inc/module.inc      (ASM include)
            ; extern declarations
```

### **4.4 Namespace Management**

#### **4.4.1 C Namespace**

```asm
;! (x-module "video")
; Results in C functions prefixed with 'video_'
;< (x-func '__init ...)  ; Becomes: bool video_init(...)
```

#### **4.4.2 Name Mangling Rules**

| ASM Name | C Name (default) | Can be overridden |
|----------|------------------|-------------------|
| `__function` | `module_function` | `:c-name "custom_name"` |
| `_constant` | `MODULE_CONSTANT` | `:c-name "CUSTOM"` |
| `_structure` | `ModuleStructure` | `:c-name "CustomStruct"` |

Example with custom names:
```asm
;< (x-func '__draw_pixel 
;<   :c-name "gfx_put_pixel"  ; Override default name
;<   :args ...)
```

---

## **PART V: STRUCTURES AND DATA TYPES**

### **5.1 Structure Definition**

#### **5.1.1 Basic Structure**

```asm
; Method 1: Implicit structure (fields define structure)
public _point
_point:
    dw 0
    ;< (x-field 'int16_t :name 'x :signed #t)
    dw 0
    ;< (x-field 'int16_t :name 'y :signed #t)
;! (x-struct 'Point :fields '(x y))  ; Optional: explicit struct
```

#### **5.1.2 Explicit Structure with Size**

```asm
; Method 2: Explicit structure with size verification
public _rect
;! (x-begin-struct 'Rect :size 8)  ; Expect 8 bytes
_rect:
    dw 0  ; left
    ;< (x-field 'int16_t :name 'left)
    dw 0  ; top
    ;< (x-field 'int16_t :name 'top)
    dw 0  ; right
    ;< (x-field 'int16_t :name 'right)
    dw 0  ; bottom
    ;< (x-field 'int16_t :name 'bottom)
;! (x-end-struct)  ; Verifies size matches
```

### **5.2 Arrays and Buffers**

```asm
; Fixed-size array
public _palette
_palette:
    ds 16 * 3  ; 16 colors × 3 bytes each
    ;< (x-field 'uint8_t :name 'colors :array-size '(16 3))
    
; String buffer
public _message
_message:
    ds 64
    ;< (x-field 'char :name 'text :array-size 64)
```

### **5.3 Enumerations**

```asm
;! (x-enum 'VideoMode 
;!   :type 'uint8_t
;!   :values '((MODE_256x192 0 "256×192, 16 colors")
;!             (MODE_320x200 1 "320×200, 4 colors")
;!             (MODE_640x200 2 "640×200, monochrome")))

; Usage with constant
CURRENT_MODE:
    defc 1
    ;< (x-const 'VideoMode :name 'CURRENT_MODE)
```

### **5.4 Unions and Bitfields**

```asm
; Union via manual offset specification
public _flags
_flags:
    db 0
    ;< (x-field 'uint8_t :name 'raw)
    ;< (x-field 'bool :name 'enabled :offset 0 :bit 0)
    ;< (x-field 'bool :name 'visible :offset 0 :bit 1)
    ;< (x-field 'uint8_t :name 'type :offset 0 :bits '(2 3))
```

---

## **PART VI: FUNCTIONS AND METHODS**

### **6.1 Function Declaration**

#### **6.1.1 Basic Function**

```asm
public __add_numbers
__add_numbers:
    ;< (x-func '__add_numbers
    ;<   :args '((a . uint8_t @a)
    ;<           (b . uint8_t @b))
    ;<   :return '(uint8_t @a)
    ;<   :desc "Adds two 8-bit numbers")
    add a, b
    ret
```

#### **6.1.2 Function with Multiple Returns**

```asm
public __divmod
__divmod:
    ;< (x-func '__divmod
    ;<   :args '((dividend . uint16_t @hl)
    ;<           (divisor . uint8_t @b))
    ;<   :return '((quotient . uint8_t @a)
    ;<             (remainder . uint8_t @c))
    ;<   :desc "Division with remainder")
    ; ... division code ...
    ret
```

### **6.2 VTable Methods (BIOS Driver Architecture)**

#### **6.2.1 VTable Definition**

```asm
;! (x-begin-vtable '__video_vtable 
;!   :size 64 
;!   :type 'VideoDriver
;!   :mandatory '(detect init deinit get_info command))

public __video_vtable
__video_vtable:
__video_detect:
    jp _detect_impl
    ;< (x-vtable-method 'detect :target '_detect_impl)
__video_init:
    jp _init_impl
    ;< (x-vtable-method 'init :target '_init_impl)
; ... 19 more methods ...
__video_vtable_end:
;! (x-end-vtable)  ; Verifies size = 64 bytes
```

#### **6.2.2 Method Implementation**

```asm
public __video_detect
_detect_impl:
    ;< (x-method 'detect
    ;<   :args '((chip_id . uint8_t @b))
    ;<   :return '(bool @c :invert #t)
    ;<   :desc "Detects video hardware")
    ; ... detection logic ...
    or a  ; CF=0 if found
    ret
```

### **6.3 Wrapper Generation Types**

```asm
;< (x-func '__optimized
;<   :args ...
;<   :wrapper 'fastcall)  ; Generates fastcall wrapper

;< (x-func '__simple
;<   :args ...
;<   :wrapper 'naked)     ; Minimal: just jp to implementation

;< (x-func '__compatible  
;<   :args ...
;<   :wrapper 'z88dk)     ; z88dk C compiler compatibility
```

### **6.4 Event Handlers (BIOS Commands)**

```asm
;! (x-event 'set_video_mode
;!   :via '__video_command      ; Called via command() method
;!   :command #x40             ; SET_MODE command code
;!   :args '((mode . uint8_t @a))
;!   :return '(bool @c :invert #t))

_set_video_mode_handler:
    ; Handle command 0x40
    ; A contains video mode
    ret
```

---

## **PART VII: BIOS SPECIFICATION INTEGRATION**

### **7.1 Mandatory Driver Methods**

XIFF automatically verifies these BIOS-required methods:

```lisp
; In xiff-core.sot
(define *mandatory-methods*
  '(detect    ; Device detection
    init      ; Initialization  
    deinit    ; Deinitialization
    get_info  ; Get device information
    command)) ; Execute commands
```

### **7.2 VTable Validation**

```asm
; XIFF checks:
; 1. Size = 64 bytes exactly
; 2. All mandatory methods present
; 3. Method slots are properly filled
; 4. End label exists for size calculation

__driver_vtable_end:
    ; Used for: defc __driver_vtable_size = __driver_vtable_end - __driver_vtable
```

### **7.3 MemoryContext Support**

```asm
; BIOS MemoryContext structure (Section 4)
public _video_context
;! (x-begin-struct 'MemoryContext :size 8)
_video_context:
_hash:      db 0
    ;< (x-field 'uint8_t :name 'hash)
_slot_reg:  db 0  
    ;< (x-field 'uint8_t :name 'slot_reg)
_window0:   db 0
    ;< (x-field 'uint8_t :name 'window0)
; ... 5 more fields ...
;! (x-end-struct)
```

### **7.4 Command Code Validation**

XIFF validates command codes against BIOS ranges:

```asm
;! (x-event 'power_on
;!   :command #x01           ; Valid: 0x00-0x1F for system
;!   ...)

;! (x-event 'video_mode
;!   :command #x40           ; Valid: 0x40-0x5F for video
;!   ...)

; Error if command code outside valid ranges
```

---

# **XIFF v6.0 — COMPLETE INTERFACE FRAMEWORK SPECIFICATION (SOOT Edition)**  
*(Продолжение)*

---

## **PART VIII: CODE GENERATION AND FILE INJECTION**

### **8.1 Generated File Formats**

#### **8.1.1 C Header (.h) Generation**

```c
/* File: include/video.h */
/* GENERATED BY XIFF v6.0 - DO NOT EDIT MANUALLY */
/* Source: drivers/video/video.asm */
/* Timestamp: 2026-01-13T14:30:00Z */

#ifndef _VIDEO_H_
#define _VIDEO_H_

#include <stdint.h>
#include <stdbool.h>

/* Constants */
#define VIDEO_SCREEN_WIDTH 320
#define VIDEO_SCREEN_HEIGHT 200

/* Enumerations */
typedef enum {
    VIDEO_MODE_256x192 = 0,
    VIDEO_MODE_320x200 = 1,
    VIDEO_MODE_640x200 = 2
} VideoMode;

/* Structures */
typedef struct {
    int16_t x;
    int16_t y;
} Point;

/* Function declarations */
bool video_detect(uint8_t chip_id);
bool video_init(VideoMode mode);
void video_draw_pixel(uint8_t x, uint8_t y, uint16_t color);

/* Driver VTable access */
extern void* video_get_vtable(void);

#endif /* _VIDEO_H_ */
```

#### **8.1.2 C Source (.c) Generation**

```c
/* File: src/video.c */
/* GENERATED BY XIFF v6.0 - DO NOT EDIT MANUALLY */

#include "video.h"

/* External wrapper functions (implemented in ASM) */
extern bool _video_detect_wrapper(uint8_t chip_id);
extern bool _video_init_wrapper(uint8_t mode);
extern void _video_draw_pixel_wrapper(uint8_t x, uint8_t y, uint16_t color);

/* Public API implementation */
bool video_detect(uint8_t chip_id) {
    return _video_detect_wrapper(chip_id);
}

bool video_init(VideoMode mode) {
    return _video_init_wrapper((uint8_t)mode);
}

void video_draw_pixel(uint8_t x, uint8_t y, uint16_t color) {
    _video_draw_pixel_wrapper(x, y, color);
}

/* VTable accessor */
void* video_get_vtable(void) {
    extern void* __video_vtable;
    return (void*)&__video_vtable;
}
```

#### **8.1.3 ASM Wrapper (.asm) Generation**

```asm
; File: src/video_wrap.asm
; GENERATED BY XIFF v6.0 - DO NOT EDIT MANUALLY
; Source: drivers/video/video.asm

.module video_wrap
.include "video.inc"

.globl _video_detect_wrapper
.globl _video_init_wrapper
.globl _video_draw_pixel_wrapper

; bool video_detect(uint8_t chip_id)
_video_detect_wrapper:
    pop hl          ; Save return address
    pop bc          ; Get chip_id from stack
    push hl         ; Restore return address
    ld b, c         ; chip_id in B register
    call __video_detect
    ld a, 0         ; Default: false
    jr c, .no_detect
    inc a           ; true = 1
.no_detect:
    ld l, a         ; Return in HL (bool in L)
    ret

; bool video_init(uint8_t mode)  
_video_init_wrapper:
    pop hl
    pop bc
    push hl
    ld a, c         ; mode in A register
    call __video_init
    ld a, 0
    jr c, .no_init
    inc a
.no_init:
    ld l, a
    ret

; void video_draw_pixel(uint8_t x, uint8_t y, uint16_t color)
_video_draw_pixel_wrapper:
    pop hl          ; Return address
    pop bc          ; x in C
    pop de          ; y in E
    ex (sp), hl     ; color in HL, restore return
    push hl
    ld h, c         ; x in H
    ld l, e         ; y in L
    ld de, (sp+2)   ; color in DE
    jp __draw_pixel ; Tail call optimization
```

#### **8.1.4 ASM Include (.inc) Generation**

```asm
; File: inc/video.inc
; GENERATED BY XIFF v6.0 - DO NOT EDIT MANUALLY
; Source: drivers/video/video.asm

; Constants
SCREEN_WIDTH:   equ 320
SCREEN_HEIGHT:  equ 200

; External function declarations
extern __video_detect
extern __video_init
extern __draw_pixel

; Structure offsets
_point_x:       equ 0
_point_y:       equ 2

; VTable reference
extern __video_vtable
```

### **8.2 Smart File Injection (Idempotent Generation)**

XIFF uses FileInjector to preserve manual code:

```cpp
// C++ side injection
bool XiffCompiler::inject_content(
    const fs::path& target_path,
    const std::string& marker,
    const std::string& content,
    const fs::path& source_file) {
    
    return m_injector.inject(
        target_path.string(),
        marker,           // "xiff-soot"
        content,
        source_file.string()
    );
}
```

**Injection markers in generated files:**
```c
/* XIFF-START: drivers/video/video.asm */
// Generated content here
/* XIFF-END: drivers/video/video.asm */
```

### **8.3 Generation Process**

```lisp
;; In xiff-core.sot - the generation entry point
(desfun xiff-generate (target-type target-path source-file)
  (case target-type
    ('h (generate-c-header target-path source-file))
    ('c (generate-c-source target-path source-file))
    ('asm (generate-asm-wrapper target-path source-file))
    ('inc (generate-asm-include target-path source-file))
    (else (error (format "Unknown target type: ~a" target-type)))))

(define (generate-c-header path source)
  (let ((content (make-string-output-stream)))
    (format content "/* File: ~a */~%" path)
    (format content "/* GENERATED BY XIFF v6.0 - DO NOT EDIT MANUALLY */~%")
    (format content "/* Source: ~a */~%" source)
    (format content "/* Timestamp: ~a */~%~%" (current-timestamp))
    
    ;; Add include guard
    (let ((guard-name (path->guard-name path)))
      (format content "#ifndef ~a~%" guard-name)
      (format content "#define ~a~%~%" guard-name))
    
    ;; Generate content based on registry
    (generate-header-content content)
    
    (format content "#endif /* ~a */~%" guard-name)
    (get-output-stream-string content)))
```

---

## **PART IX: COMMAND LINE INTERFACE**

### **9.1 Command Overview**

```
xiff <command> [options] <files>
```

### **9.2 Main Commands**

#### **9.2.1 `parse` — Parse and validate**

```bash
xiff parse driver.asm
xiff parse --verbose *.asm
xiff parse --output errors.txt drivers/
```

**Checks:**
- SOOT syntax in annotations
- Type and register compatibility
- Label existence for bindings
- BIOS specification compliance

#### **9.2.2 `generate` — Generate files**

```bash
xiff generate driver.asm
xiff generate --force driver.asm      # Overwrite without merge
xiff generate --target h driver.asm   # Only generate headers
xiff generate --clean drivers/        # Remove all generated files
```

#### **9.2.3 `validate` — BIOS validation**

```bash
xiff validate driver.asm
xiff validate --strict driver.asm     # Warnings as errors
xiff validate --report json bios/     # JSON output
```

#### **9.2.4 `interactive` — REPL mode**

```bash
xiff interactive driver.asm
; Enters SOOT REPL with file context loaded
; Can execute annotations manually for debugging
```

### **9.3 Logging System**

```bash
xiff generate file.asm           # Level 1: Errors only
xiff generate file.asm -v        # Level 2: + Warnings  
xiff generate file.asm -vv       # Level 3: + Info (parsing details)
xiff generate file.asm -vvv      # Level 4: + Debug (SOOT execution)
xiff generate file.asm -vvvv     # Level 5: Trace (everything)
```

**Log format:**
```
[LEVEL][COMPONENT] Message
[INFO][parser] Processing video.asm
[WARN][type] uint16_t in 8-bit register A
[ERROR][bios] VTable size mismatch: 63 vs 64 bytes
```

### **9.4 Configuration File**

XIFF looks for `.xiffrc` in project root:

```json
{
  "version": "6.0",
  "paths": {
    "inc_dir": "inc",
    "h_dir": "include",
    "c_dir": "src",
    "wrap_dir": "src",
    "backup": true,
    "backup_dir": ".xiff_backup"
  },
  "generation": {
    "c_standard": "c99",
    "stdint_header": "<stdint.h>",
    "stdbool_header": "<stdbool.h>",
    "indent": "  ",
    "comment_style": "c"
  },
  "validation": {
    "check_vtable_size": true,
    "check_mandatory_methods": true,
    "warnings_as_errors": false,
    "strict_types": true
  },
  "soot": {
    "libraries": ["xiff/core.sot", "xiff/bios.sot"],
    "repl_timeout": 30,
    "memory_limit": 10485760
  }
}
```

---

## **PART X: IMPLEMENTATION ROADMAP**

### **10.1 Phase 1: Core Parser and SOOT Integration**

- [ ] Basic annotation parser (`;!`, `;<`, `;>`)
- [ ] SOOT interpreter integration
- [ ] Label detection and binding
- [ ] `x-const` and `x-field` support
- [ ] Simple C header generation

### **10.2 Phase 2: Function and Type System**

- [ ] `x-func` with argument/return types
- [ ] Register allocation validation
- [ ] C wrapper generation
- [ ] ASM wrapper generation
- [ ] Type conversion attributes (`:invert`, `:signed`)

### **10.3 Phase 3: BIOS Specification Support**

- [ ] VTable support (`x-begin-vtable`, `x-vtable-method`)
- [ ] 64-byte size verification
- [ ] Mandatory method checking
- [ ] MemoryContext structure generation
- [ ] Command/event system

### **10.4 Phase 4: Advanced Features**

- [ ] Smart file injection (FileInjector integration)
- [ ] Configuration file support
- [ ] Multi-file project support
- [ ] Enum and structure generation
- [ ] Error reporting and validation

### **10.5 Phase 5: Optimization and Tooling**

- [ ] Incremental generation (cache)
- [ ] VS Code extension
- [ ] Makefile/CMake integration
- [ ] Performance optimization
- [ ] Comprehensive test suite

### **10.6 Phase 6: Documentation and Release**

- [ ] Complete documentation
- [ ] Example drivers
- [ ] Migration guide from v5.0
- [ ] Release v1.0.0

---

## **PART XI: ERROR HANDLING AND DIAGNOSTICS**

### **11.1 Error Categories**

#### **11.1.1 Syntax Errors**
- Malformed SOOT expressions
- Unbalanced parentheses
- Invalid annotation prefix

#### **11.1.2 Semantic Errors**
- Type/register mismatch
- Undefined labels in bindings
- Duplicate definitions

#### **11.1.3 BIOS Compliance Errors**
- VTable size incorrect
- Missing mandatory methods
- Invalid command codes

#### **11.1.4 Generation Errors**
- File system permissions
- Invalid output paths
- Injection conflicts

### **11.2 Error Recovery**

XIFF attempts to continue after errors when possible:

```lisp
;; In xiff-core.sot - error handling
(define *error-count* 0)
(define *warning-count* 0)

(desmacro with-error-handling (&body body)
  `(with-handlers 
     ((parse-error (lambda (e) (increment-error-count) (print-error e)))
      (type-error (lambda (e) (increment-error-count) (print-error e)))
      (warning (lambda (w) (increment-warning-count) (print-warning w))))
     ,@body))
```

### **11.3 Diagnostic Output**

```bash
# Summary output
xiff generate driver.asm
# Output:
Processed: driver.asm
Generated: 4 files (include/driver.h, src/driver.c, ...)
Errors: 0
Warnings: 2
Duration: 0.45s
```

---

## **PART XII: PERFORMANCE CONSIDERATIONS**

### **12.1 Parser Optimizations**

- **Incremental parsing**: Only re-parse changed files
- **SOOT bytecode caching**: Compile annotations to bytecode
- **Parallel processing**: Multiple files in parallel

### **12.2 Memory Usage**

- **SOOT interpreter**: ~10MB baseline
- **Registry storage**: Hash tables for fast lookup
- **String interning**: Reduce duplication in generated code

### **12.3 Generation Performance**

- **Template-based generation**: Pre-compiled templates
- **String builders**: Avoid excessive concatenation
- **Batch file writes**: Minimize I/O operations

### **12.4 Expected Performance**

```
File size        Parse time    Generate time    Total
-----------      ----------    -------------    -----
10 KB ASM        0.02s         0.05s            0.07s
100 KB ASM       0.15s         0.30s            0.45s
1 MB ASM         1.20s         2.50s            3.70s
```

---

## **APPENDIX A: MIGRATION FROM v5.0**

### **A.1 Syntax Changes**

| v5.0 Syntax | v6.0 Syntax | Notes |
|-------------|-------------|-------|
| `;; XIFF:const` | `;< (x-const ...)` | Positional binding |
| `;; XIFF:func` | `;< (x-func ...)` | After function label |
| `;; XIFF:struct` | `;! (x-struct ...)` | File-level directive |
| `;; XIFF:vtable` | `;! (x-begin-vtable ...)` | With end marker |

### **A.2 Automated Migration**

```bash
xiff migrate --from=5.0 driver.asm
```

**Migration steps:**
1. Convert annotations to SOOT syntax
2. Add binding prefixes (`;!`, `;<`)
3. Update type specifications
4. Preserve manual code blocks

### **A.3 Backward Compatibility**

**Not supported:** v6.0 cannot parse v5.0 annotations directly. Use migration tool.

---

## **APPENDIX B: EXAMPLE DRIVER IMPLEMENTATION**

### **B.1 Complete Sound Driver**

```asm
; sound.asm - AY-3-8910 Sound Driver with XIFF v6.0

module sound_driver

;! (x-module "sound")
;! (x-export-h "include/sound.h")
;! (x-export-c "src/sound.c")
;! (x-export-asm "src/sound_wrap.asm")

; Constants
SAMPLE_RATE:
    defc 44100
    ;< (x-const 'uint32_t :name 'SAMPLE_RATE :desc "Sampling frequency")

MAX_VOLUME:
    defc 15
    ;< (x-const 'uint8_t :name 'MAX_VOLUME :desc "Maximum volume level")

; Enumeration
;! (x-enum 'Note
;!   :type 'uint8_t
;!   :values '((NOTE_C4 60 "Middle C")
;!             (NOTE_D4 62 "D above middle C")
;!             (NOTE_E4 64 "E above middle C")))

; Sound state structure
public _sound_state
_sound_state:
volume:     db 15
    ;< (x-field 'uint8_t :name 'volume)
muted:      db 0
    ;< (x-field 'bool :name 'muted)
frequency:  dw 440
    ;< (x-field 'uint16_t :name 'frequency')
;! (x-struct 'SoundState :fields '(volume muted frequency))

; Driver VTable (64 bytes, BIOS compliant)
;! (x-begin-vtable '__sound_vtable 
;!   :size 64
;!   :type 'SoundDriver
;!   :mandatory-methods #t)

public __sound_vtable
__sound_vtable:
__sound_detect:
    jp _detect_impl
    ;< (x-vtable-method 'detect :target '_detect_impl)
__sound_init:
    jp _init_impl
    ;< (x-vtable-method 'init :target '_init_impl)
; ... 19 more methods ...
__sound_vtable_end:

;! (x-end-vtable)

; Method implementations
public __sound_detect
_detect_impl:
    ;< (x-method 'detect
    ;<   :args '((chip_id . uint8_t @b))
    ;<   :return '(bool @c :invert #t)
    ;<   :desc "AY-3-8910 detection")
    ; ... detection code ...
    or a        ; CF=0 if found
    ret

; Event handler (BIOS command)
;! (x-event 'power_control
;!   :via '__sound_command
;!   :command #x01
;!   :args '((state . uint8_t @a))
;!   :return '(bool @c :invert #t))

_power_control_handler:
    ; Handle power on/off command
    ret
```

### **B.2 Generated C Usage**

```c
#include "sound.h"

int main() {
    // Detect sound hardware
    if (!sound_detect(0x10)) {
        printf("Sound chip not found\n");
        return 1;
    }
    
    // Initialize
    if (!sound_init()) {
        printf("Initialization failed\n");
        return 1;
    }
    
    // Access state
    SoundState* state = sound_get_state();
    printf("Volume: %d\n", state->volume);
    
    // Control power
    sound_power_control(1);  // Power on
    
    return 0;
}
```

---

## **APPENDIX C: XIFF CORE SOOT LIBRARY REFERENCE**

### **C.1 Core Functions**

```lisp
;; Registration functions
(x-register-constant name value type &key desc)
(x-register-field label-name type &key signed array-size name)
(x-register-function label-name &key args return desc wrapper)

;; Structure management  
(x-begin-structure name &key size fields)
(x-add-field field-spec)
(x-end-structure)

;; VTable management
(x-begin-vtable name &key size type mandatory-methods)
(x-add-vtable-method slot-name target-label)
(x-end-vtable)

;; Export control
(x-add-export type path)
(x-get-exports)  ; Returns list of export targets
```

### **C.2 Utility Functions**

```lisp
;; Type conversion
(x-type->c-type soot-type)     ; → C type string
(x-type-size soot-type)        ; → Size in bytes
(x-register-compatible? type register) ; → Boolean

;; Label management
(x-current-label)              ; → Current label or #f
(x-find-label name)            ; → Label info or #f
(x-label-exists? name)         ; → Boolean

;; Generation helpers
(x-generate-c-prototype func-info) ; → C prototype string
(x-generate-asm-wrapper func-info) ; → ASM wrapper code
```

### **C.3 Validation Functions**

```lisp
;; Type validation
(x-validate-type type-spec)    ; → (success? message)
(x-validate-register type register) ; → (success? message)

;; BIOS validation
(x-validate-vtable vtable-info) ; → List of issues
(x-check-mandatory-methods vtable-info) ; → Missing methods

;; Structure validation  
(x-validate-structure struct-info) ; → Size mismatches, etc.
```

---

## **APPENDIX D: KNOWN LIMITATIONS AND FUTURE EXTENSIONS**

### **D.1 MVP Limitations (v1.0)**

1. **No inline ASM in C**: Generated C files use external wrapper calls
2. **Limited type system**: No `float`, `double`, or complex structs
3. **Simple inheritance**: Basic VTable inheritance only
4. **Single-file focus**: Limited cross-file dependency resolution
5. **No callback support**: Function pointers not generated

### **D.2 Future Extensions**

1. **Callback generation**: Support for C→ASM callbacks
2. **Template system**: Generic driver generation
3. **Documentation extraction**: Auto-generate API docs
4. **Optimization hints**: Suggest register allocation improvements
5. **IDE integration**: Real-time annotation validation

### **D.3 Compatibility Notes**

- **Assemblers**: Primary support for sjasmplus, basic support for z80asm
- **C Compilers**: Compatible with SDCC, z88dk, and standard C99 compilers
- **Platforms**: Windows, Linux, macOS (any with C++17 and SOOT)
- **BIOS Versions**: Targets Xi Aleste BIOS 2.0+ specification

---

## **APPENDIX E: TROUBLESHOOTING GUIDE**

### **E.1 Common Issues**

#### **"No label for binding" error**
```asm
; ERROR: ;< used without preceding label
    dw 100
    ;< (x-field 'int16_t)  ; ERROR!
    
; FIX: Add a label
data:
    dw 100
    ;< (x-field 'int16_t)  ; OK
```

#### **"Type mismatch" warning**
```asm
; WARNING: 16-bit type in 8-bit register
;< (x-func ... :args '((value . uint16_t @a)))  ; WARNING!

; FIX: Use correct register
;< (x-func ... :args '((value . uint16_t @hl))) ; OK
```

#### **"VTable size incorrect" error**
```asm
; ERROR: VTable not 64 bytes
__vtable_end:
; Size calculation shows 63 bytes

; FIX: Add padding or correct method count
    ; ... ensure exactly 21 methods (21×3 = 63 bytes)
    jp _dummy_handler  ; +3 bytes = 66, need 64? Check spec
```

### **E.2 Debugging Tips**

1. **Use verbose mode**: `xiff generate -vv file.asm`
2. **Check SOOT execution**: `xiff interactive file.asm`
3. **Examine generated code**: Look at wrapper ASM for register usage
4. **Validate step-by-step**: `xiff parse` then `xiff validate`

---

## **CONCLUSION**

**XIFF v6.0** represents a paradigm shift in interface generation for Z80 assembly, replacing custom syntax with a powerful, embeddable LISP dialect. By leveraging SOOT, XIFF gains:

1. **Unprecedented flexibility** through a full programming language in annotations
2. **Clean integration** with existing ASM code via simple comment annotations  
3. **Robust type safety** with comprehensive validation
4. **BIOS specification compliance** through automated checks
5. **Professional output** with idempotent file generation

This specification provides a complete blueprint for implementation, balancing sophistication with the KISS principle. The result will be a tool that significantly accelerates driver development for Xi Aleste BIOS while maintaining the performance advantages of hand-optimized assembly.

---

**Document Status:** Approved for implementation  
**Next Steps:** Begin Phase 1 implementation (Core Parser and SOOT Integration)  
**Reference Implementation:** See `xiff/` directory in Xi Aleste BIOS repository

---
*"The power of LISP meets the pragmatism of Z80" — XIFF v6.0*