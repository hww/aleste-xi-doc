# **XIFF v5.0 — ПОЛНАЯ СПЕЦИФИКАЦИЯ ИНТЕРФЕЙСНОГО ФРЕЙМВОРКА**

## **Документ: XIFF-SPEC-5.0**

**Статус:** Финальная спецификация для реализации  
**Дата:** 2026-01-11  
**Авторы:** Команда разработки Xi Aleste BIOS

---

## **ЧАСТЬ I: ВВЕДЕНИЕ И ФИЛОСОФИЯ**

### **1.1 Назначение XIFF**

**XIFF (XI Interface Framework)** — это инструмент для **автоматической генерации интерфейсов** между кодом на ассемблере Z80 и языком C в контексте операционной системы **Xi Aleste BIOS**.

**Проблема, которую решает XIFF:**
Разработчики драйверов пишут код на ассемблере для максимальной производительности, но:

- Приложения хотят использовать драйверы через C API
- Вручную поддерживать соответствие между ASM и C функциями — трудоёмко и чревато ошибками
- Спецификация BIOS требует строгих форматов (64-байтные VTable и т.д.)

**Решение XIFF:**
Программист добавляет **аннотации прямо в ASM код**, а XIFF:

1. **Генерирует** C заголовки (.h) и обёртки (.asm, .c)
2. **Проверяет** соответствие спецификации BIOS
3. **Обеспечивает** типобезопасность между ASM и C

### **1.2 Философия дизайна**

XIFF основан на трёх принципах:

#### **1. Минимализм (KISS)**

- Аннотации добавляются **прямо в существующий ASM код**
- **Нет отдельного языка описания интерфейсов** (IDL)
- **Нет сложной конфигурации** — достаточно указать пути выходных файлов

#### **2. Идиоматика C**

- Типы данных (`uint8_t`, `const char*`, `bool`) — стандартные из `stdint.h`
- Синтаксис (`arg`, `res`) — интуитивно понятен C программистам
- Соглашения об именовании следуют стандартам Aleste BIOS

#### **3. Прагматизм**

- **Не мешает VS Code и другим IDE** — генерирует чистый C код без inline asm
- **Идемпотентная генерация** — ручной код вне блоков XIFF сохраняется
- **Поэтапное внедрение** — можно аннотировать только часть функций

### **1.3 Архитектура в контексте Aleste BIOS**

```text
┌─────────────────────────────────────────────────────────┐
│           ПРИЛОЖЕНИЕ НА C                               │
│  #include "video.h"                                     │
│  video_draw_pixel(x, y, color);                         │
└──────────────┬──────────────────────────────────────────┘
               │ Вызов C функции
┌──────────────▼──────────────────────────────────────────┐
│           СГЕНЕРИРОВАННЫЙ C КОД (video.c)               │
│  void video_draw_pixel(uint8_t x, uint8_t y,            │
│                        uint16_t color) {                │
│    _video_draw_pixel_wrapper(x, y, color);              │
│  }                                                      │
└──────────────┬──────────────────────────────────────────┘
               │ Вызов ASM обёртки
┌──────────────▼──────────────────────────────────────────┐
│           СГЕНЕРИРОВАННАЯ ASM ОБЁРТКА                   │
│  _video_draw_pixel_wrapper:                             │
│    ld h, iyl        ; x из стека                       │
│    ld l, iyh        ; y из стека                       │
│    ld de, (sp+4)    ; color из стека                    │
│    jp __draw_pixel  ; Прыжок в реальную реализацию      │
└──────────────┬──────────────────────────────────────────┘
               │ Прямой вызов (17 циклов!)
┌──────────────▼──────────────────────────────────────────┐
│           РЕАЛЬНЫЙ ДРАЙВЕР НА ASM                       │
│  __draw_pixel:                                          │
│    ; ... высокооптимизированный код ...                │
│    ret                                                  │
└─────────────────────────────────────────────────────────┘
```

---

## **ЧАСТЬ II: СИНТАКСИС И ГРАММАТИКА АННОТАЦИЙ**

### **2.1 Базовый формат**

Все аннотации начинаются с `;; XIFF:` и должны находиться **непосредственно перед** аннотируемым элементом:

```asm
;; XIFF:const -- Ширина экрана в пикселях
SCREEN_WIDTH: defc 320

public __draw_pixel
;; XIFF:func __draw_pixel
;;   :arg uint8_t  @h x
;;   :arg uint8_t  @l y
;;   :arg uint16_t @de color
__draw_pixel:
    ; ... реализация ...
    ret
```

