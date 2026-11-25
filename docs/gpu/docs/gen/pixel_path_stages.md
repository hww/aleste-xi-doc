**Pixel Path Stages**

| Stage | Signal | Description |
| --- | --- | --- |
| 1 | <a id="idx_stored"></a>**idx_stored** | 20-bit index (15 word, 4 position, 1 page overflow) |
| 2 | <a id="word_out"></a>**word_out** | 15-bit word (integer part) |
| 3 | <a id="gc_rdata"></a>**gc_rdata** | 16-bit data from cache |
| 4 | <a id="pb_pixel_out"></a>**pb_pixel_out** | 16-bit pixel from blender (read); on a write the blender sends pixel + bit mask to the cache |
| 5 | <a id="wdata"></a>**wdata** | Written to destination register |
