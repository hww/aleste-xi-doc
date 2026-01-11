# XIFF - Инструмент генерации кода для Xi Aleste BIOS

## Статус: Черновик v2

* **НАЗНАЧЕНИЕ**

XIFF (XI Interface Framework) — утилита генерации интерфейсного кода, которая связывает декларативные описания драйверов с конкретными файлами ASM, C и заголовков. Инструмент следует философии **KISS (Keep It Simple, Stupid)** и специализируется только на генерации интерфейсов, оставляя бизнес-логику разработчику.

* **ПРИНЦИПЫ РАЗРАБОТКИ**

1. **Одна задача, одно решение**: Генерация интерфейсов, а не логики
2. **Идемпотентность**: Повторный запуск не ломает пользовательский код
3. **Защищённые зоны**: Пользовательский код помечается тегами и никогда не перезаписывается
4. **Прагматизм**: Использование LISP для простого парсинга и максимальной гибкости

* **ТЕХНИЧЕСКИЕ ХАРАКТЕРИСТИКИ**

- **Язык реализации**: SBCL (Common Lisp)
- **Формат входных данных**: S-выражения LISP
- **Объём проекта**: Один исполняемый файл SBCL
- **Зависимости**: Только стандартная библиотека Common Lisp

---

## ОСНОВНЫЕ КОНЦЕПЦИИ

### **Блоки с тегами (Tagged Blocks)**

XIFF работает с файлами через помеченные блоки. Каждое определение имеет ассоциированный тег, который определяет его положение в файле.

```asm
;; Файл sound.asm
;; <xiff vtable> - НАЧАЛО БЛОКА VTABLE
__sound_vtable:
    jp _sound_init
    jp _sound_command
;; </xiff> - КОНЕЦ БЛОКА
```

**Правила работы с тегами:**

1. Если тег существует → XIFF обновляет содержимое между маркерами
2. Если тега нет → XIFF создаёт блок в соответствии с порядком приоритета
3. Порядок тегов определяется декларацией `define-tag`

```lisp
;; Порядок тегов в файле
(define-tag includes   :order 100)   ;; В начале файла
(define-tag constants  :order 200)
(define-tag vtable     :order 300)
(define-tag code       :order 400)   ;; Основной код
(define-tag data       :order 500)   ;; Данные
(define-tag footer     :order 999)   ;; В конце файла
```

### **Два типа файлов**

XIFF генерирует две группы файлов:

| Группа | Назначение | Файлы |
|--------|------------|-------|
| **ASM** | Драйверы и константы для ассемблера | `.asm` (код), `.inc` (объявления) |
| **C**   | Интерфейсы для программ на C | `.h` (заголовки), `.c` (реализации), `_wrap.asm` (обёртки) |

---

## СИНТАКСИС ОПИСАНИЯ ДРАЙВЕРОВ

### **Модуль (Module)**

Модуль — это контейнер для определений, связанный с конкретными выходными файлами.

```lisp
(module sound
  ;; Определение выходных файлов
  (define-file c-header "include/sound.h")
  (define-file c-code   "src/sound.c")
  (define-file c-asm    "src/sound_wrap.asm")
  (define-file inc      "inc/sound.inc")
  (define-file asm      "drivers/sound/sound.asm")
  
  ;; Определения внутри модуля
  (defconst MAX_VOLUME 255)
  (defconst SAMPLE_RATE 44100)
  
  ;; Тип драйвера
  (deftype sound (driver)
    ((volume uint8_t 255)
     (pan    uint8_t 128))
    (:methods
      (set_volume ((vol uint8_t a)) void)
      (get_volume () (uint8_t a)))))
```

### **Определение типов (Deftype)**

Создаёт новый тип драйвера или расширяет существующий.

```lisp
;; Базовый синтаксис
(deftype имя (родитель-или-driver)
  ((поле1 тип1 значение-по-умолчанию)
   (поле2 тип2 значение-по-умолчанию))
  (:methods
    (метод1 ((аргумент тип регистр)) возвращаемый-тип :атрибуты)
    (метод2 ((арг1 тип1 рег1) (арг2 тип2 рег2)) тип-возврата)))
```