### **2.2 Типы аннотаций**

#### **2.2.1 Объявление модуля и файлов**

```asm
;; XIFF:export h "include/video.h"
;; XIFF:export inc "inc/video.inc"
;; XIFF:export wrap "src/video_wrap.asm"
;; XIFF:export c "src/video.c"
```

**Объяснение:**

- `export h` — генерирует C заголовок для `#include`
- `export inc` — генерирует ASM заголовок с `extern` объявлениями  
- `export wrap` — генерирует ASM обёртки для C calling convention
- `export c` — генерирует чистые C функции-посредники

#### **2.2.2 Константы**

```asm
;; XIFF:const -- Максимальное число спрайтов на экране
MAX_SPRITES: defc 128
```

XIFF ищет метку и `defc`/`equ` на той же или следующей строке.

#### **2.2.3 Перечисления**

```asm
;; XIFF:enum VideoMode :type uint8_t
;;   :desc "Режимы работы видео контроллера"
VIDEO_MODE_0: defc 0  ;; 256x192, 16 цветов
VIDEO_MODE_1: defc 1  ;; 320x200, 4 цвета
VIDEO_MODE_2: defc 2  ;; 640x200, монохромный
```

**Атрибуты:**

- `:type` — C тип для значений enum (по умолчанию `int`)
- `:desc` — описание для документации

#### **2.2.4 Структуры**

**Способ 1: Явное объявление структуры**

```asm
;; XIFF:struct Point
;;   :desc "Координаты точки на экране"
public _my_point
_my_point:
_x: dw 0  ;; XIFF:field int16_t -- Координата X
_y: dw 0  ;; XIFF:field int16_t -- Координата Y
```

**Способ 2: Определение экземпляра**

```asm
;; XIFF:define cursor Point
;;   :desc "Позиция курсора мыши"
_cursor:
cursor_x: dw 0  ;; XIFF:field int16_t -- X позиция
cursor_y: dw 0  ;; XIFF:field int16_t -- Y позиция
```

**Поддерживаемые типы полей:**

- Базовые: `uint8_t`, `int16_t`, `bool`
- Указатели: `const char*`, `void*`, `Point*`
- Массивы: `uint8_t[16]`, `Color[256]`
- Вложенные структуры: `Rect bounds`

#### **2.2.5 Функции и методы**

```asm
;; XIFF:func __detect_hardware
;;   :desc "Обнаружение графического чипа"
;;   :arg uint8_t @b chip_id -- ID чипа для проверки
;;   :res bool @c :invert    -- CF=0: найден, CF=1: не найден
;;   :wrapper fastcall       -- Авто-генерация fastcall обёртки
public __detect_hardware
__detect_hardware:
    ; Проверяем chip_id в регистре B
    ; Устанавливаем CF=0 если чип найден
    ret
```

**Полный список атрибутов функций:**

| Атрибут | Формат | Описание |
|---------|--------|----------|
| `:desc` | текст | Описание функции для документации |
| `:arg` | `тип @регистр имя` | Параметр функции |
| `:res` | `тип @регистр :атрибуты` | Возвращаемое значение |
| `:wrapper` | `тип` | Тип генерируемой обёртки (см. ниже) |

**Типы обёрток:**

- `fastcall` — стандартная fastcall конвенция (аргументы в регистрах)
- `naked` — минимальная обёртка (только `jp` в реализацию)
- `z88dk` — совместимость с z88dk C compiler
- `sdcc` — совместимость с SDCC compiler
- `null` — не генерировать обёртку (только декларация)

#### **2.2.6 VTable драйверов (специфика BIOS)**

```asm
;; XIFF:vtable VideoDriver :size 64
;;   :desc "Виртуальная таблица методов видео драйвера"
public __video_vtable
__video_vtable:
__video_detect: jp _detect_impl  ;; XIFF:method detect
__video_init:   jp _init_impl    ;; XIFF:method init
; ... остальные методы ...
__video_vtable_end:

;; XIFF:method detect
;;   :desc "Обнаружение видеоадаптера"
;;   :res bool @c :invert  ; CF=0: успех
_detect_impl:
    ; Реализация обнаружения
    ret
```

**Ключевые особенности:**

- `:size 64` — XIFF проверяет размер таблицы (требование BIOS)
- `__video_vtable_end` — метка для автоматического расчёта размера
- XIFF проверяет наличие 5 обязательных методов: `detect`, `init`, `deinit`, `get_info`, `command`

