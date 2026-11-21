import re

# Lines on a menu card that are decoration, not data.
NOISE = {"NEW!", "NEW", "V", "GF"}


def clean_price(text: str) -> float:
    text = text.replace("$", "").replace(",", "").strip()
    return float(text)


def clean_card_lines(text: str) -> list[str]:
    lines = text.split("\n")
    line_list = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if all(w in NOISE for w in line.split()):
            continue

        line_list.append(line)

    return line_list



def parse_price_line(line: str) -> list[tuple[str, float]]:
    match = re.findall(r"([SML])?\s*(\$[\d.,]+)", line)
    output = []

    for size, price in match:
        if not size:
            size = "Each"

        output.append((size, clean_price(price)))

    return output
    


def card_rows(cafe: str, category: str, card_text: str) -> list[dict]:
    lines = clean_card_lines(card_text)

    item = lines[0]

    price_line = next(line for line in lines if "$" in line)

    prices = parse_price_line(price_line)

    rows = []

    for size, price in prices:
        rows.append({
            "cafe": cafe,
            "category": category,
            "item": item,
            "size": size,
            "price": price
        })
    return rows
