**Cache FSM**

| State | Output | Description |
| --- | --- | --- |
| <a id="ST_IDLE"></a>**ST_IDLE** (initial) | — | Hits, write misses (allocate), posting to the write buffer, page changes, clean flushes |
| <a id="ST_FILL"></a>**ST_FILL** | — | Read one word from memory (read miss, merge fill or lazy fill); waits until the write buffer is empty |
| <a id="ST_WRITEBACK"></a>**ST_WRITEBACK** | — | FLUSH of a dirty channel: blocking write, not through the write buffer |

| From | To | Condition | Action |
| --- | --- | --- | --- |
| ST_IDLE | ST_IDLE | write miss, entry clean | allocate: TAG, DATA = pixel, DMASK = written nibbles; ack |
| ST_IDLE | ST_IDLE | write miss, entry dirty, buffer free | post old word to the buffer and allocate, same cycle; ack |
| ST_IDLE | ST_IDLE | page change pending, entry dirty, buffer free | post old word to the buffer |
| ST_IDLE | ST_IDLE | page change pending, entry clean | apply the new page, invalidate |
| ST_IDLE | ST_FILL | read miss or read of a partial entry, buffer empty | — |
| ST_IDLE | ST_FILL | dirty entry with a half-written byte must be evicted | lazy fill of its own word |
| ST_FILL | ST_IDLE | wb_ack_i && buffer empty | DATA = memory word with dirty nibbles kept; FULL = 1 |
| ST_IDLE | ST_WRITEBACK | FLUSH && dirty && buffer empty | — |
| ST_WRITEBACK | ST_IDLE | wb_ack_i | DMASK = 0, invalidate, flush_ack |
| ST_IDLE | ST_IDLE | FLUSH && !dirty && buffer empty | invalidate, flush_ack (flush_noop) |

**Notes:**

- The posted write buffer (one word, shared by the four channels) drains to memory on its own, in any state. While it is busy, Wishbone carries its write; ST_FILL and ST_WRITEBACK wait for it.
- Order of priority in ST_IDLE: pending page change, then FLUSH, then the channel access.
- The cache is a 4-channel single-word buffer, not a classic cache. Consecutive words can be written without FLUSH: each eviction goes to the write buffer.