#### **2.2.7 События (команды) драйверов**

```asm
;; XIFF:event power_on
;;   :via __video_command    ; Через метод command()
;;   :command 0x01           ; Код команды POWER_ON
;;   :arg uint8_t @a mode    ; Режим питания
;;   :res bool @c :invert    ; Результат выполнения
_power_on_handler:
    ; Обработка команды POWER_ON
    ; A содержит код режима
    ret
```

Соответствует командам из **Раздела 5 спецификации BIOS**.

---

## **ЧАСТЬ III: СИСТЕМА ТИПОВ И ПРЕОБРАЗОВАНИЯ**

### **3.1 Поддерживаемые типы данных**

XIFF использует стандартные типы C99:

| Тип XIFF              | Тип C                           | Размер      | Допустимые регистры Z80 |
|-----------------------|---------------------------------|-------------|-------------------------|
| `void`                | `void`                          | 0           | -                       |
| `bool`                | `bool` (`#include <stdbool.h>`) | 8 бит       | Флаги (Z, C), регистр A |
| `uint8_t`, `int8_t`   | `uint8_t`, `int8_t`             | 8 бит       | A, B, C, D, E, H, L     |
| `uint16_t`, `int16_t` | `uint16_t`, `int16_t`           | 16 бит      | HL, DE, BC, IX, IY      |
| `uint32_t`, `int32_t` | `uint32_t`, `int32_t`           | 32 бит      | Пары регистров (DE:HL)  |
| `void*`, `T*`         | `void*`, `T*`                   | 16 бит      | HL, DE, BC, IX, IY      |
| `const T*`            | `const T*`                      | 16 бит      | HL                      |
| `T[N]`                | `T name[N]`                     | N*sizeof(T) | HL (адрес)              |

### **3.2 Соглашения о регистрах**

#### **3.2.1 Регистры для параметров**

```asm
;; XIFF:func example
;;   :arg uint8_t  @a first    ; 8-бит в A
;;   :arg uint16_t @hl second  ; 16-бит в HL
;;   :arg uint16_t @de third   ; 16-бит в DE
```

**Правила:**

1. 8-битные типы → 8-битные регистры (A, B, C, D, E, H, L)
2. 16-битные типы → 16-битные регистры (HL, DE, BC)
3. Указатели → HL (рекомендуется) или другие 16-битные регистры

#### **3.2.2 Регистры для возвращаемых значений**

```asm
;; XIFF:func example
;;   :res uint8_t  @a          ; 8-бит в A
;;   :res uint16_t @hl         ; 16-бит в HL
;;   :res bool @c :invert      ; Логический флаг в CF
```

### **3.3 Атрибуты преобразования**

Атрибуты указываются после типа возвращаемого значения:

```asm
:res тип @регистр :атрибут1 :атрибут2
```

#### **3.3.1 `:invert` — инверсия логики**

```asm
;; BIOS: CF=0 означает успех, но в C true = 1
;; XIFF:func detect
;;   :res bool @c :invert  ; CF=0 → true, CF=1 → false
_detect:
    ; ... обнаруживаем устройство
    or a        ; Устройство найдено, CF=0
    ret         ; XIFF преобразует в: return true;
```

#### **3.3.2 `:expand-sign` — расширение знака**

```asm
;; XIFF:func read_temperature
;;   :res int8_t @a :expand-sign  ; -20..100 → -20..100 (16 бит)
_read_temperature:
    ld a, -20   ; Температура -20°C
    ret         ; XIFF сгенерирует: int16_t, где -20 → 0xFFEC
```

#### **3.3.3 `:saturate` — насыщение при переполнении**

```asm
;; XIFF:func add_safe
;;   :arg uint8_t @a x
;;   :arg uint8_t @b y  
;;   :res uint8_t @a :saturate  ; 200+100 → 255, не 44
_add_safe:
    add a, b    ; 200 + 100 = 44 (с переносом)
    ret         ; XIFF сгенерирует насыщение до 255
```

#### **3.3.4 `:truncate` — усечение**

```asm
;; XIFF:func get_high_byte
;;   :res uint16_t @hl
;;   :res uint8_t @a :truncate  ; Берём только младший байт
_get_high_byte:
    ld hl, 0x1234
    ld a, h     ; = 0x12
    ret
```

### **3.4 Соглашения об именовании (префиксы)**