**Поддерживаемые атрибуты методов:**

- `:abstract` — метод должен быть реализован в наследниках (по умолчанию все методы abstract)  
- `:virtual` — метод имеет реализацию по умолчанию
- `:override` — переопределяет метод родителя с указанием новой реализации
- `:import` — метод уже определён в ASM коде
- `:command` — метод вызывается через диспетчер команд

### **Аргументы и возвращаемые значения**

Каждый аргумент и возвращаемое значение описываются с указанием типа и регистра/флага.

```lisp
;; Формат аргумента
(имя тип регистр :атрибуты)

;; Формат возвращаемого значения
(тип регистр/флаг)
```

**Поддерживаемые регистры:**

- 8-бит: `a`, `b`, `c`, `d`, `e`, `h`, `l`
- 16-бит: `af`, `bc`, `de`, `hl`, `sp`
- Парные: `bc`, `de`, `hl`
- Специальные: `ix`, `iy`, `i`, `r`

**Поддерживаемые флаги:**

- `z` — zero flag
- `c` — carry flag
- `n` — negative flag
- `p` — parity flag

**Атрибуты преобразования типов:**

```lisp
;; Расширение знака
(arg int8_t a :expand-sign)

;; Ограничение с насыщением
(result uint16_t hl :saturate)

;; Простое усечение
(result uint8_t a :truncate)

;; Ошибка при переполнении (по умолчанию)
(result uint8_t a :error)

;; Добавление описания
(arg speed uint16_t hl :info "Fixed point 8.8 format")
```

Для лучшей читаемости можно добавлять регистрам символ @

```lisp
;; Расширение знака
(arg int8_t @a :expand-sign)

;; Ограничение с насыщением
(result uint16_t @hl :saturate)
```


### **Константы и перечисления**

```lisp
;; Простая константа
(defconst MAX_BUFFER 1024)

;; Константа с импортом из ASM
(defconst PORT_ADDRESS 0xFD :import)

;; Перечисление
(defenum Command (uint8_t)
  (PLAY  0x01)
  (STOP  0x02)
  (PAUSE 0x03))

;; Перечисление с импортом
(defenum Mode (uint8_t) :import
  (SLOW  1)
  (FAST  2))
```

### **Переменные**

```lisp
;; Объявление переменной
(defvar current_volume uint16_t)

;; С импортом из ASM
(defvar buffer_ptr void* :import)
```

---

## СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ

### **1. Импорт существующих ASM определений**

Когда код уже написан на ASM, XIFF только декларирует его:

```asm
;; Существующий ASM код
_ay_init:        ; Уже реализовано
    ld a, 0xFF
    out (0xFD), a
    ret

_ay_volume:      ; Переменная
    defb 128
```

```lisp
;; Описание для XIFF
(module ay8910
  (defunc ay_init () void :import)
  (defvar ay_volume uint8_t :import))
```

### **2. Экспорт новых определений**

Когда код нужно сгенерировать:

```lisp
(module video
  (defconst SCREEN_WIDTH 320)
  (defconst SCREEN_HEIGHT 200)
  
  (deftype video (driver)
    ((mode uint8_t 0))
    (:methods
      (clear_screen ((color uint8_t a)) void)
      (draw_pixel ((x uint8_t h) (y uint8_t l) (color uint8_t a)) void))))
```

### **3. Наследование и переопределение**

```lisp
;; Базовый драйвер звука
(deftype sound (driver)
  ((volume uint8_t 100))
  (:methods
    (set_volume ((vol uint8_t a)) void :abstract)
    (get_volume () (uint8_t a) :virtual)))

;; Конкретная реализация AY-3-8910
(deftype ay8910 (sound)
  ((chip_port uint8_t 0xFD))  ; Добавляем новое поле
  (:methods
    (set_volume ((vol uint8_t a)) void :override ay8910_set_volume)
    (enable_channel ((ch uint8_t a) (on bool z)) void)))
```

