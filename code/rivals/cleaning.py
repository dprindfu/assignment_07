import re

# Lines on a menu card that are decoration, not data.
NOISE = {"NEW!", "NEW", "V", "GF"}


def clean_price(text: str) -> float:
    """A price as a number: "$4.75" -> 4.75, " $1,029.00 " -> 1029.0.

    How to build it:

    - Remove the dollar sign and any commas with `.replace()`.
    - `.strip()` the spaces, then convert with `float()`.
    """
    text = text.replace("$", "").replace(",", "").strip()
    return float(text)


def clean_card_lines(text: str) -> list[str]:
    """The useful lines of a menu card, in order, with the decoration removed.

        clean_card_lines("NEW!\\n\\nAvocado Toast\\nV GF\\n$8.50\\nToast.")
        -> ["Avocado Toast", "$8.50", "Toast."]

    Remove: blank lines, and lines made only of NOISE words (badges like "NEW!"
    and dietary tags like "V" or "V GF").

    How to build it:

    - `text.split("\\n")` gives a list of lines. Loop over it.
    - `.strip()` each line. Skip it if it is empty.
    - Skip it if every word in it is in NOISE: `all(w in NOISE for w in line.split())`.
    - Otherwise append it to a list, and return the list.
    """
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
    """One row per size for one menu card.

        card_rows("Lakeshore Lattes", "Tea & More", "NEW!\\nMatcha Latte\\nV\\n"
                  "S $5.05 · L $6.25\\nMatcha.")
        -> [{"cafe": "Lakeshore Lattes", "category": "Tea & More",
             "item": "Matcha Latte", "size": "S", "price": 5.05},
            {... "size": "L", "price": 6.25}]

    How to build it:

    - `clean_card_lines()` the text. The first line is the item's name. The price
      line is the first line with a "$" in it — usually the second, but don't
      count on it.
    - `parse_price_line()` the price line, and build one dict per (size, price)
      pair with the five keys above. Return the list.
    """
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