**Ключевое правило:** Префикс определяет, как XIFF обрабатывает функцию.

| Префикс | Пример | Обработка XIFF | Использование |
|---------|--------|----------------|---------------|
| `_` (один) | `_init` | **Только декларация** в C | Функция уже совместима с C |
| `__` (два) | `__detect` | **Генерация обёртки** | Чистая ASM функция |
| (нет) | `local_func` | Игнорируется | Внутренняя функция модуля |

**Примеры:**

```asm
;; 1. Уже совместима с C (например, скомпилирована z88dk)
public _c_compatible_func
;; XIFF:func _c_compatible_func
;;   :arg uint16_t @hl value
_c_compatible_func:
    ; ... код, совместимый с C calling convention ...
    ret

;; 2. Чистая ASM, нужна обёртка
public __pure_asm_func  
;; XIFF:func __pure_asm_func
;;   :arg uint8_t @a param
__pure_asm_func:
    ; ... чистый ASM, может портить любые регистры ...
    ret  ; XIFF сгенерирует обёртку
```

---

## **ЧАСТЬ IV: ГЕНЕРАЦИЯ ФАЙЛОВ И ФОРМАТЫ**

### **4.1 Процесс генерации**

```text
Исходный файл драйвера (driver.asm)
        │
        ▼ (Парсинг аннотаций XIFF)
        │
        ├───▶ inc/driver.inc      (extern объявления)
        ├───▶ include/driver.h    (C заголовок)  
        ├───▶ src/driver_wrap.asm (ASM обёртки)
        └───▶ src/driver.c        (C функции-прокси)
```

### **4.2 Формат генерируемых файлов**

#### **4.2.1 ASM заголовок (.inc)**

```asm
; Файл: inc/video.inc
; СГЕНЕРИРОВАНО XIFF. НЕ РЕДАКТИРОВАТЬ ВРУЧНУЮ.
; XIFF:start "drivers/video/video.asm"

extern SCREEN_WIDTH
extern SCREEN_HEIGHT  
extern __video_detect
extern __video_init

; XIFF:end
```

#### **4.2.2 C заголовок (.h)**

```c
/* Файл: include/video.h */
/* СГЕНЕРИРОВАНО XIFF. НЕ РЕДАКТИРОВАТЬ ВРУЧНУЮ. */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include <stdint.h>
#include <stdbool.h>

/* XIFF:start "drivers/video/video.asm" */

#define SCREEN_WIDTH 320
#define SCREEN_HEIGHT 200

typedef enum {
    VIDEO_MODE_0 = 0,
    VIDEO_MODE_1 = 1
} VideoMode;

bool video_detect(uint8_t chip_id);
bool video_init(VideoMode mode);

/* XIFF:end */

#endif /* _VIDEO_H_ */
```

#### **4.2.3 ASM обёртка (_wrap.asm)**

```asm
; Файл: src/video_wrap.asm
; СГЕНЕРИРОВАНО XIFF. НЕ РЕДАКТИРОВАТЬ ВРУЧНУЮ.
; XIFF:start "drivers/video/video.asm"

.module video_wrap
.include "video.inc"

; bool video_detect(uint8_t chip_id)
_video_detect_wrapper:
    pop hl          ; Сохраняем возвратный адрес
    pop bc          ; Берём chip_id из стека
    push hl         ; Восстанавливаем возвратный адрес
    ld b, c         ; chip_id в B для __video_detect
    call __video_detect
    ld a, 0         ; Предполагаем false
    jr c, .no_detect
    inc a           ; true = 1
.no_detect:
    ld l, a
    ret

; XIFF:end
```

#### **4.2.4 C файл-прокси (.c)**

```c
/* Файл: src/video.c */
/* СГЕНЕРИРОВАНО XIFF. НЕ РЕДАКТИРОВАТЬ ВРУЧНУЮ. */
/* XIFF:start "drivers/video/video.asm" */

#include "video.h"

extern bool _video_detect_wrapper(uint8_t chip_id);

bool video_detect(uint8_t chip_id) {
    return _video_detect_wrapper(chip_id);
}

/* XIFF:end */
```

### **4.3 Идемпотентная генерация (Smart Merge)**

**Проблема:** Программист редактирует `.h` файл, добавляя ручные определения, а XIFF перезаписывает файл.

**Решение Smart Merge:**

