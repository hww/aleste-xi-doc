# Retro Graphics Effects: Technical Reference

**Status:** Draft  **Version:** 2.0  **Author:** hww

## A Practical Guide for Artists, Programmers, and Hardware Implementers

**Scope:** 2D retro graphics, sprite engines, tile-based displays,
framebuffer effects, and 16-bit-inspired rendering\
**Platform note:** The original notes refer to a platform called *Kiss*
and use illustrative accelerator fields such as `accel->operation` and
`OP_BLEND`. No authoritative Kiss hardware/API specification was
included with the source. Accordingly, all such identifiers in this
document are treated as **pseudocode placeholders**, not verified
register names, constants, or guaranteed hardware features.

------------------------------------------------------------------------

## Table of Contents

- [Retro Graphics Effects: Technical Reference](#retro-graphics-effects-technical-reference)
  - [A Practical Guide for Artists, Programmers, and Hardware Implementers](#a-practical-guide-for-artists-programmers-and-hardware-implementers)
  - [Table of Contents](#table-of-contents)
  - [1. Purpose and Scope](#1-purpose-and-scope)
    - [1.1 What this guide does not assume](#11-what-this-guide-does-not-assume)
    - [1.2 Terminology](#12-terminology)
  - [2. Core Graphics Concepts](#2-core-graphics-concepts)
    - [2.1 Pixels, Color Formats, and Framebuffers](#21-pixels-color-formats-and-framebuffers)
    - [2.2 Transparency and Alpha](#22-transparency-and-alpha)
    - [2.3 Compositing and Blend Equations](#23-compositing-and-blend-equations)
    - [2.4 Logical Raster Operations](#24-logical-raster-operations)
    - [2.5 Coordinate Systems, Clipping, and Memory Layout](#25-coordinate-systems-clipping-and-memory-layout)
  - [3. Sprite Effects](#3-sprite-effects)
    - [3.1 Color-Key Transparency](#31-color-key-transparency)
    - [3.2 Sprite Inversion and Negative Effects](#32-sprite-inversion-and-negative-effects)
    - [3.3 Flipping, Rotation, and Scaling](#33-flipping-rotation-and-scaling)
    - [3.4 Palette and Color Replacement](#34-palette-and-color-replacement)
  - [4. Composition and Layer Effects](#4-composition-and-layer-effects)
    - [4.1 Layer Compositing](#41-layer-compositing)
    - [4.2 Alpha Blending](#42-alpha-blending)
    - [4.3 Additive and Subtractive Blending](#43-additive-and-subtractive-blending)
    - [4.4 Masking](#44-masking)
    - [4.5 Priority, Ordering, and Transparency Interaction](#45-priority-ordering-and-transparency-interaction)
  - [5. Pattern and System Effects](#5-pattern-and-system-effects)
    - [5.1 Pixelation and Mosaic](#51-pixelation-and-mosaic)
    - [5.2 Dithering](#52-dithering)
    - [5.3 Area and Rectangle Filling](#53-area-and-rectangle-filling)
    - [5.4 Raster Bars and Scanline Effects](#54-raster-bars-and-scanline-effects)
  - [6. Lighting and Temporal Effects](#6-lighting-and-temporal-effects)
    - [6.1 Shadows](#61-shadows)
    - [6.2 Highlights and Glow](#62-highlights-and-glow)
    - [6.3 Flicker and Blink](#63-flicker-and-blink)
    - [6.4 Flash and Hit Feedback](#64-flash-and-hit-feedback)
    - [6.5 Fade In and Fade Out](#65-fade-in-and-fade-out)
  - [7. Screen-Space Effects](#7-screen-space-effects)
    - [7.1 Screen Shake and Screen Offset](#71-screen-shake-and-screen-offset)
    - [7.2 Scrolling and Parallax](#72-scrolling-and-parallax)
    - [7.3 Clipping and Viewports](#73-clipping-and-viewports)
    - [7.4 Screen Transitions](#74-screen-transitions)
  - [8. Worked Example: Player Damage Feedback](#8-worked-example-player-damage-feedback)
    - [8.1 Desired behavior](#81-desired-behavior)
    - [8.2 State-based implementation](#82-state-based-implementation)
    - [8.3 Calculate flash intensity](#83-calculate-flash-intensity)
    - [8.4 Calculate camera shake](#84-calculate-camera-shake)
    - [8.5 Render order](#85-render-order)
    - [8.6 Important corrections](#86-important-corrections)
  - [9. Implementation Architecture](#9-implementation-architecture)
    - [9.1 Effect lifecycle](#91-effect-lifecycle)
    - [9.2 Separate world-space and screen-space effects](#92-separate-world-space-and-screen-space-effects)
    - [9.3 Avoid hidden state in the accelerator](#93-avoid-hidden-state-in-the-accelerator)
    - [9.4 Synchronization and command completion](#94-synchronization-and-command-completion)
  - [10. Performance, Timing, and Reliability](#10-performance-timing-and-reliability)
    - [10.1 Cost model](#101-cost-model)
    - [10.2 Prefer the simplest supported implementation](#102-prefer-the-simplest-supported-implementation)
    - [10.3 Frame-rate independence](#103-frame-rate-independence)
    - [10.4 Memory and buffer safety](#104-memory-and-buffer-safety)
    - [10.5 Retro authenticity](#105-retro-authenticity)
  - [11. Testing and Visual Validation](#11-testing-and-visual-validation)
  - [12. Common Mistakes and Corrections](#12-common-mistakes-and-corrections)
  - [13. Hardware/API Verification Checklist](#13-hardwareapi-verification-checklist)
    - [13.1 Device and pixel format](#131-device-and-pixel-format)
    - [13.2 Drawing operations](#132-drawing-operations)
    - [13.3 Geometry and memory](#133-geometry-and-memory)
    - [13.4 Execution model](#134-execution-model)
    - [13.5 Code integration](#135-code-integration)
  - [14. Glossary](#14-glossary)
  - [15. Appendix A: Pseudocode Conventions](#15-appendix-a-pseudocode-conventions)
  - [16. Appendix B: Reference Equations](#16-appendix-b-reference-equations)
    - [B.1 Source-over alpha blend](#b1-source-over-alpha-blend)
    - [B.2 Integer alpha blend (8-bit alpha)](#b2-integer-alpha-blend-8-bit-alpha)
    - [B.3 Additive blend](#b3-additive-blend)
    - [B.4 Subtractive blend](#b4-subtractive-blend)
    - [B.5 Channel inversion](#b5-channel-inversion)
    - [B.6 Bitwise inversion](#b6-bitwise-inversion)
    - [B.7 Color-key transparency](#b7-color-key-transparency)
    - [B.8 Nearest-sample mosaic](#b8-nearest-sample-mosaic)
    - [B.9 Camera transform](#b9-camera-transform)
    - [B.10 Fade to a target color](#b10-fade-to-a-target-color)
  - [Final Notes](#final-notes)

------------------------------------------------------------------------

## 1. Purpose and Scope

This guide describes common visual effects used in retro-style 2D games
and explains how to reason about their implementation. It is intended
for both artists, who need to understand the visual result and its
constraints, and programmers, who need to translate that result into
rendering operations.

The effects are grouped by the part of the rendering pipeline they
affect:

-   **Sprite effects** modify an individual graphic or its pixels.
-   **Composition effects** combine multiple images or layers.
-   **Pattern effects** alter the spatial appearance of an image.
-   **Lighting and temporal effects** change color or visibility over
    time.
-   **Screen-space effects** operate on a viewport or the final image.

These categories are conceptual, not mutually exclusive. A damage flash,
for example, may combine a sprite tint, a screen overlay, and a short
camera shake.

### 1.1 What this guide does not assume

A retro-style platform does not necessarily provide modern GPU features.
Depending on the hardware, it may use:

-   a tile map and hardware sprites rather than a full framebuffer;
-   indexed color and a palette rather than direct RGB pixels;
-   a fixed set of raster operations;
-   hardware scrolling but no arbitrary affine transforms;
-   a limited number of blend modes, or no alpha blending at all;
-   CPU-generated effects, lookup tables, or pre-rendered animation
    frames.

An effect described here may therefore be implemented in hardware,
software, by palette manipulation, or by a precomputed asset. Choose the
implementation that the target system actually supports.

### 1.2 Terminology

The terms **source** and **destination** are used consistently:

-   **Source (`src`)**: the image, pixel, color, or mask being read.
-   **Destination (`dst`)**: the pixel or buffer being modified.
-   **Background**: the already-rendered content behind the current
    object.
-   **Overlay**: content drawn over an existing image.
-   **Framebuffer**: memory containing a rendered image.
-   **Viewport**: the rectangular portion of the world currently visible
    on screen.

The word *transparency* must be used carefully. Color-key transparency,
binary mask transparency, and alpha transparency are different
techniques.

------------------------------------------------------------------------

## 2. Core Graphics Concepts

### 2.1 Pixels, Color Formats, and Framebuffers

A pixel is a stored color value, but its interpretation depends on the
selected format. Common formats include:

  -----------------------------------------------------------------------
  Format                  Meaning                 Typical considerations
  ----------------------- ----------------------- -----------------------
  RGB565                  5 red, 6 green, 5 blue  Common in 16-bit
                          bits                    displays; no alpha
                                                  channel

  RGB555                  5 bits per RGB channel, Exact layout varies
                          often one unused bit    

  RGBA8888                8 bits per red, green,  Flexible, but more
                          blue, and alpha         memory bandwidth

  Indexed color           Pixel stores a palette  Palette changes can
                          index                   produce efficient
                                                  global effects

  Packed bitplanes        Color bits are stored   Common in older
                          in separate planes      graphics architectures
  -----------------------------------------------------------------------

Do not assume that `0xFFFF` means white or that `0x0000` means black
without confirming the pixel format and color interpretation. In RGB565,
for example, `0xFFFF` is white, while `0x0000` is black; in an
indexed-color mode these values may simply be palette indices.

For RGB565, a common packing convention is:

``` c
uint16_t pack_rgb565(uint8_t r, uint8_t g, uint8_t b) {
    return ((r & 0xF8) << 8) |
           ((g & 0xFC) << 3) |
           (b >> 3);
}
```

The exact memory byte order may differ from the logical 16-bit value.
Confirm endianness and pitch/stride before manipulating framebuffer
memory.

### 2.2 Transparency and Alpha

There are three common transparency models.

**Color-key transparency**\
A specific source color means "do not draw this pixel." It is usually
binary: a pixel is either copied or skipped.

**Binary mask transparency**\
A separate mask determines whether a source pixel is visible. This is
useful when every possible source color must remain available.

**Alpha transparency**\
Each pixel or draw operation has an opacity value. A value of 0 is fully
transparent and a value of 1 (or the maximum integer value) is fully
opaque.

These methods are not interchangeable. A color key cannot express
partial opacity. A binary mask cannot express a smooth translucent edge
unless additional coverage levels are supported.

### 2.3 Compositing and Blend Equations

For a source color `S`, destination color `D`, and opacity `a` in the
range 0 to 1, the basic source-over equation is:

``` text
Out = S * a + D * (1 - a)
```

This equation is applied per color channel. For an 8-bit channel, an
integer implementation can use a scale of 255:

``` c
out = (src * alpha + dst * (255 - alpha) + 127) / 255;
```

The `+127` provides rounding rather than always truncating downward.

If the source has its own per-pixel alpha `As` and the draw operation
has global opacity `Ag`, the effective opacity is commonly:

``` text
A = As * Ag
```

The exact equation changes when using premultiplied alpha. In
premultiplied representation, RGB channels have already been multiplied
by alpha; using the straight-alpha equation on premultiplied data
produces incorrect edges and brightness.

**Important:** alpha blending is not the same as a bitwise `OR`, `AND`,
or `XOR` operation. A blend mode must be implemented by arithmetic or by
a dedicated blending unit.

### 2.4 Logical Raster Operations

Logical raster operations work on individual bits. They do not perform
color-aware interpolation.

  Operation   Bitwise meaning   Typical use
  ----------- ----------------- ------------------------------------------------
  COPY        `D = S`           Ordinary opaque copy
  AND         `D = D & S`       Bit masking
  OR          `D = D \| S`      Combining bit fields or setting bits
  XOR         `D = D ^ S`       Reversible toggling, simple inversion patterns
  NOT         `D = ~D`          Bitwise complement, where supported

The visual result of a logical operation depends on the pixel encoding.
An AND mask that works on a monochrome bitmap may produce unexpected
colors in RGB565.

A raster operation does not automatically know which pixels are
transparent. Transparency testing must be performed separately unless
the hardware explicitly combines color-key comparison with the raster
operation.

### 2.5 Coordinate Systems, Clipping, and Memory Layout

Before implementing an effect, establish:

-   whether coordinates are screen-relative or world-relative;
-   whether the origin is at the top-left or bottom-left;
-   whether rectangle endpoints are inclusive or exclusive;
-   whether negative coordinates are allowed;
-   whether drawing clips automatically at screen edges;
-   whether the framebuffer uses a row stride larger than its visible
    width;
-   whether source and destination rectangles may overlap.

A common framebuffer address calculation is:

``` c
pixel_address = base + y * pitch_bytes + x * bytes_per_pixel;
```

Do not replace `pitch_bytes` with `screen_width * bytes_per_pixel`
unless the platform guarantees tightly packed rows.

For a half-open rectangle, the valid pixels satisfy:

``` text
x1 <= x < x2
y1 <= y < y2
```

Its width and height are `x2 - x1` and `y2 - y1`. Other APIs use
inclusive endpoints; verify the convention to avoid off-by-one errors.

------------------------------------------------------------------------

## 3. Sprite Effects

### 3.1 Color-Key Transparency

**Purpose:** Make one designated source color invisible while copying
all other source pixels.

**Examples:** A character with a flat background, a projectile, foliage,
or an icon stored on a fixed-color canvas.

**Conceptual rule:**

``` c
if (src_pixel != key_color) {
    dst_pixel = src_pixel;
}
// Otherwise, leave the destination unchanged.
```

This is a comparison-and-skip operation, not an alpha blend.

**Pseudocode:**

``` c
for each pixel (x, y) in sprite:
    color = read_source(x, y)

    if color != transparent_key:
        write_destination(dst_x + x, dst_y + y, color)
```

**Hardware-style illustration (unverified pseudocode):**

``` c
accel->transparent_color = TRANSPARENT_KEY;
accel->use_transparency = 1;
accel->operation = OP_COPY;
```

The names above are illustrative. A real accelerator may use a
color-compare register, a transparency bit, a sprite attribute, or a
separate mask.

**Important details:**

-   The key must match the stored pixel value exactly unless the
    hardware supports a tolerance.
-   The key color must not also be needed as a visible color in the
    sprite.
-   Filtering or scaling can create edge colors that do not equal the
    key, producing halos. Nearest-neighbor scaling or pre-cleaned edge
    pixels are often preferable for pixel art.
-   If the source is palette-indexed, the key may be an index rather
    than an RGB color.
-   A transparent source pixel must normally leave the destination
    unchanged, not write the key color into it.

**Common failure:** Setting black as the key without checking the asset.
This makes every legitimate black pixel disappear.

### 3.2 Sprite Inversion and Negative Effects

**Purpose:** Create a negative, damage, shield, or temporary
invulnerability appearance.

There are multiple meanings of "invert":

1.  **Bitwise inversion:** complement every bit.
2.  **Channel inversion:** replace each channel value `C` with
    `MAX - C`.
3.  **XOR against a fixed mask:** toggle selected bits.
4.  **Palette remapping:** map each palette index to a chosen alternate
    color.

These produce different results.

For an 8-bit RGB channel:

``` text
R' = 255 - R
G' = 255 - G
B' = 255 - B
```

For a packed pixel, a bitwise complement is:

``` c
inverted = (~pixel) & PIXEL_FORMAT_MASK;
```

The format mask is essential: complementing a 16-bit value is not
necessarily the same as producing a visually correct RGB negative.

An XOR with all bits set within the pixel format is equivalent to
bitwise complement:

``` c
inverted = pixel ^ PIXEL_FORMAT_MASK;
```

It is **not** generally correct to use an unexplained expression such as
`(src XOR dst) XOR 0xFFFF` for sprite inversion. That expression depends
on the destination and is not simply a negative of the source.

**Preferred retro implementations:**

-   For indexed color: use a remapped palette or alternate palette bank.
-   For RGB565: unpack channels, invert them, and repack; or use a
    verified format-specific lookup table.
-   For a quick reversible highlight: XOR can be appropriate, but only
    when the mask and destination behavior are intentional.

### 3.3 Flipping, Rotation, and Scaling

These are geometric sprite transformations rather than color effects.

**Horizontal flip:**

``` text
source_x = sprite_width - 1 - destination_x
```

**Vertical flip:**

``` text
source_y = sprite_height - 1 - destination_y
```

**Nearest-neighbor scaling:** Map each destination pixel to a source
pixel. This preserves hard pixel edges and is usually the safest default
for pixel art.

Arbitrary rotation may be expensive or unavailable on older hardware.
Alternatives include pre-rendered frames, tile rearrangement, or a small
set of discrete orientations.

Check whether the platform supports transformations in hardware or
whether the sprite must be transformed in memory before drawing.

### 3.4 Palette and Color Replacement

Palette-based graphics make global color changes especially efficient. A
palette swap can turn a normal sprite into a poisoned, frozen,
underwater, or invulnerable version without changing the sprite bitmap.

A simple remap is:

``` text
output_color = palette_remap[input_index]
```

A palette change can affect every object using that palette. If only one
sprite should change, use a dedicated palette bank or draw-time
remapping if supported.

**Pitfall:** Changing a shared palette entry may unintentionally recolor
the background, UI, or other sprites.

------------------------------------------------------------------------

## 4. Composition and Layer Effects

### 4.1 Layer Compositing

Layer compositing determines how an image is combined with content
already drawn behind it.

A typical scene may contain:

1.  background;
2.  distant scenery or parallax layers;
3.  terrain and tile maps;
4.  objects and characters;
5.  particles and foreground effects;
6.  HUD and menus.

The order matters. If the HUD is drawn before a full-screen flash
overlay, the overlay may tint the HUD too. If that is not intended, draw
the HUD after the world-space effect or restrict the overlay to the
gameplay viewport.

A layer is not automatically translucent. It may be opaque, color-keyed,
masked, alpha-blended, or palette-based.

### 4.2 Alpha Blending

**Purpose:** Combine foreground and background colors with a controlled
opacity.

**Examples:** translucent water, glass, smoke, ghost sprites, soft UI
overlays.

**Straight-alpha source-over equation:**

``` text
Out = Source * Alpha + Destination * (1 - Alpha)
```

For an 8-bit alpha value `a` from 0 to 255:

``` c
out = (src * a + dst * (255 - a) + 127) / 255;
```

Apply this per color channel.

**Pseudocode:**

``` c
for each pixel:
    if source_is_valid:
        dst = blend(source, dst, opacity)
```

**Hardware-style illustration (unverified pseudocode):**

``` c
accel->operation = OP_BLEND;
accel->blend_mode = BLEND_MODE_ALPHA;
accel->alpha = opacity;
```

The original notes used `BLEND_MODE_ADD` next to an alpha-blending
equation. This is inconsistent: additive blending and alpha blending are
different modes. Select the mode that matches the intended equation.

**Retro alternatives when alpha blending is unavailable:**

-   use a checkerboard or ordered-dither pattern to simulate partial
    coverage;
-   use a palette variant with darker or lighter colors;
-   precompute several opacity frames;
-   use a hardware-supported shadow/highlight mode if one exists.

### 4.3 Additive and Subtractive Blending

**Additive blending** brightens the destination:

``` text
Out = min(MAX, Destination + Source * Intensity)
```

Useful for magic, sparks, energy weapons, and bright highlights.

**Subtractive blending** darkens the destination:

``` text
Out = max(0, Destination - Source * Intensity)
```

Useful for darkening overlays or stylized lighting.

These operations are channel arithmetic, not logical OR and AND.
Saturation and clamping are required to prevent channel overflow or
underflow.

For RGB565, perform arithmetic on unpacked channel values or use a
verified hardware mode. Adding packed 16-bit words directly can cause
carries to cross channel boundaries.

### 4.4 Masking

**Purpose:** Restrict an image or effect to a defined shape or region.

**Examples:** binocular view, circular spotlight, minimap window,
status-bar fill, silhouette, or patterned reveal.

A binary mask commonly uses:

``` text
if mask_pixel_is_set:
    output = source_pixel
else:
    output = destination_pixel
```

This is conceptually clearer than saying "the destination equals source
AND mask," which is only correct for certain bit-level mask
representations.

For a bitwise mask:

``` c
result = source & mask;
```

This operation is valid only if the mask bits are encoded to preserve
the intended source bits. It does not automatically create a clean
visual stencil for arbitrary RGB pixels.

**Two common mask conventions:**

-   **1 = visible, 0 = hidden**
-   **1 = hidden, 0 = visible**

Document which convention is used. Invert the mask if the hardware
expects the opposite convention.

A soft mask requires alpha or multiple coverage levels; a one-bit mask
can only provide hard edges.

### 4.5 Priority, Ordering, and Transparency Interaction

A correct transparency test does not guarantee correct layering. The
renderer must also know which object is in front.

Typical priority approaches include:

-   draw-order sorting;
-   a fixed layer priority;
-   per-sprite priority bits;
-   a depth or priority buffer;
-   tile priority combined with sprite priority.

Define how ties are resolved. Also define whether transparent pixels
write priority/depth information. In most simple 2D pipelines, a
transparent pixel should not overwrite either the destination color or
the relevant visibility state.

------------------------------------------------------------------------

## 5. Pattern and System Effects

### 5.1 Pixelation and Mosaic

**Purpose:** Make an image appear as larger blocks of color.

**Examples:** teleportation, low-resolution transitions, damaged-screen
effects, retro censoring, or stylized focus.

A mosaic is primarily a **sampling and resampling** effect, not a
bitwise AND pattern.

For block size `B`, a simple nearest-sample mosaic is:

``` text
sample_x = floor(x / B) * B
sample_y = floor(y / B) * B
output(x, y) = source(sample_x, sample_y)
```

A block-average mosaic instead averages all pixels in each block. The
nearest-sample version is cheaper and tends to look more deliberately
pixelated.

**Implementation options:**

-   render the scene to a smaller off-screen buffer and scale it up
    using nearest-neighbor sampling;
-   sample one pixel per block from the existing framebuffer;
-   draw large colored rectangles based on representative block colors;
-   use a precomputed low-resolution version of the image.

A checkerboard or bit pattern can create a dither or dissolve effect,
but it does not by itself create a mosaic.

### 5.2 Dithering

Dithering simulates intermediate colors or transparency using a spatial
pattern of available colors.

**Ordered dithering:** Compare pixel brightness or opacity with a
repeating threshold matrix, such as a 2×2 or 4×4 Bayer matrix.

Conceptually:

``` text
visible = opacity > threshold_matrix[x mod N][y mod N]
```

**Error-diffusion dithering:** Distribute quantization error to
neighboring pixels. It can produce good tonal transitions but is often
more expensive and less suitable for dynamic real-time scenes.

Dithering is especially useful when the target palette is limited. Keep
the pattern stable in screen space or object space deliberately; moving
patterns can shimmer.

### 5.3 Area and Rectangle Filling

**Purpose:** Fill a rectangular region with a solid color.

**Examples:** menu backgrounds, health bars, panel borders, letterbox
bars, and simple platforms.

**Conceptual rule:**

``` text
for y in [y1, y2):
    for x in [x1, x2):
        destination(x, y) = fill_color
```

**Hardware-style illustration (unverified pseudocode):**

``` c
accel->operation = OP_FILL;
accel->fill_color = RED;
accel->x = x1;
accel->y = y1;
accel->width = x2 - x1;
accel->height = y2 - y1;
```

The actual API may require destination address, pitch, inclusive
endpoints, or a separate fill command.

For a health bar, calculate the filled width from a clamped ratio:

``` c
ratio = clamp((float)health / max_health, 0.0f, 1.0f);
filled_width = (int)(bar_width * ratio);
```

Handle `max_health == 0` explicitly. Avoid drawing outside the bar's
clipping rectangle.

### 5.4 Raster Bars and Scanline Effects

Raster effects change color or position by scanline or by a small group
of scanlines.

**Examples:** classic demo-scene color bars, heat haze, water
distortion, and horizontal palette bands.

A scanline effect may be implemented by:

-   changing palette registers during vertical scan;
-   changing a horizontal scroll register at a scanline boundary;
-   drawing thin colored rectangles;
-   applying a per-row color transform in software.

Hardware timing is critical. If a register update misses the intended
scanline, the effect may appear one line late or flicker. The exact
timing mechanism is platform-specific and must be verified against the
hardware documentation.

------------------------------------------------------------------------

## 6. Lighting and Temporal Effects

### 6.1 Shadows

**Purpose:** Make an object appear grounded or create depth.

Common retro shadow techniques:

1.  **Blob shadow:** Draw a flattened dark ellipse or sprite beneath the
    character.
2.  **Silhouette shadow:** Draw a darkened copy of the sprite offset
    from its original position.
3.  **Palette shadow:** Use a darker palette variant.
4.  **Dark overlay:** Blend a translucent dark shape over the
    background.
5.  **Dithered shadow:** Approximate transparency using a pattern.

A simple alpha shadow over destination `D` with black source `0` is:

``` text
Out = D * (1 - Alpha)
```

The expression `D + shadow_color * intensity` is not a correct general
formula for a dark shadow when `shadow_color` is black. Additive
blending with black leaves the destination unchanged. Use alpha
compositing with a dark source, subtractive blending, or a
palette/dither method.

For pixel art, a deliberately designed shadow sprite often looks better
than a blurred modern-style shadow.

### 6.2 Highlights and Glow

A highlight can be a lighter palette variant, a bright outline, or an
additive overlay.

For additive glow:

``` text
Out = min(MAX, D + Glow * Intensity)
```

A convincing glow often has two parts:

-   a bright core with crisp edges;
-   a larger, lower-intensity halo.

On hardware without blending, approximate the halo with a few palette
levels, dither patterns, or pre-rendered frames. Avoid assuming that a
single bright OR operation will create a smooth glow.

### 6.3 Flicker and Blink

**Purpose:** Alternate visibility or appearance over time.

**Examples:** invulnerability, blinking pickups, warning indicators,
ghost effects.

A basic blink is controlled by elapsed time:

``` c
visible = (elapsed_ms % period_ms) < visible_duration_ms;
```

This is preferable to tying the effect to an arbitrary number of
rendered frames. Frame-rate-based logic can change its speed when
rendering performance changes.

For a 50% duty cycle:

``` c
visible = ((elapsed_ms / half_period_ms) % 2) == 0;
```

The effect may alternate between:

-   visible and invisible;
-   normal and tinted;
-   normal and inverted palette;
-   opaque and dithered.

Do not implement invisibility by drawing nothing if the previous frame's
sprite pixels remain in a persistent framebuffer. The scene must be
redrawn or the old sprite area restored, otherwise the sprite may leave
trails.

### 6.4 Flash and Hit Feedback

**Purpose:** Provide immediate visual feedback for damage, explosions,
impacts, or magic.

A flash can be implemented as:

-   a white or colored alpha overlay;
-   a sprite tint;
-   a palette swap;
-   a brief additive highlight;
-   a full-screen overlay limited to the gameplay viewport.

For a white flash:

``` text
Out = D * (1 - a) + White * a
```

For a red damage tint:

``` text
Out = D * (1 - a) + Red * a
```

A bitwise OR with white (`D | 0xFFFF`) normally sets all bits and
produces white in common packed RGB formats. It does not produce a
controllable flash intensity. OR with a red value sets selected bits and
is not equivalent to a red alpha tint.

A flash should have a defined duration and intensity curve. A short,
strong initial flash followed by a rapid decay is often more readable
than a long constant overlay.

### 6.5 Fade In and Fade Out

**Purpose:** Gradually transition between a scene and a solid color,
usually black.

For a fade to a target color `F`:

``` text
Out = D * (1 - a) + F * a
```

-   Fade out to black: `F = black`, with `a` increasing from 0 to 1.
-   Fade in from black: `F = black`, with `a` decreasing from 1 to 0.

Use elapsed time rather than a blocking loop:

``` c
progress = clamp(elapsed_ms / duration_ms, 0.0f, 1.0f);
alpha = progress; // Fade out
```

For fade-in, use `alpha = 1.0f - progress`.

The original pattern of looping through alpha values and issuing draw
operations is only valid if the hardware completes each operation
synchronously and the display is updated between iterations. In most
real-time renderers, such a loop runs too quickly and does not create a
visible transition. Update the fade once per frame.

If alpha blending is unavailable, use a sequence of palette steps,
ordered dithering, or precomputed transition frames.

------------------------------------------------------------------------

## 7. Screen-Space Effects

### 7.1 Screen Shake and Screen Offset

**Purpose:** Shift the rendered view to communicate impact, explosion,
recoil, or environmental motion.

A screen-space offset maps each destination pixel to a source
coordinate:

``` text
source_x = destination_x + offset_x
source_y = destination_y + offset_y
```

This is a sampling/copy operation. It is not enough to set `src_x` and
`src_y` unless the accelerator's source rectangle, destination
rectangle, and address semantics are known.

**Recommended architecture:** Apply shake to the camera or world render
origin, not by repeatedly copying the final framebuffer in place. This
avoids read/write overlap and makes it easier to keep the HUD fixed.

If the entire framebuffer must be shifted:

1.  copy from a separate source buffer, or use a hardware operation that
    explicitly supports overlapping regions;
2.  define what appears in newly exposed edges (clear color, border
    fill, wrap, or overscan);
3.  clamp or wrap the source coordinates as required;
4.  draw fixed screen-space UI after the shake if the UI should remain
    stable.

**Hardware-style illustration (unverified pseudocode):**

``` c
accel->src_addr = source_buffer;
accel->dst_addr = destination_buffer;
accel->src_x = offset_x;
accel->src_y = offset_y;
accel->width = viewport_width;
accel->height = viewport_height;
```

Do not assume that identical source and destination addresses are safe
for a shifted copy. Overlapping copies may smear or overwrite pixels
unless the engine defines a safe traversal order or uses an intermediate
buffer.

### 7.2 Scrolling and Parallax

Scrolling changes the relationship between world coordinates and screen
coordinates:

``` text
screen_x = world_x - camera_x
screen_y = world_y - camera_y
```

Parallax layers move at different fractions of camera speed:

``` text
layer_camera_x = camera_x * parallax_factor
```

A distant background may use a factor below 1.0. A foreground layer may
move faster than the camera, though this is less common.

Older hardware may provide dedicated horizontal/vertical scroll
registers per tile plane. This is usually more efficient than copying
the entire framebuffer. Confirm wrap behavior and whether scroll values
are signed, pixel-based, tile-based, or constrained to a hardware range.

### 7.3 Clipping and Viewports

**Purpose:** Prevent drawing outside a specified rectangle.

**Examples:** HUD panels, minimaps, split-screen regions, dialogue
windows, and scrolling viewports.

For a half-open clipping rectangle:

``` text
clip_x1 <= x < clip_x2
clip_y1 <= y < clip_y2
```

A pixel outside the rectangle is discarded.

**Hardware-style illustration (unverified pseudocode):**

``` c
accel->clip_x1 = 50;
accel->clip_y1 = 30;
accel->clip_x2 = 270;
accel->clip_y2 = 170;
```

Verify whether the hardware uses inclusive or exclusive maximum
coordinates. Also verify whether clipping applies to fills, copies,
sprites, and lines equally.

If hardware clipping is unavailable, intersect the requested drawing
rectangle with the viewport in software before issuing the draw.

### 7.4 Screen Transitions

Common retro transitions include:

-   fade to/from black or a palette color;
-   vertical or horizontal curtain/wipe;
-   checkerboard or ordered-dither dissolve;
-   expanding or contracting iris;
-   tile-by-tile reveal;
-   mosaic/pixelation;
-   palette cycling or palette fade.

A transition should have a deterministic progress value from 0 to 1 and
a clearly defined direction. It should not depend on how many times a
rendering loop happens to execute.

For a wipe, compare each pixel coordinate with a moving boundary. For an
iris, compare the pixel's distance from a center point with a changing
radius. For a tile reveal, use a deterministic ordering of tile indices.

------------------------------------------------------------------------

## 8. Worked Example: Player Damage Feedback

This example combines a short red tint, camera shake, and recovery. It
is intentionally written as engine-independent pseudocode. It does not
assume that the illustrative `accel` structure exists on the Kiss
platform.

### 8.1 Desired behavior

1.  On damage, start a short red flash.
2.  Apply a brief camera shake.
3.  Optionally blink the player during a temporary invulnerability
    period.
4.  Return smoothly to the normal image.
5.  Keep the HUD stable unless the design explicitly calls for a
    full-screen effect.

### 8.2 State-based implementation

``` c
typedef struct {
    float flash_timer;
    float flash_duration;
    float shake_timer;
    float shake_duration;
    float shake_strength;
    float invulnerability_timer;
} DamageEffect;

void start_damage_effect(DamageEffect *fx) {
    fx->flash_timer = 0.0f;
    fx->flash_duration = 120.0f;       // milliseconds
    fx->shake_timer = 0.0f;
    fx->shake_duration = 180.0f;       // milliseconds
    fx->shake_strength = 3.0f;          // pixels
    fx->invulnerability_timer = 900.0f; // milliseconds
}

void update_damage_effect(DamageEffect *fx, float delta_ms) {
    fx->flash_timer += delta_ms;
    fx->shake_timer += delta_ms;

    if (fx->invulnerability_timer > 0.0f) {
        fx->invulnerability_timer -= delta_ms;
        if (fx->invulnerability_timer < 0.0f)
            fx->invulnerability_timer = 0.0f;
    }
}
```

The timers advance once per game update. Rendering reads their current
values but does not modify them.

### 8.3 Calculate flash intensity

``` c
float get_flash_alpha(const DamageEffect *fx) {
    float t = fx->flash_timer / fx->flash_duration;

    if (t >= 1.0f)
        return 0.0f;

    // Strong at the beginning, then fades out.
    return 1.0f - t;
}
```

### 8.4 Calculate camera shake

A deterministic sequence is preferable for reproducible tests:

``` c
void get_shake_offset(const DamageEffect *fx, int *x, int *y) {
    if (fx->shake_timer >= fx->shake_duration) {
        *x = 0;
        *y = 0;
        return;
    }

    // Illustrative sequence; replace with a seeded pattern if needed.
    int phase = (int)(fx->shake_timer / 30.0f);
    static const int shake_x[] = { -3, 2, -2, 1, 0, 0 };
    static const int shake_y[] = {  1,-2,  2,-1, 0, 0 };

    int index = phase;
    if (index < 0) index = 0;
    if (index > 5) index = 5;

    *x = shake_x[index];
    *y = shake_y[index];
}
```

A production implementation should scale the offsets by
`shake_strength`, use a seeded pseudo-random sequence, or select a
precomputed pattern. Avoid calling an unseeded random function
independently for every pixel or every render pass.

### 8.5 Render order

``` c
void render_game(const DamageEffect *fx) {
    int shake_x, shake_y;
    get_shake_offset(fx, &shake_x, &shake_y);

    begin_frame();

    // World and gameplay objects move with the camera.
    set_camera_offset(base_camera_x + shake_x,
                      base_camera_y + shake_y);
    draw_world();
    draw_enemies();
    draw_player_with_invulnerability_state(fx->invulnerability_timer);
    draw_particles();

    // Apply the damage tint to the gameplay viewport only.
    float alpha = get_flash_alpha(fx);
    if (alpha > 0.0f)
        draw_color_overlay(RED, alpha, GAMEPLAY_VIEWPORT);

    // UI is drawn last and therefore remains stable.
    draw_hud();

    end_frame();
}
```

`draw_color_overlay` is an abstract operation. Implement it using a
verified alpha blend, palette effect, or dithered approximation.

### 8.6 Important corrections

-   Do not run a blocking `for` loop to animate the shake or fade. The
    effect must evolve over successive frames.
-   Do not repeatedly copy a shifted framebuffer onto itself unless
    overlapping-copy behavior is explicitly supported.
-   Do not use bitwise OR as a substitute for a controllable color tint.
-   Decide whether the flash affects the player only, the gameplay
    viewport, or the entire screen.
-   Decide whether the HUD should shake or flash; render it in the
    appropriate pass.

------------------------------------------------------------------------

## 9. Implementation Architecture

A robust effect system separates **effect state**, **effect update**,
and **effect rendering**.

### 9.1 Effect lifecycle

A typical lifecycle is:

1.  **Trigger:** gameplay event starts an effect.
2.  **Initialize:** set duration, strength, color, and parameters.
3.  **Update:** advance timers using elapsed time.
4.  **Evaluate:** calculate current intensity, offset, visibility, or
    palette state.
5.  **Render:** issue drawing commands.
6.  **Expire:** stop applying the effect after its duration.

This prevents gameplay logic from becoming entangled with low-level
drawing commands.

### 9.2 Separate world-space and screen-space effects

World-space effects follow objects or the camera:

-   sprite tint;
-   object shadow;
-   particles;
-   local glow;
-   object-specific flicker.

Screen-space effects operate on the viewport or final image:

-   screen shake;
-   full-screen fade;
-   global color tint;
-   scanlines;
-   screen transition.

A useful render order is:

``` text
Clear / restore background
    -> Background layers
    -> World geometry and tile maps
    -> World sprites and particles
    -> World-space lighting or tint
    -> Screen-space gameplay overlays
    -> HUD and menus
    -> Display/present
```

The exact order depends on the desired visual result. Document any
intentional deviation.

### 9.3 Avoid hidden state in the accelerator

Before starting an accelerator operation, explicitly set every state
field that affects the operation:

-   source and destination addresses;
-   source and destination coordinates;
-   width, height, and pitch;
-   pixel format;
-   transparency key and enable flag;
-   blend mode and alpha;
-   raster operation;
-   clipping rectangle;
-   completion/interrupt behavior.

Do not assume that a previous command left the accelerator in a known
state. Persistent register state is a common source of intermittent
rendering bugs.

### 9.4 Synchronization and command completion

A hardware accelerator may be synchronous, asynchronous, or queue-based.

If commands are asynchronous:

-   do not overwrite source data before the accelerator has finished
    reading it;
-   do not read destination data before completion;
-   use the documented busy flag, interrupt, fence, or queue
    synchronization;
-   avoid submitting dependent operations out of order;
-   confirm whether the display scans the buffer while it is being
    modified.

Double buffering or a documented page-flip mechanism can prevent
tearing. Never assume a `START_BIT` write means the operation has
completed.

------------------------------------------------------------------------

## 10. Performance, Timing, and Reliability

### 10.1 Cost model

An effect's cost depends on more than its mathematical complexity.
Consider:

-   number of pixels touched;
-   source and destination memory bandwidth;
-   bytes per pixel;
-   cache behavior;
-   overdraw;
-   whether the operation is accelerated;
-   synchronization overhead;
-   whether the effect requires an extra framebuffer pass.

A full-screen blend every frame can be much more expensive than tinting
one small sprite.

### 10.2 Prefer the simplest supported implementation

Typical preference order:

1.  dedicated hardware feature, if its behavior is verified;
2.  palette or scroll-register change;
3.  hardware fill/copy/blend operation;
4.  optimized CPU loop;
5.  precomputed frames or lookup tables;
6.  full-screen software post-processing.

This is not an absolute ranking. A palette swap may be ideal for a
global fade but unsuitable if several objects share the same palette and
must remain unchanged.

### 10.3 Frame-rate independence

Use elapsed time (`delta_ms` or fixed simulation ticks) for effect
duration. Avoid defining an effect as "exactly 10 rendered frames"
unless a fixed frame rate is guaranteed.

For deterministic gameplay, update effects on a fixed simulation
timestep and render their interpolated state separately.

### 10.4 Memory and buffer safety

Validate:

-   source and destination bounds;
-   row pitch and pixel size;
-   alignment requirements;
-   buffer ownership;
-   overlap rules;
-   integer overflow in address and size calculations;
-   behavior at negative coordinates and screen edges.

For a rectangle copy, clip both source and destination consistently. A
clipped destination may require adjusting the source origin by the same
amount.

### 10.5 Retro authenticity

Authenticity is not achieved by applying every effect available in a
modern renderer. Respect the target system's visual constraints:

-   limited palette;
-   intentional pixel clusters;
-   nearest-neighbor scaling;
-   restrained transparency;
-   deliberate dithering;
-   tile and sprite limits;
-   characteristic scanline or raster behavior, if appropriate.

An effect should support readability and game feedback rather than
obscure the artwork.

------------------------------------------------------------------------

## 11. Testing and Visual Validation

Test every effect in isolation before combining effects.

  -----------------------------------------------------------------------
  Test                                What to verify
  ----------------------------------- -----------------------------------
  Color-key sprite                    Intended key pixels disappear;
                                      legitimate same-colored pixels are
                                      preserved

  Inversion                           Correct channel or bit-level result
                                      for the actual pixel format

  Alpha blend                         0% shows destination; 100% shows
                                      source; intermediate values are
                                      monotonic

  Additive blend                      No channel overflow or
                                      cross-channel corruption

  Mask                                Both visible and hidden regions
                                      behave as documented

  Mosaic                              Blocks have the expected size and
                                      stable sampling origin

  Fill                                Correct dimensions, color, and
                                      clipping

  Flicker                             Stable timing at different frame
                                      rates; no stale sprite trails

  Flash                               Correct scope, intensity, and
                                      duration

  Fade                                Smooth or intentionally stepped
                                      progression; no blocking loop

  Screen shake                        No smear, unintended wrap, or
                                      exposed uninitialized edges

  Clipping                            Correct behavior at all four
                                      boundaries

  Combined effects                    Correct render order and no
                                      accidental HUD tint/shake
  -----------------------------------------------------------------------

Also test the smallest and largest supported resolutions, different
pixel formats if applicable, and boundary coordinates.

------------------------------------------------------------------------

## 12. Common Mistakes and Corrections

  -------------------------------------------------------------------------
  Incorrect assumption or  Why it is wrong          Correct approach
  implementation                                    
  ------------------------ ------------------------ -----------------------
  "Black is always         Black may be a           Define and document an
  transparent."            legitimate sprite color; explicit key or mask.
                           transparency is          
                           format/asset-specific.   

  "Alpha blending is an    Alpha interpolation and  Select the blend mode
  ADD operation."          additive light           that matches the
                           accumulation use         desired equation.
                           different equations.     

  "Mosaic is               AND changes bits; it     Sample or average one
  `source AND pattern`."   does not group pixels    value per block and
                           into blocks.             replicate it.

  "OR with white creates a OR sets bits; it does    Blend toward white or
  controllable flash."     not interpolate          use palette steps.
                           intensity.               

  "Adding black creates a  Adding zero leaves the   Blend toward black,
  shadow."                 destination unchanged.   subtract, or use a dark
                                                    palette/mask.

  "XOR with the            The result depends on    Invert source channels
  destination inverts a    the old destination and  or use a
  sprite."                 may not be a source      format-specific
                           negative.                mask/remap.

  "A loop over alpha       A tight loop may finish  Advance alpha over
  values creates a fade."  before a display         multiple frames using
                           refresh.                 elapsed time.

  "Copying a framebuffer   Overlap may overwrite    Use a separate buffer
  with an offset is always pixels that have not yet or documented
  safe in place."          been read.               overlap-safe copy.

  "Setting clip            Some engines apply       Verify clipping per
  coordinates guarantees   clipping only to         command type or clip in
  all commands clip."      selected operations.     software.

  "A transparent pixel     That destroys the        Skip the destination
  writes its key color."   background under the     write for transparent
                           sprite.                  pixels.

  "The accelerator state   Registers may retain     Set all relevant state
  is already correct."     values from a previous   explicitly before each
                           command.                 operation.

  "A start command means   Hardware may execute     Wait or synchronize
  completion."             asynchronously.          using the documented
                                                    mechanism.
  -------------------------------------------------------------------------

------------------------------------------------------------------------

## 13. Hardware/API Verification Checklist

The original notes contain code-shaped examples, but no Kiss SDK header,
register map, or programming manual was supplied. Before translating
this guide into production code, verify the following against the actual
platform documentation.

### 13.1 Device and pixel format

-   [ ] Supported display resolutions and refresh rates
-   [ ] Supported pixel formats and channel bit layouts
-   [ ] Palette size, palette organization, and palette update timing
-   [ ] Framebuffer base address, pitch, and alignment
-   [ ] Byte order and memory access restrictions

### 13.2 Drawing operations

-   [ ] Whether copy, fill, blend, AND, OR, XOR, and NOT are supported
-   [ ] Exact operation/opcode names and numeric values
-   [ ] Whether color-key transparency is supported
-   [ ] Whether transparency applies before or after the raster
    operation
-   [ ] Whether alpha is per-pixel, per-command, or unavailable
-   [ ] Supported blend equations and alpha range
-   [ ] Whether masks are supported and what bit convention they use
-   [ ] Whether clipping is hardware-managed and which commands honor it

### 13.3 Geometry and memory

-   [ ] Source/destination coordinate semantics
-   [ ] Inclusive or exclusive rectangle endpoints
-   [ ] Width/height limits and alignment requirements
-   [ ] Behavior for negative or out-of-range coordinates
-   [ ] Overlapping source/destination copy behavior
-   [ ] Scaling, flipping, rotation, and scroll support

### 13.4 Execution model

-   [ ] Synchronous or asynchronous command execution
-   [ ] Busy/status register or completion interrupt
-   [ ] Command queue capacity and ordering guarantees
-   [ ] Required memory barriers or cache maintenance
-   [ ] Safe buffer-swap/page-flip procedure
-   [ ] Whether display scanout can overlap writes

### 13.5 Code integration

-   [ ] Replace all illustrative `OP_*`, `LOGIC_OP_*`, and
    `BLEND_MODE_*` values with verified definitions.
-   [ ] Replace illustrative `accel` fields with the real SDK interface.
-   [ ] Confirm the actual start/completion protocol; do not assume
    `START_BIT`.
-   [ ] Confirm that every example's source and destination addresses
    are valid.
-   [ ] Test every operation with known pixel patterns before using it
    in gameplay.

**Until this checklist is completed, the code snippets in this document
must be treated as conceptual pseudocode, not drop-in Kiss code.**

------------------------------------------------------------------------

## 14. Glossary

  -----------------------------------------------------------------------
  Term                                Definition
  ----------------------------------- -----------------------------------
  Alpha                               Opacity or coverage value
                                      associated with a pixel or draw
                                      operation

  Alpha blending                      Arithmetic combination of source
                                      and destination colors using alpha

  Bitwise operation                   Operation applied independently to
                                      the bits of stored values

  Color key                           A designated source color treated
                                      as transparent

  Compositing                         Combining multiple visual elements
                                      into one image

  Destination                         Buffer or pixel being modified by a
                                      rendering operation

  Dithering                           Spatial pattern used to approximate
                                      unavailable colors or opacity
                                      levels

  Framebuffer                         Memory containing pixel data for an
                                      image

  Palette                             Table mapping color indices to
                                      actual display colors

  Parallax                            Motion of layers at different rates
                                      to imply depth

  Pitch/stride                        Number of bytes between the starts
                                      of adjacent framebuffer rows

  Raster operation                    Logical or arithmetic operation
                                      applied while transferring pixels

  Source                              Image or pixel data read by a
                                      rendering operation

  Viewport                            Screen region showing a portion of
                                      the game world
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 15. Appendix A: Pseudocode Conventions

The following identifiers are illustrative only:

``` c
OP_COPY
OP_FILL
OP_BLEND
OP_LOGIC

LOGIC_OP_AND
LOGIC_OP_OR
LOGIC_OP_XOR

BLEND_MODE_ALPHA
BLEND_MODE_ADD
```

Likewise, the following structure is a conceptual placeholder:

``` c
accel->operation
accel->blend_mode
accel->logic_op
accel->fill_color
accel->transparent_color
accel->use_transparency
accel->src_addr
accel->dst_addr
accel->src_x
accel->src_y
accel->width
accel->height
accel->clip_x1
accel->clip_y1
accel->clip_x2
accel->clip_y2
accel->control
```

A real implementation may have different names, data types, command
packing, address spaces, or no equivalent feature at all. Do not copy
these fields into a project without checking the platform SDK.

------------------------------------------------------------------------

## 16. Appendix B: Reference Equations

### B.1 Source-over alpha blend

For each color channel:

``` text
Out = S * a + D * (1 - a)
```

### B.2 Integer alpha blend (8-bit alpha)

``` c
out = (src * alpha + dst * (255 - alpha) + 127) / 255;
```

### B.3 Additive blend

``` text
Out = min(MAX, D + S * intensity)
```

### B.4 Subtractive blend

``` text
Out = max(0, D - S * intensity)
```

### B.5 Channel inversion

``` text
C_inverted = MAX - C
```

### B.6 Bitwise inversion

``` c
inverted = (~pixel) & PIXEL_FORMAT_MASK;
```

### B.7 Color-key transparency

``` c
if (src_pixel != key_color)
    dst_pixel = src_pixel;
```

### B.8 Nearest-sample mosaic

``` text
sample_x = floor(x / block_size) * block_size
sample_y = floor(y / block_size) * block_size
out(x, y) = source(sample_x, sample_y)
```

### B.9 Camera transform

``` text
screen_position = world_position - camera_position
```

### B.10 Fade to a target color

``` text
Out = D * (1 - a) + FadeColor * a
```

------------------------------------------------------------------------

## Final Notes

This reference expands the original effect list into a
rendering-oriented guide and corrects several conceptual errors. It
intentionally distinguishes visual behavior from implementation details.

The most important implementation rule is simple: **choose the
mathematical operation that matches the visual effect, then map that
operation to a hardware feature only after verifying the target
platform's specification.**

The exact Kiss-specific register map, command values, supported blend
modes, memory layout, and synchronization protocol remain unverified
because the corresponding platform documentation was not part of the
supplied source.
