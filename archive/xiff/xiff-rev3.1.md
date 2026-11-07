Отлично! Полная спецификация готова. Собираю все вместе:

---

# XIFF - ИНСТРУМЕНТ ГЕНЕРАЦИИ КОДА ДЛЯ XI ALESTE BIOS

## Статус: **Спецификация v3.1 - ГОТОВО К РЕАЛИЗАЦИИ**

## ОСНОВНЫЕ ПРИНЦИПЫ

1. **Директивы в ASM коде** - аннотации прямо в исходниках
2. **Генерация 4 файлов** - .inc, .h, _wrap.asm, .c (чистые декларации)
3. **Блоки start/end** - для идемпотентной генерации
4. **KISS** - минимальный синтаксис, решаем реальные проблемы

---

## СИНТАКСИС ДИРЕКТИВ

```asm
;; XIFF:директива параметры
```

**ПРИМЕРЫ:**

```asm
;; XIFF:import "other.asm"
;; XIFF:export inc "inc/sound.inc"
;; XIFF:desc "Описание смысла"
```

---

## ДИРЕКТИВЫ

### **Экспорт файлов**

```asm
;; XIFF:export inc "inc/sound.inc"      ; ASM заголовок
;; XIFF:export h "include/sound.h"      ; C заголовок
;; XIFF:export wrap "src/sound_wrap.asm" ; ASM обёртки
;; XIFF:export c "src/sound.c"          ; C файл (только декларации)
```

### **Импорт**

```asm
;; XIFF:import "other.asm"    ; обработать другой файл
;; XIFF:import c "other.h"    ; добавить #include в C заголовок
```

### **Константы**

```asm
SCREEN_WIDTH: defc 320  ;; XIFF:const "Ширина экрана в пикселях"
```

### **Перечисления**

```asm
;; XIFF:enum Имя
;;   :type тип_си
;;   :prefix префикс_
COLOR_RED:   defc 1
COLOR_GREEN: defc 2
COLOR_BLUE:  defc 3
```

### **Структуры**

```asm
;; XIFF:struct Имя
;;   :prefix префикс_
;;   :instance имя_экземпляра1
;;   :instance имя_экземпляра2
_точка:
точка_x: dw 0  ;; XIFF:field тип "описание"
точка_y: dw 0  ;; XIFF:field тип "описание"
```

Или через define:

```asm
;; XIFF:define имя_экземпляра1 ИмяСтруктуры
_точка:
точка_x: dw 0  ;; XIFF:field тип "описание"
точка_y: dw 0  ;; XIFF:field тип "описание"
```

### **Функции**

```asm
;; XIFF:func имя
;;   :desc "описание"
;;   :param имя тип @регистр "описание"
;;   :result тип @регистр
;;   :wrapper имя_враппера  ; нестандартный враппер
;;   :wrapper null          ; без враппера
public __функция
__функция:
    ; реализация
    ret
```

### **VTable и методы драйвера**

```asm
;; XIFF:vtable имя (родитель)
public __vtable
__vtable:
__метод1: jp _реализация1
__метод2: jp _реализация2
__vtable_end:
public __vtable_size
__vtable_size: defc __vtable_end-__vtable

;; XIFF:method __метод1 (vtable)
;;   :desc "описание"
;;   :result тип @регистр :атрибуты
_реализация1:
    ret
```

### **События (команды)**

```asm
;; XIFF:event имя_события
;;   :via __команда_драйвера
;;   :command значение_команды
;;   :param имя тип @регистр "описание"
;;   :result тип @регистр
_обработчик_команды:
    ret
```

---

## АТРИБУТЫ ПРЕОБРАЗОВАНИЯ ТИПОВ

```asm
;; :invert      - инвертировать bool (ZF=1 → false, ZF=0 → true)
;; :expand-sign - расширить знак (int8 → int16)
;; :saturate    - насыщение при переполнении
;; :truncate    - усечение
;; :error       - ошибка при переполнении (по умолчанию)
```

**Пример:**

```asm
;; XIFF:method __детект (vtable)
;;   :desc "Проверка устройства"
;;   :result bool @c :invert  ; CF=0 → true, CF=1 → false
_детект:
    or a        ; CF=0 → устройство найдено
    ret
```

---

## ГЕНЕРИРУЕМЫЕ ФАЙЛЫ (с блоками)

Все генерируемые файлы содержат блоки:

```asm
; XIFF:start "src/sound.asm"
; сгенерированный код
; XIFF:end
```

### **inc/sound.inc:**

```asm
; XIFF:start "src/sound.asm"
extern SAMPLE_RATE
extern AY_REG_TONE_A_LO
extern _ay_state
extern __audio_detect
; XIFF:end
```

### **include/sound.h:**

