**SysDMA arbitration rules**

| Rule | Name | Description |
| --- | --- | --- |
| 1 | <a id="Key"></a>**Key** | Each requesting channel presents the key {MASK[2:0], ~CH[2:0]}; the larger key wins |
| 2 | <a id="Elimination"></a>**Elimination** | Equivalent to NuBus bitwise elimination: the key is compared from the MSB down and losers drop out; implemented as a 8-to-1 maximum tree |
| 3 | <a id="Granularity"></a>**Granularity** | One grant moves up to BURST_BYTES bytes, then the arbiter runs again |
| 4 | <a id="Default"></a>**Default** | All MASK = 0: the lower channel number wins, so CPU channels outrank SPI channels |
| 5 | <a id="Override"></a>**Override** | A driver can raise MASK of an SPI channel while it talks to a latency-sensitive module |

**Notes:**

- Masks are not merged with a bitwise OR: OR would produce a value no channel owns. The arbiter selects the winning key.
- Arbitration against the audio engine and the GPU on the shared memory path is outside this table (see open items).
