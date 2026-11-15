**Cache FSM**

| State | Output | Description |
| --- | --- | --- |
| <a id="C_IDLE"></a>**C_IDLE** (initial) | — | Waiting for access / prefetch / flush |
| <a id="C_FILL_REQ"></a>**C_FILL_REQ** | — | Read miss: wb_cyc=1 until wb_ack_i |
| <a id="C_WB_REQ"></a>**C_WB_REQ** | — | Writeback of dirty channel: wb_cyc=1 until wb_ack_i |

| From | To | Condition | Action |
| --- | --- | --- | --- |
| C_IDLE | C_FILL_REQ | access && !hit \|\| prefetch_req && !hit | — |
| C_FILL_REQ | C_IDLE | wb_ack_i | — |
| C_IDLE | C_WB_REQ | flush_req && valid && dirty | — |
| C_WB_REQ | C_IDLE | wb_ack_i | — |
| C_IDLE | C_IDLE | flush_req && !(valid && dirty) | valid=0, dirty=0, flush_done=1 |

**Notes:**

- C_IDLE -> C_IDLE is flush_noop: flush requested but channel invalid or clean, no WB needed.
- gc is a 4-channel single-word buffer, not a classic cache. Writing N consecutive words requires FLUSH after each word.
