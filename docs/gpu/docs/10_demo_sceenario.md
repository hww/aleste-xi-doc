# GPU Demo and Benchmark Scenario

## Goal and Test Philosophy

We are not building an artistic showcase or duplicating work by porting every scene to two processors—we want **dry, honest, reproducible numbers** for a real, not-very-fast GPU. The test should be buildable within a reasonable timeframe, rely on minimal assets (procedurally generated or easily sourced), and ramp up from the cheapest operations to the heaviest ones to find the hardware's true limit in game-like scenarios.

Unified microprograms serve two modes:

* **Visual run (demo):** a clear load progression with an overlay and a result figure at the end of each scene.


* **`bench` mode:** the same compute kernels, but without story pauses or extra fluff—dry metrics output as a table.



---

## Supported Formats

* **8 bpp** — the primary working format across all scenes.


* **4 bpp** — a full mode (source and destination). Used, among other things, for live switching inside the sprite scene to clearly show throughput and object-count gains within the same budget.


* **Monochrome font source (1-bit glyphs -> colored output 8-bpp, 4-bpp):** tested via a dedicated character-drawing test (expanding a black-and-white glyph mask into colored pixels of the target format), without supporting `1 bpp` or `2 bpp` as framebuffer modes.


* **2 bpp** — excluded from the scenario and test codebase.



---

## General Principles and Frame Architecture

* **Double buffering:** all scenes use two buffers—we draw into the `back-buffer` while the `front-buffer` is displayed.


* **Frame lifecycle:** reset/prepare GPU state -> draw -> wait for end of frame (VBlank / synchronization) -> swap buffers.


* **Gaming focus:** we measure the cost of full or multi-layer game screen redraws (background, layers, sprites, clipping, affine transforms), not text scrolling.
* **Memory and bounds safety:** all operations explicitly account for row stride (`pitch`), buffer boundaries, and clipping; shifts and scrolling must not clobber unread data when regions overlap.


* **Measurements and overlay:** every frame measures FPS, CPU usage (%), and GPU usage (%). A compact overlay is always shown in the corner: `FPS | CPU % | GPU % | Test | Budget`.



---

## Command-Line Parameters (CLI)

* `--m N` — color mode (`8` or `4`, default `8`). If `--m` is omitted, the test runs `8 bpp` followed by `4 bpp`.


* `--b N` — rendering budget in VBlank frames (default `1` frame—a strict, honest ceiling). Values of `2` (~25–30 FPS, a solid gaming standard), `3`, and higher are supported to see how many objects the GPU can reach with a wider budget.


* `--t N` — duration of one phase/animation inside a scene in seconds (default `3–5` s; `10` s for the base fill).


* `--s N` — screen/buffer size in KB (`64` by default). If `--s` is omitted, the test progresses: `64` KB -> `32` KB.


* `--bench` — run without visual pauses and output a summary table to console/log.



### Budget Stop Rule (`--b`)

In scenes with increasing load, the number of elements doubles (`2, 4, 8, 16, 32...`, or `32, 64, 128...` for text) after the measurement stabilizes at the current step. As soon as frame render time exceeds the configured budget `--b`, growth stops, and the maximum sustainable element count and achieved FPS are recorded.

---

## Test Scenario

### Scene 1. Fill (Baseline Throughput)

* **Leitmotif:** lowest-budget GPU program—pure write bandwidth into video memory without branching or extra logic.


* **Duration:** `10` s.


* **Action:** full-screen fill with horizontal bands that may cycle/change color. Explicit check of `pitch` and frame boundaries.


* **On-screen result:** peak fill rate (Mpix/s and FPS).

### Scene 2. Second Layer of Horizontal Lines

* **Leitmotif:** cost of many small draw commands without blending or complex movement logic.


* **Action:** over a background fill, draw `N` horizontal lines in different colors (simple pixel copy/fill with slight shift/drop and color change).


* **Progression:** line count grows `2, 4, 8, 16, 32...` until hitting budget `--b`.


* **On-screen result:** maximum line count within budget `--b`.

### Scene 3. Fixed-Size Rectangle Rain

* **Leitmotif:** testing block fill/copy without transparency as primitive area changes.


* **Action:** over a background fill, draw rectangles without blending with simple falling/shifting and color changes (respecting bounds and clipping).


* **Progression:**
* Sizes: `2x2` -> `4x4` -> `8x8` -> `16x16` -> `32x32`.