1. **XIFF читает целевой файл** (например, `video.h`)
2. **Ищет блоки** `/* XIFF:start "source.asm" */` ... `/* XIFF:end */`
3. **Если находит:**
   - Заменяет содержимое блока
   - Сохраняет всё вне блоков
4. **Если не находит:**
   - Добавляет новый блок в конец файла
5. **Всегда сохраняет:**
   - `#ifndef` защиту
   - `#include` директивы вне блоков
   - Комментарии вне блоков

**Пример работы:**

```c
/* video.h ДО генерации */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include "common.h"  <!-- Сохраняется

/* Ручная оптимизация для ARM */
#ifdef __ARM_ARCH
#define FAST_MODE 1
#endif

/* XIFF:start "drivers/video/video.asm" */
// СТАРЫЙ сгенерированный код
/* XIFF:end */

// Дополнительные ручные функции
void manual_helper(void);  <!-- Сохраняется

#endif
```

После генерации:

```c
/* video.h ПОСЛЕ генерации */
#ifndef _VIDEO_H_
#define _VIDEO_H_

#include "common.h"  <!-- Сохранено!

/* Ручная оптимизация для ARM */
#ifdef __ARM_ARCH
#define FAST_MODE 1
#endif

/* XIFF:start "drivers/video/video.asm" */
// НОВЫЙ сгенерированный код (обновлён)
#define SCREEN_WIDTH 320
bool video_detect(uint8_t chip_id);
/* XIFF:end */

// Дополнительные ручные функции
void manual_helper(void);  <!-- Сохранено!

#endif
```

---

## **ЧАСТЬ V: ИНТЕГРАЦИЯ СО СПЕЦИФИКАЦИЕЙ ALESTE BIOS**

### **5.1 Поддержка архитектуры драйверов BIOS**

XIFF обеспечивает соответствие **Разделу 2** спецификации BIOS:

#### **5.1.1 Singleton vs Polymorphic драйверы**

```asm
;; SINGLETON драйвер (например, системный таймер)
;; XIFF:vtable SystemTimer :size 64
;;   :singleton            ; Только одна реализация
__sys_timer_vtable:
    jp _timer_init
    ; ...

;; POLYMORPHIC драйвер (например, видео)
;; XIFF:vtable VideoDriver :size 64
;;   :polymorphic          ; Несколько реализаций
;;   :parent Graphics      ; Наследует методы Graphics
__video_vtable:
    jp _video_detect
    ; ...
```

#### **5.1.2 Обязательные методы (Раздел 2.2 спецификации)**

XIFF **автоматически проверяет** наличие 5 обязательных методов:

1. **detect()** — обнаружение устройства
2. **init()** — инициализация  
3. **deinit()** — деинициализация
4. **get_info()** — получение информации
5. **command()** — выполнение команд

**Пример объявления:**

```asm
;; XIFF:vtable StorageDriver :size 64
__storage_vtable:
__storage_detect:   jp _storage_detect
;; XIFF:method detect
;;   :desc "Обнаружение SD карты"
;;   :res bool @c :invert
_storage_detect:
    ; ... проверка наличия SD карты ...
    ret
```

### **5.2 Проверка VTable размера**

Спецификация BIOS требует **64-байтные VTable**. XIFF проверяет:

```asm
;; XIFF:vtable AudioDriver :size 64  <!-- Явное указание
public __audio_vtable
__audio_vtable:
    ; 21 слотов × 3 байта = 63 байта
    ; XIFF предупредит о несоответствии
__audio_vtable_end:

public __audio_vtable_size
__audio_vtable_size: defc __audio_vtable_end-__audio_vtable
```

**Правила:**

- Если `:size` указан — проверяется точное соответствие
- Если не указан — проверяется, что размер ≥ необходимого
- Предупреждение, если есть неиспользуемые байты

### **5.3 Поддержка MemoryContext (Раздел 4 спецификации)**

```asm
;; XIFF:struct MemoryContext
public _video_context
_video_context:
_hash:      db 0  ;; XIFF:field uint8_t  -- XOR хеш конфигурации
_slot_reg:  db 0  ;; XIFF:field uint8_t  -- Регистр слота
_window0:   db 0  ;; XIFF:field uint8_t  -- Банк окна 0
_window1:   db 0  ;; XIFF:field uint8_t  -- Банк окна 1
_window2:   db 0  ;; XIFF:field uint8_t  -- Банк окна 2  
_window3:   db 0  ;; XIFF:field uint8_t  -- Банк окна 3
_flags:     db 0  ;; XIFF:field uint8_t  -- Флаги контекста
_reserved:  db 0  ;; XIFF:field uint8_t  -- Выравнивание
```

