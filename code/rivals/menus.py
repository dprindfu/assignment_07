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
    menus = pd.DataFrame(rows, columns=MENU_COLUMNS)
    menus = menus.reindex(columns=[
        "cafe", "category", "item", "size", "price"
    ])
    return menus


def add_kinds(menus: pd.DataFrame, categories: pd.DataFrame) -> pd.DataFrame:
    merged = menus.merge(
        categories,
        how="left",
        on=["cafe", "category"]
    )
    return merged


def build_dataset(rival_rows: list[dict]) -> pd.DataFrame:
    menu = load_our_menu()
    rivals = menus_table(rival_rows)

    combined = pd.concat([menu, rivals], ignore_index=True)
    categories = pd.read_csv(CATEGORIES_FILE)
    dataset = add_kinds(combined, categories)
    return dataset[
        ["cafe", "category", "kind", "item", "size", "price"]
    ].reset_index(drop=True)