```c
// XIFF:start "src/sound.asm"
#define SAMPLE_RATE 44100
typedef enum { AY_REG_TONE_A_LO = 0x00 } AYRegister;
typedef struct { uint8_t reg_shadow[16]; } AYState;
extern AYState ay_state;
bool audio_detect(void);
void audio_play_note(uint8_t note, uint8_t channel);
// XIFF:end
```

### **src/sound_wrap.asm:**

```asm
; XIFF:start "src/sound.asm"
.module sound_wrap
.include "sound.inc"
_audio_play_note_wrapper:
    ; C → Z80 преобразование
    jp __audio_command
; XIFF:end
```

### **src/sound.c:**

```c
// XIFF:start "src/sound.asm"
#include "sound.h"
extern void _audio_play_note_wrapper(uint8_t note, uint8_t channel);
void audio_play_note(uint8_t note, uint8_t channel) {
    _audio_play_note_wrapper(note, channel);
}
// XIFF:end
```

---

## ШАБЛОНЫ ФАЙЛОВ

Для каждого типа файла есть шаблон с подстановками `{{...}}`:

### **Шаблон .h файла:**

```c
#ifndef _{{MODULE_NAME}}_H_
#define _{{MODULE_NAME}}_H_

// XIFF:start {{FILE_PATH}}
// XIFF:end

#endif
```

**Подстановки:**

- `{{MODULE_NAME}}` - имя модуля (uppercase)
- `{{FILE_PATH}}` - путь к исходному ASM файлу

---

## КОМАНДЫ XIFF

```bash
# Парсинг и проверка
xiff parse драйвер.asm

# Генерация файлов
xiff generate драйвер.asm

# Проверка (валидация)
xiff validate драйвер.asm

# Показать различия
xiff diff драйвер.asm

# Создать шаблон драйвера
xiff new --name звук --type driver
```

---

## ПРАВИЛА ВАЛИДАЦИИ

1. **VTable = 64 байта** (проверяется через __vtable_size)
2. **5 обязательных методов**: detect, init, deinit, get_info, command
3. **Все методы реализованы** - jp ведёт на существующую метку
4. **Типы совместимы с регистрами** (uint16_t → HL, не A)
5. **Нет конфликтов имён** между ASM и C

---

## ПОВЕДЕНИЕ И КОНФИГУРАЦИЯ

### **Обработка импортов:**

- **Depth-first** обход зависимостей
- Обнаружение циклических зависимостей с ошибкой

### **Кеширование:**

- **Нет кеширования** - всегда парсим заново
- Можно использовать Makefile для инкрементальной сборки

### **Инкрементальная генерация:**

- **Нет** - всегда полная генерация
- Но можно обновлять только изменённые **файлы** (через Makefile)

### **Логирование (3 уровня):**

```bash
xiff generate file.asm           # Уровень 1: нормальный
xiff generate file.asm -v        # Уровень 2: подробный (элементы)
xiff generate file.asm -vv       # Уровень 3: отладка (всё подряд)
```

**Формат сообщений:**

```text
[info|warn|error][file|module|class] Message .... details
```

**Примеры:**

```text
[info][file] Processing sound.asm
[warn][module] VTable size is 60 bytes, should be 64
[error][class] Method 'detect' not implemented
```

### **Конфигурация:**

- **Параметры командной строки** - для интеграции в процесс сборки
- **Файл config.h/config.py** - для детальных настроек инструмента

---

## ПРЕИМУЩЕСТВА

1. **Нет отдельного .xiff файла** - всё в ASM коде
2. **VS Code не ругается** - нет inline asm в C файлах
3. **Идемпотентность** - блоки start/end защищают ручной код
4. **Простая интеграция** с Makefile/CMake
5. **Совместимость** с существующим кодом
6. **Валидация** против спецификации BIOS
7. **Минимализм** - решает только проблему интерфейсов

---

## ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### **Вход:**

- ASM файлы с директивами `;; XIFF:`
- Поддерживаемые ассемблеры: sjasmplus, z80asm
- Кодировка: UTF-8 или CP866

### **Выход:**

- `.inc` - extern объявления для ASM
- `.h` - C заголовки с типами и прототипами
- `_wrap.asm` - ASM обёртки для C calling convention
- `.c` - чистые C файлы (только декларации)

### **Обработка ошибок:**

- Все ошибки с указанием строки и файла
- Продолжение после некритических предупреждений
- Выход с кодом ошибки для скриптов сборки

---

## ГОТОВОСТЬ

✅ **Спецификация завершена** - все вопросы проработаны
✅ **Синтаксис определён** - директивы, атрибуты, форматы
✅ **Архитектура ясна** - парсер → генератор → валидатор
✅ **Интеграция определена** - команды, логирование, конфигурация

**Следующий шаг:** Реализация прототипа на выбранном языке (C++ ≥17 или Python).

---

**XIFF готов к разработке.** Спецификация покрывает все аспекты инструмента генерации интерфейсов для драйверов Aleste BIOS.
