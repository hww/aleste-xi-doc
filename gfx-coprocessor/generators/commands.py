name: FIFO command opcodes
dispatch:
  - {range: "0x00-0x1F", name: "SET16", description: "Запись 16 бит в R0-R31", length: 3, payload: "16-бит значение"}
  - {range: "0x20-0x3F", name: "SET8", description: "Запись 8 бит в R0-R31", length: 2, payload: "8-бит значение"}
commands:
  - {opcode: "0x40", name: "NOP", length: 1, payload: "—", description: "Пустая операция"}
  - {opcode: "0x41", name: "FILL", length: 1, payload: "—", description: "Заливка прямоугольника"}
  - {opcode: "0x42", name: "COPY", length: 1, payload: "—", description: "Копирование"}
  - {opcode: "0x43", name: "STENCIL", length: 1, payload: "—", description: "Трафарет"}
  - {opcode: "0x44", name: "LINE", length: 1, payload: "—", description: "Линия"}
  - {opcode: "0x45", name: "AFFINE", length: 1, payload: "—", description: "Аффинное преобразование"}
  - {opcode: "0x46", name: "PAL", length: 3, payload: "8-бит индекс + 16-бит цвет", description: "Палитра"}
  - {opcode: "0x47", name: "LOAD", length: "3 + n", payload: "16-бит n + n байт", description: "Загрузка в VRAM"}
  - {opcode: "0x48", name: "IRQ", length: 1, payload: "—", description: "Прерывание"}
  - {opcode: "0x49", name: "GET", length: 2, payload: "8-бит номер регистра", description: "Чтение регистра"}