### **4. Система событий (Commands)**

Для реализации паттерна Command из спецификации Aleste:

```lisp
(deftype video (driver)
  ()
  (:methods
    (command ((cmd uint8_t a) (param uint16_t hl)) void)
  (:events
    (clear_screen 0x01 ((color uint8_t a)) void :call command)
    (scroll_up    0x02 ((lines uint8_t a)) void :call command)
    (set_palette  0x03 ((index uint8_t h) (color uint16_t l)) void :call 0x03)))
```

**Результат генерации:**

```c
// C заголовок
#define VIDEO_CMD_CLEAR_SCREEN 0x01
#define VIDEO_CMD_SCROLL_UP    0x02
#define VIDEO_CMD_SET_PALETTE  0x03

void video_clear_screen(uint8_t color) __z88dk_fastcall;
void video_scroll_up(uint8_t lines) __z88dk_fastcall;
void video_set_palette(uint8_t index, uint16_t color) __z88dk_callee;
```

```asm
; ASM диспетчер
__video_command:
    cp 0x01
    jp z, _video_clear_screen
    cp 0x02
    jp z, _video_scroll_up
    cp 0x03
    jp z, _video_set_palette
    ret
```

---

## ГЕНЕРАЦИЯ КОДА

### **Для ASM файлов**

```asm
;; Генерируемый префикс
.module драйвер
.include "инклуды"

;; <xiff constants>
;; Константы, перечисления
;; </xiff>

;; <xiff vtable>
;; Таблица виртуальных методов
;; </xiff>

;; <xiff code>
;; Заглушки методов (jp _not_implemented)
;; Или вызовы импортированных функций
;; </xiff>

;; <xiff data>
;; Данные и переменные
;; </xiff>
```

### **Для C заголовков**

```c
// <xiff constants>
#define DRIVER_CONSTANT  value
enum DriverCommands { CMD1, CMD2 };
// </xiff>

// <xiff types>
typedef struct { ... } driver_t;
// </xiff>

// <xiff declarations>
extern void driver_method(uint8_t param) __z88dk_fastcall;
// </xiff>
```

### **Для C обёрток**

```c
// <xiff wrappers>
void driver_set_volume(uint8_t vol) __z88dk_fastcall {
    __asm
    ld a, l          ; fastcall: параметр в L
    call __driver_set_volume
    __endasm;
}
// </xiff>
```

### **Для INC файлов**

```asm
; <xiff externs>
extern _driver_method
extern _driver_variable
; </xiff>

; <xiff constants>
defc DRIVER_CONSTANT = value
; </xiff>
```
---

## Автоматическая генерация полиморфных драйверов

```lisp
(deftype video (driver)
  ()
:implementations (
    (video_mode0 driver_16bpp)
    (video_mode1 driver_8bpp)
    (video_mode2 driver_4bpp)
  )
  :switch-command CMD_SWITCH_DRIVER)

(deftype driver_16bpp (video) ... )
(deftype driver_8bpp (video) ... )
(deftype driver_4bpp (video) ... )
```

---

## Документация

В большинстве случаев, после имени можно добавлять документацию

```lisp
(deftype video (driver)
 (:methods
  (bar "test method" ((x int)(y int)) (int)))
```

При необходимости в аттрибутах

```lisp
  (bar ((x int)(y int)) (int)) :desc "test method")
```

## КОМАНДНАЯ СТРОКА

```bash
# Генерация всех файлов
xiff generate driver.xiff

# Генерация только ASM файлов
xiff generate driver.xiff --target asm

# Генерация только C файлов
xiff generate driver.xiff --target c

# Проверка синтаксиса без генерации
xiff check driver.xiff

# Список всех определений
xiff list driver.xiff

# Обновление только изменённых блоков
xiff update driver.xiff

# Создание шаблона нового драйвера
xiff new --name video --type driver

# Показать различия между текущими и генерируемыми файлами
xiff diff driver.xiff
```