* Within each size, rectangle count grows `2, 4, 8, 16...` until hitting budget `--b`.




* **On-screen result:** count/table of rectangles per size within budget `--b`.

### Scene 4. Character Rendering (Monochrome Font to Color)

* **Leitmotif:** speed of expanding 1-bit font glyphs into a color buffer (`8 bpp` / `4 bpp`)—the real cost of text output and UI.


* **Action:** clear the screen and draw `N` characters (no complex layout or line-wrap math—can draw overlapping with an offset or in a simple coordinate loop to measure glyph rendering itself).
* **Progression:** character count per frame grows `32, 64, 128, 256, 512...` until budget `--b` is consumed.
* **On-screen result:** maximum characters per frame and pure glyph rendering time.

### Scene 5. Color-Keyed Sprites

* **Leitmotif:** testing color-key transparency (`CMP` + conditional `MOV`, skipping write when matching the key) with minimal physics budget (`STEP = ±1`).


* **Action:** bouncing/moving sprites over a background. Inside the scene, perform a live switch from `8 bpp` to `4 bpp` (unless `--m` is locked), clearly showing the jump in sprite count within the same budget.


* **Progression:**
* Sizes: `16x16` -> `32x32` -> `64x64` -> `128x128`.


* Within each size, sprite count grows `2, 4, 8, 16...` until hitting budget `--b`.




* **On-screen result:** sprite limit by size for `8 bpp` and `4 bpp` (and the visible difference between `--b 1` and `--b 2`).

### Scene 6. Tiles and Game Scrolling

* **Leitmotif:** cost of full tile-screen redraw and overlaying an upper layer with transparency.


* **Assets:** minimal tile set (ready-made tileset/map or procedural pattern), without bloating asset prep.
* **Action:** opaque base tile layer across the screen + a scrolling upper layer (scroll step a multiple of tile size, e.g., `8` pixels) using color keying (`CMP` + conditional `MOV`, `STEP = ±1`).


* **Progression:** increase upper-layer tile density/count up to 100% coverage or until hitting budget `--b`.


* **On-screen result:** coverage percentage and upper-layer tile count within budget.

### Scene 7. Parallax and Clipping

* **Leitmotif:** realistic multi-layer game backdrop with mandatory hardware/software clipping at viewport edges.


* **Action:** background layer + up to 3 looping tile layers scrolling at different speeds (e.g., far layer at `1` px, mid layer at `2` px, near layer at `4` px per frame). Upper layers use color keying (`CMP` + conditional `MOV`).


* **Progression:** ramp layer fill up to ~80% of the screen, then remove layers one by one to record each layer's cost.


* **On-screen result:** cost of each additional parallax layer (in ms / % of budget).

### Scene 8. Sprite Rotation (Affine)

* **Leitmotif:** cost of affine sampling when rotating sprites without complicating game logic.


* **Action:** follows the sprite scene mechanics (color key + clipping at screen edges), except sprites rotate.


* **Progression:** rotating sprite count grows `2, 4, 8, 16...` until hitting budget `--b`.


* **On-screen result:** maximum rotating sprite count and performance drop relative to plain blitting.

### Scene 9. Sprite Scaling (Affine)

* **Leitmotif:** cost of affine scaling (zoom in / zoom out) and the impact of growing fill area + clipping when zoomed in.


* **Action:** follows the sprite scene mechanics, except sprites smoothly scale (zooming out and in, going past screen edges with mandatory clipping).


* **Progression:** scalable sprite count grows `2, 4, 8, 16...` until hitting budget `--b`.


* **On-screen result:** maximum scalable sprite count within budget `--b`.

### Scene 10. Line-by-Line Image Shift

* **Leitmotif:** a simple visual test of line-by-line image redrawing without load progression and without trying to hit budget `--b`.


* **Action:** load an image and shift horizontal lines—half in one direction, half in the other. Halfway through the test duration (`--t / 2`), switch to upward movement (accounting for `pitch`, boundaries, and clipping).


* **On-screen result:** no ramping up to the budget—just show the visual effect, record the statistics (`FPS`, `CPU %`, `GPU %`), and move on.

---

## Summary Screen and `bench` Output

After all scenes finish, a summary of the current run is displayed on screen (and when launched with `--bench`, formatted as a table with columns: `Scene | Mode (bpp) | Buffer (KB) | Budget (frames) | Max objects / result | FPS | CPU % | GPU %`).