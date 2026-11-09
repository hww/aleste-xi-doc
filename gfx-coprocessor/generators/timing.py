from common import load_yaml, svg_start, write_svg, esc, COLOR_GRID, COLOR_TEXT, COLOR_FILL_LIGHT

def render_timing(spec_file, output_file):
    data = load_yaml(spec_file)
    W = data.get("width", 800)
    signals = data["signals"]
    
    # Ищем первый сигнал, у которого есть состояния, чтобы определить количество тактов
    num_ticks = 0
    for sig in signals:
        if "states" in sig:
            num_ticks = len(sig["states"])
            break
            
    if num_ticks == 0:
        raise ValueError("No 'states' found in any signal in timing.yaml")

    # Геометрия
    left = 150
    top = 120
    col_w = (W - left - 32) / num_ticks
    row_h = 40
    H = top + len(signals) * row_h + 40

    parts = [svg_start(W, H, data["title"], data.get("subtitle", ""))]

    # Сетка тактов
    for i in range(num_ticks + 1):
        x = left + i * col_w
        parts.append(f'<line x1="{x}" y1="{top}" x2="{x}" y2="{top + len(signals)*row_h}" stroke="#CCCCCC" stroke-width="1"/>')
        if i < num_ticks:
            parts.append(f'<text x="{x + col_w/2}" y="{top - 15}" text-anchor="middle" style="font: 12px monospace; fill: #666;">T{i+1}</text>')

    # Сигналы
    for idx, sig in enumerate(signals):
        y_mid = top + idx * row_h + row_h / 2
        y_top = top + idx * row_h
        y_bot = y_top + row_h

        # Имя сигнала
        parts.append(f'<text x="{left - 10}" y="{y_mid + 5}" text-anchor="end" style="font: 700 14px monospace; fill: {COLOR_TEXT};">{esc(sig["name"])}</text>')

        if sig.get("type") == "clock":
            # Рисуем тактовый сигнал (меандр)
            path = f"M{left} {y_bot} "
            for i in range(num_ticks):
                x1 = left + i * col_w
                x2 = x1 + col_w
                path += f"L{x1} {y_bot} L{x1} {y_top} L{x2} {y_top} L{x2} {y_bot} "
            parts.append(f'<path d="{path}" fill="none" stroke="{COLOR_GRID}" stroke-width="2"/>')
        
        elif "states" in sig:
            states = sig["states"]
            for i, state in enumerate(states):
                x = left + i * col_w
                # Для шин (значений) рисуем прямоугольник с текстом
                if state not in ("0", "1"):
                    parts.append(f'<rect x="{x}" y="{y_top+5}" width="{col_w}" height="{row_h-10}" fill="{COLOR_FILL_LIGHT}" stroke="{COLOR_GRID}" stroke-width="1"/>')
                    parts.append(f'<text x="{x + col_w/2}" y="{y_mid + 5}" text-anchor="middle" style="font: 13px monospace; fill: {COLOR_TEXT};">{esc(state)}</text>')
                else:
                    # Для битовых сигналов (0/1) рисуем линию на верхнем или нижнем уровне
                    y_val = y_top + 5 if state == "1" else y_bot - 5
                    parts.append(f'<line x1="{x}" y1="{y_val}" x2="{x+col_w}" y2="{y_val}" stroke="{COLOR_GRID}" stroke-width="2"/>')
                    # Соединительные вертикальные линии, если значение меняется
                    if i > 0:
                        prev_state = states[i-1]
                        if prev_state != state and prev_state in ("0","1"):
                            y_prev = y_top + 5 if prev_state == "1" else y_bot - 5
                            parts.append(f'<line x1="{x}" y1="{y_prev}" x2="{x}" y2="{y_val}" stroke="{COLOR_GRID}" stroke-width="2"/>')

    write_svg(output_file, "".join(parts))

if __name__ == "__main__":
    render_timing("timing.yaml", "timing.svg")