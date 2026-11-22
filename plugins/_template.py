"""
Шаблон плагина buildex. Файлы, чьё имя начинается с «_», не загружаются — скопируйте шаблон в
plugins/<имя>.py (глобально) или src/<проект>/plugins/<имя>.py (только для проекта) и переименуйте.

Плагин получает всё нужное через объект api (ничего импортировать из buildex не нужно):

  api.register_kind(name, validate, diagram=None, table=None, anchors=None, views=None, order=0, help=None)
  api.register_directive(name, fn)            # {{name:arg}} в Markdown  ->  fn(arg, ctx, P) -> str
  api.Svg, api.svg_doc, api.tw                # рисование SVG, оценка ширины текста
  api.md_table, api.notes_md                  # таблицы Markdown
  api.check_keys, api.as_int, api.as_list, api.W_, api.BASE_KEYS, api.NS, api.anchor_id, api.fmt_pin
  api.GROUP_FILLS, api.FILL_A, api.FILL_B, api.FILL_FIXED, api.INK, api.GRAY_TXT
  api.KINDS                                   # реестр сущностей (читать можно, менять — только register_kind)

Ошибки сообщаются так:  P.diag.err(where, "что не так")  /  P.diag.warn(where, "...")
Результат разбора кладите в spec["_что-то"] — оттуда его заберут diagram/table/anchors.
Исключение внутри плагина не роняет сборку: оно превращается в обычную ошибку с именем сущности.
"""


def register(api):
    def validate(spec, P):
        where = api.W_(spec)
        api.check_keys(spec, api.BASE_KEYS + ["items"], where, P)
        items = api.as_list(spec.get("items"))
        if not items:
            P.diag.err(where, "'items' must be a non-empty list")
        spec["_items"] = [str(x) for x in items]

    def diagram(spec, P):
        svg = api.Svg()
        y = 100
        for it in spec["_items"]:
            svg.rect(32, y, 240, 32, fill=api.FILL_A, sw=1.5)
            svg.text(152, y + 21, it, 14, bold=True)
            y += 40
        return api.svg_doc(320, y + 16, spec.get("title", spec["name"]), spec.get("subtitle", ""), svg.inner())

    def table(spec, P):
        return api.md_table(["#", "Item"], [[i + 1, x] for i, x in enumerate(spec["_items"])])

    api.register_kind("stack", validate=validate, diagram=diagram, table=table,
                      anchors=lambda spec: set(spec.get("_items", [])),
                      help=("Пример: вертикальный список блоков.",
                            "kind: stack\nname: NAME\ntitle: \"Stack\"\nitems: [A, B, C]"))
