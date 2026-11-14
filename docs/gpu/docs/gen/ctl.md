# Controller FSM

![Controller FSM](gen/ctl.svg)

| State | Output | Description |
| --- | --- | --- |
| <a id="IDLE"></a>**IDLE** (initial) | busy=0 | — |
| <a id="FETCH"></a>**FETCH** | busy=1 | — |
| <a id="EXEC"></a>**EXEC** | busy=1 | — |
| <a id="DONE"></a>**DONE** | — | — |

| From | To | Condition | Action |
| --- | --- | --- | --- |
| IDLE | FETCH | start | load |
| FETCH | EXEC | — | — |
| EXEC | EXEC | !last | — |
| EXEC | FETCH | more | — |
| FETCH | IDLE | abort | — |
| EXEC | DONE | last | — |
| DONE | IDLE | — | — |