XIFF генерирует соответствующий C struct:

```c
typedef struct {
    uint8_t hash;
    uint8_t slot_reg;
    uint8_t window0;
    uint8_t window1;
    uint8_t window2;
    uint8_t window3;
    uint8_t flags;
    uint8_t reserved;
} MemoryContext;

extern MemoryContext video_context;
```

### **5.4 Поддержка команд (Раздел 5 спецификации)**

```asm
;; XIFF:event set_video_mode
;;   :via __video_command      ; Вызывается через command()
;;   :command 0x40            ; Код команды SET_MODE
;;   :arg uint8_t @a mode     ; Видеорежим
;;   :res bool @c :invert     ; Результат
_set_video_mode:
    ; Обработка команды 0x40
    ; A содержит видеорежим
    ret
```

XIFF генерирует C функцию:

```c
bool video_set_mode(uint8_t mode);
```

И проверяет, что коды команд находятся в правильных диапазонах (0x40-0x5F для видео).

---

## **ЧАСТЬ VI: ИНТЕРФЕЙС КОМАНДНОЙ СТРОКИ**

### **6.1 Основные команды**

```
xiff <команда> [опции] <файлы>
```

#### **6.1.1 `parse` — Парсинг и проверка синтаксиса**

```
xiff parse драйвер.asm
xiff parse --verbose *.asm
xiff parse --output errors.txt drivers/
```

**Проверяет:**

- Корректность синтаксиса аннотаций
- Соответствие типов и регистров
- Наличие обязательных меток (`public`, `defc`)

#### **6.1.2 `generate` — Генерация файлов**

```
xiff generate драйвер.asm
xiff generate --force драйвер.asm    # Перезаписать без Smart Merge
xiff generate --inc-only драйвер.asm # Только .inc файлы
```

#### **6.1.3 `validate` — Проверка спецификации BIOS**

```
xiff validate драйвер.asm
xiff validate --strict драйвер.asm  # Ошибки вместо предупреждений
```

**Проверяет:**

- Размер VTable = 64 байта
- Наличие 5 обязательных методов
- Корректность MemoryContext структур
- Соответствие кодов команд диапазонам

#### **6.1.4 `diff` — Показать изменения**

```
xiff diff драйвер.asm          # Что изменится при генерации
xiff diff --color драйвер.asm  # Цветной вывод
```

### **6.2 Уровни логирования**

```bash
xiff generate file.asm           # Уровень 1: Нормальный (только ошибки)
xiff generate file.asm -v        # Уровень 2: Подробный (+ предупреждения)
xiff generate file.asm -vv       # Уровень 3: Отладка (+ детали парсинга)
xiff generate file.asm -vvv      # Уровень 4: След выполнения (для разработки)
```

**Формат сообщений:**

```
[уровень][компонент] сообщение
[info][parser] Обработка video.asm
[warn][vtable] VTable video_driver: 63 байта, ожидается 64
[error][type] Несовместимый тип: uint16_t в 8-битном регистре A
```

### **6.3 Конфигурационный файл**

XIFF ищет `.xiffrc` в текущем каталоге или домашней директории:

```json
{
  "version": "5.0",
  "output": {
    "inc_dir": "inc",
    "h_dir": "include",
    "wrap_dir": "src",
    "c_dir": "src",
    "backup": true
  },
  "validation": {
    "check_vtable_size": true,
    "check_mandatory_methods": true,
    "warnings_as_errors": false
  },
  "code_style": {
    "c_prefix": "",
    "asm_prefix": "__",
    "indent": "  ",
    "comment_style": "c"  // "c" или "asm"
  },
  "compiler": {
    "default_wrapper": "fastcall",
    "c_standard": "c99",
    "stdint_header": "<stdint.h>"
  }
}
```

---

## **ЧАСТЬ VII: ПРАКТИЧЕСКИЕ ПРИМЕРЫ**

### **7.1 Полный пример драйвера звука**

