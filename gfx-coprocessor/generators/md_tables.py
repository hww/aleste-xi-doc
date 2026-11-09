from common import load_yaml, write_md

def gen_alu_table():
    data = load_yaml("alu.yaml")
    md = "| Код | Имя | Действие |\n| --- | --- | --- |\n"
    for op in data["operations"]:
        md += f'| {op["code"]} | **{op["name"]}** | {op["description"]} |\n'
    write_md("alu-table.md", md)

def gen_registers_table():
    data = load_yaml("registers.yaml")
    md = "| № | Имя | Назначение | Группа |\n| --- | --- | --- | --- |\n"
    for r in data["registers"]:
        md += f'| {r["index"]:02d} | **{r["name"]}** | {r["description"]} | {r["group"]} |\n'
    write_md("registers-table.md", md)

def gen_operand_table():
    data = load_yaml("operand_map.yaml")
    md = "| Адрес | Имя | Чтение | Запись |\n| --- | --- | --- | --- |\n"
    for e in data["entries"]:
        md += f'| {e["address"]} | **{e["name"]}** | {e["read"]} | {e["write"]} |\n'
    write_md("operand-table.md", md)

def gen_commands_table():
    data = load_yaml("commands.yaml")
    
    md = "### Диспетчеризация\n\n"
    md += "| Диапазон | Имя | Длина (байт) | Payload | Описание |\n"
    md += "| --- | --- | --- | --- | --- |\n"
    for d in data.get("dispatch", []):
        length = d.get("length", "—")
        payload = d.get("payload", "—")
        desc = d.get("description", "")
        md += f'| {d["range"]} | **{d["name"]}** | {length} | {payload} | {desc} |\n'
    
    md += "\n### Команды\n\n"
    md += "| Опкод | Имя | Длина (байт) | Payload | Описание |\n"
    md += "| --- | --- | --- | --- | --- |\n"
    for c in data.get("commands", []):
        length = c.get("length", "—")
        payload = c.get("payload", "—")
        desc = c.get("description", "")
        md += f'| {c["opcode"]} | **{c["name"]}** | {length} | {payload} | {desc} |\n'
    
    write_md("commands-table.md", md)

if __name__ == "__main__":
    gen_alu_table()
    gen_registers_table()
    gen_operand_table()
    gen_commands_table()