import pandas as pd

from .settings import (
    CATEGORIES_FILE,
    MENU_COLUMNS,
    OUR_CAFE,
    OUR_MENU_FILE,
)


def load_our_menu() -> pd.DataFrame:
    """Salt City Coffee's menu with the scrapers' five columns.  *(Provided.)*"""
    ours = pd.read_csv(OUR_MENU_FILE)
    return pd.DataFrame({
        "cafe": OUR_CAFE,
        "category": ours["category"],
        "item": ours["item"],
        "size": ours["size"],
        "price": ours["price"],
    })


def menus_table(rows: list[dict]) -> pd.DataFrame:
    """Scraped rows as a DataFrame with exactly these columns, in this order:
    `cafe`, `category`, `item`, `size`, `price`.

    Extra keys a scraper might add are left out. An empty list gives an empty
    table that still has the five columns.
    """
    # TODO: your code here
    menus = pd.DataFrame(rows, columns=MENU_COLUMNS)
    menus = menus.reindex(columns=[
        "cafe", "category", "item", "size", "price"
    ])
    return menus


def add_kinds(menus: pd.DataFrame, categories: pd.DataFrame) -> pd.DataFrame:
    """`menus` plus a `kind` column ("drink" or "food"): each row's (`cafe`,
    `category`) looked up in `categories` (data/categories.csv).

    Every row is kept, in order (a one-sided merge). A category that is not in
    `categories` gets a missing kind. `menus` itself is not changed.
    """
    # TODO: your code here
    merged = menus.merge(
        categories,
        how="left",
        on=["cafe", "category"]
    )
    return merged


def build_dataset(rival_rows: list[dict]) -> pd.DataFrame:
    """The whole dataset: our menu first, then the rivals' rows, as one table.

    `pd.concat` our menu (`load_our_menu()`) with `menus_table(rival_rows)`, then
    `add_kinds` with data/categories.csv. The columns are settings.MENU_COLUMNS,
    in that order; plain index.
    """
    menu = load_our_menu()
    rivals = menus_table(rival_rows)

    combined = pd.concat([menu, rivals], ignore_index=True)
    categories = pd.read_csv(CATEGORIES_FILE)
    dataset = add_kinds(combined, categories)
    return dataset[
        ["cafe", "category", "kind", "item", "size", "price"]
    ].reset_index(drop=True)