---

## ПРАВИЛА ВАЛИДАЦИИ

1. **Уникальность имён**: Все определения в пределах модуля должны иметь уникальные имена
2. **Совместимость типов**: Типы аргументов и возвращаемых значений должны соответствовать регистрам
3. **Наследование**: Дочерний тип должен реализовывать все abstract методы родителя
4. **Регистры**: Нет конфликтов использования регистров в пределах метода
5. **Теги**: Каждый define-tag должен иметь уникальный порядок

---

## ПРИМЕР ПОЛНОГО ФАЙЛА

```lisp
;; video.xiff - Описание видео драйвера

(define-tag includes   :order 100)
(define-tag constants  :order 200)
(define-tag vtable     :order 300)
(define-tag code       :order 400)
(define-tag data       :order 500)

(module video
  ;; Выходные файлы
  (define-file c-header "include/drivers/video.h")
  (define-file c-code   "src/drivers/video.c")
  (define-file c-asm    "src/drivers/video_wrap.asm")
  (define-file inc      "inc/drivers/video.inc")
  (define-file asm      "drivers/video/video.asm")
  
  ;; Константы
  (defconst SCREEN_WIDTH  320)
  (defconst SCREEN_HEIGHT 200)
  (defconst BYTES_PER_LINE 40)
  
  ;; Перечисление режимов
  (defenum VideoMode (uint8_t)
    (MODE_0   0)   ; 256x192, 2 цвета
    (MODE_1   1)   ; 256x192, 4 цвета
    (MODE_2   2)   ; 256x192, 16 цветов
    (MODE_3   3))  ; 256x192, 256 цветов
  
  ;; Тип драйвера
  (deftype video (driver)
    ((mode    VideoMode MODE_0)
     (palette uint8_t[16] :import))  ; Импортированная палитра
    
    (:methods
      ;; Абстрактные методы (должны быть реализованы)
      (set_mode ((mode VideoMode a)) void :abstract)
      (clear    ((color uint8_t a)) void :abstract)
      
      ;; Виртуальные методы (есть реализация по умолчанию)
      (get_width  () (uint16_t hl) :virtual)
      (get_height () (uint16_t hl) :virtual)
      
      ;; Командный интерфейс
      (command ((cmd uint8_t a) (param uint16_t hl)) void))
    
    (:events
      (clear_screen 0x01 ((color uint8_t a)) void :call command))
      (set_palette  0x02 ((index uint8_t h) (color uint16_t l)) void :func command))
      (draw_sprite  0x03 ((x uint8_t b) (y uint8_t c) (sprite void* hl)) void :func command)))
  
  ;; Конкретная реализация для режима 0
  (deftype video_mode0 (video)
    ((buffer void* :import))  ; Указатель на видеобуфер
    
    (:methods
      (set_mode ((mode VideoMode a)) void :override video_mode0_set_mode)
      (clear    ((color uint8_t a)) void :override video_mode0_clear)
      (draw_pixel ((x uint8_t b) (y uint8_t c) (color uint8_t a)) void))))
```

---

## ОГРАНИЧЕНИЯ

1. **Нет анализа ASM**: XIFF не анализирует содержимое ASM файлов, только теги
2. **Нет оптимизации**: Генерируется прямой код без оптимизаций
3. **Ручное управление памятью**: Разработчик сам управляет банкованной памятью
4. **Минимальная проверка типов**: Проверяется только совместимость регистров и правильност таблиц vtable

---

## БУДУЩИЕ РАСШИРЕНИЯ

1. **Шаблоны кодогенерации**: Пользовательские шаблоны для генерации кода
2. **Плагины для редакторов**: Интеграция с VS Code, Vim, Emacs
3. **Статистика использования**: Анализ использования методов и констант
4. **Автодокументация**: Генерация документации из комментариев
5. **Миграции**: Автоматический рефакторинг при изменении интерфейсов
