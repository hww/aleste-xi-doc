### Диспетчеризация

| Диапазон | Имя | Длина (байт) | Payload | Описание |
| --- | --- | --- | --- | --- |
| 0x00-0x1F | **SET16** | — | — | Write FIFO16S into R0-R31 |
| 0x20-0x3F | **SET8** | — | — | Write FIFO8 into R0-R31 |

### Команды

| Опкод | Имя | Длина (байт) | Payload | Описание |
| --- | --- | --- | --- | --- |
| 0x40 | **NOP** | — | — | No operation |
| 0x41 | **FILL** | — | — | Fill rectangle |
| 0x42 | **COPY** | — | — | Copy pixels |
| 0x43 | **STENCIL** | — | — | Stencil operation |
| 0x44 | **LINE** | — | — | Draw line |
| 0x45 | **AFFINE** | — | — | Affine transform |
| 0x46 | **PAL** | — | — | Write palette entry |
| 0x47 | **LOAD** | — | — | Load bytes into video memory |
| 0x48 | **IRQ** | — | — | Request interrupt after prior work |
| 0x49 | **GET** | — | — | Copy register to host-readable latch |