```asm
;; ============================================
;; sound.asm - Драйвер звука AY-3-8910
;; ============================================

;; XIFF:export h "include/sound.h"
;; XIFF:export inc "inc/sound.inc"
;; XIFF:export wrap "src/sound_wrap.asm"

;; Константы
;; XIFF:const -- Частота дискретизации
SAMPLE_RATE: defc 44100

;; XIFF:enum Note :type uint8_t
;;   :desc "Ноты MIDI (0-127)"
NOTE_C4:  defc 60
NOTE_D4:  defc 62
NOTE_E4:  defc 64

;; Структура состояния
;; XIFF:struct AYState
public _ay_state
_ay_state:
_registers: ds 16  ;; XIFF:field uint8_t[16] -- Тень регистров
_volume:    db 15  ;; XIFF:field uint8_t     -- Громкость 0-15
_muted:     db 0   ;; XIFF:field bool        -- Флаг отключения звука

;; VTable драйвера
;; XIFF:vtable SoundDriver :size 64
;;   :polymorphic  ; Поддержка разных чипов
public __sound_vtable
__sound_vtable:
__sound_detect:   jp _sound_detect
__sound_init:     jp _sound_init
__sound_deinit:   jp _sound_deinit
__sound_get_info: jp _sound_get_info
__sound_command:  jp _sound_command
__sound_play:     jp _sound_play_note
; ... остальные 16 методов ...
__sound_vtable_end:

;; Метод обнаружения
;; XIFF:method detect
;;   :desc "Обнаружение AY-3-8910"
;;   :res bool @c :invert
public __sound_detect
_sound_detect:
    ; ... код обнаружения ...
    or a        ; CF=0 если найден
    ret

;; Метод воспроизведения ноты
;; XIFF:method play_note
;;   :desc "Воспроизвести ноту на канале"
;;   :arg uint8_t @a note     ; Нота MIDI (0-127)
;;   :arg uint8_t @b channel  ; Канал (0-2)
;;   :res bool @c :invert     ; Успех операции
public __sound_play_note
_sound_play_note:
    ; ... код воспроизведения ...
    or a        ; CF=0 если успешно
    ret

;; Команда управления питанием
;; XIFF:event power_control
;;   :via __sound_command
;;   :command 0x01            ; POWER_ON/POWER_OFF
;;   :arg uint8_t @a state    ; 1=вкл, 0=выкл
;;   :res bool @c :invert
_power_control:
    ; ... обработка питания ...
    or a
    ret
```

### **7.2 Генерация и использование**

```bash
# Генерация интерфейсов
xiff generate sound.asm

# Проверка соответствия BIOS
xiff validate sound.asm

# Использование в C программе
```

**C программа:**

```c
#include "sound.h"

int main() {
    // Обнаружение звукового чипа
    if (!sound_detect()) {
        printf("Звуковой чип не найден\n");
        return 1;
    }
    
    // Инициализация
    if (!sound_init()) {
        printf("Ошибка инициализации звука\n");
        return 1;
    }
    
    // Воспроизведение ноты
    sound_play_note(NOTE_C4, 0);  // Нота C4 на канале 0
    
    // Управление питанием
    sound_power_control(0);  // Выключить питание
    
    return 0;
}
```

---

## **ЧАСТЬ VIII: ТРЕБОВАНИЯ И ОГРАНИЧЕНИЯ**

### **8.1 Требования к системе**

- **Python 3.8+** или **C++17 компилятор** (для нативной версии)
- **Ассемблер:** sjasmplus (основной), z80asm (альтернативный)
- **Кодировка файлов:** UTF-8 (рекомендуется) или CP866
- **Операционная система:** Любая (Windows, Linux, macOS)

### **8.2 Ограничения MVP**

**Первая версия (MVP) поддерживает:**

1. Базовые типы данных (`uint8_t`, `uint16_t`, `bool`, указатели)
2. Функции с до 3 параметрами
3. Проверку VTable размера
4. Генерацию `.inc`, `.h`, `_wrap.asm` файлов
5. Smart Merge для идемпотентной генерации

**Будущие версии добавят:**

1. Поддержка `float` и `double` типов
2. Callback функции (указатели на функции)
3. Генерация документации (Doxygen, Markdown)
4. Плагины для VS Code и других IDE
5. Поддержка других ассемблеров (NASM, AS)

### **8.3 Обработка ошибок**

XIFF различает три уровня проблем:

| Уровень | Пример | Действие |
|---------|--------|----------|
| **Ошибка** | Неизвестная директива, несовместимые типы | Прервать генерацию |
| **Предупреждение** | VTable 63 байта вместо 64, неиспользуемые методы | Продолжить, сообщить |
| **Информация** | Сгенерировано X файлов, использовано Y аннотаций | Только в verbose режиме |

---

## **ЧАСТЬ IX: ПЛАН РАЗРАБОТКИ**

### **Фаза 1: Базовый парсер**

- [ ] Парсинг аннотаций `;; XIFF:`
- [ ] Поддержка `export`, `const`, `enum`
- [ ] Генерация `.inc` файлов
- [ ] Команда `parse`

### **Фаза 2: Генерация C интерфейсов**

- [ ] Поддержка `func`, `arg`, `res`
- [ ] Генерация `.h` и `_wrap.asm`
- [ ] Атрибуты преобразования (`:invert`, `:expand-sign`)
- [ ] Команды `generate`, `diff`

### **Фаза 3: Поддержка BIOS спецификации**

- [ ] Структуры и `struct`
- [ ] VTable и `vtable`, `method`
- [ ] Проверка 64-байтного размера
- [ ] Обязательные методы драйверов
- [ ] Команда `validate`

### **Фаза 4: Расширенные возможности**

- [ ] Smart Merge (идемпотентная генерация)
- [ ] Конфигурационный файл `.xiffrc`
- [ ] События (`event`) и команды
- [ ] MemoryContext структуры

### **Фаза 5: Тестирование и документация**

- [ ] Тесты на реальных драйверах Aleste BIOS
- [ ] Документация с примерами
- [ ] Интеграция в процесс сборки
- [ ] Релиз v1.0.0

---

## **ЧАСТЬ X: ЗАКЛЮЧЕНИЕ И СТАТУС**

### **10.1 Текущий статус**

✅ **Спецификация завершена** — все аспекты проработаны  
✅ **Синтаксис определён** — аннотации, типы, атрибуты  
✅ **Архитектура ясна** — парсер → генератор → валидатор  
✅ **Интеграция определена** — с BIOS, C компиляторами, CI/CD  

### **10.2 Ключевые инновации**

1. **Идиоматика C в ASM аннотациях** — естественно для разработчиков
2. **Smart Merge** — защищает ручной код при генерации
3. **Автоматическая проверка спецификации BIOS** — гарантия совместимости
4. **Прагматичный дизайн** — решает реальные проблемы без излишеств

### **10.3 Следующие шаги**

1. **Утвердить спецификацию** как стандарт для команды
2. **Создать репозиторий** на GitHub с этой документацией
3. **Начать реализацию** парсера на Python 3.10+
4. **Протестировать** на драйвере звука из Appendix A оригинальной спецификации

---

## **ПРИЛОЖЕНИЕ A: СРАВНЕНИЕ С АНАЛОГАМИ**

| Характеристика | **XIFF** | SWIG | CTypes | Ручная разработка |
|----------------|----------|------|--------|-------------------|
| **Целевая платформа** | Z80 + Aleste BIOS | Мультиплатформенный | Python + C | Любая |
| **Синтаксис** | Аннотации в ASM | Отдельный IDL файл | Описания в Python | Код на C и ASM |
| **Проверка BIOS** | **Да, автоматическая** | Нет | Нет | Вручную |
| **Генерация обёрток** | **Автоматическая** | Да | Runtime | Вручную |
| **Сложность внедрения** | Низкая | Средняя | Низкая | Высокая |
| **Производительность** | **Максимальная** (оптимизировано под Z80) | Средняя | Низкая | Зависит от разработчика |

---

## Маленькие нюансы, которые стоит держать в уме (для реализации)

- Директива :via в событиях: В примере set_video_mode используется:via __video_command. Стоит убедиться, что генератор будетпроверять, существует ли эта функция__video_command в текущеммодуле, иначе линкер выдаст ошибку.
- Тип bool в Z80: Поскольку в C stdbool.h обычно определяет trueкак 1, а в ASM мы часто используем флаги, ваша идея с атрибутом:invert остается ключевой. Нужно будет жестко зафиксировать вкоде генератора, что :invert для флага Carry (@c) означает: CF=0-> return true.
- Регистровые пары для 32-бит: В таблице 3.1 упомянуты uint32_t ипара DE:HL. Это очень полезно для работы с LBA секторами наSD-карте. Стоит предусмотреть в парсере, что @dehl — это одинсоставной регистр.

**XIFF v5.0 готов к реализации.** Эта спецификация предоставляет полное, самодостаточное руководство для создания инструмента, который значительно упростит разработку драйверов для Xi Aleste BIOS, сохраняя при этом все преимущества ручной оптимизации ассемблерного кода.
