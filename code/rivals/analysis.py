from unittest import result

import pandas as pd

from .settings import (
    ABOVE_ALL,
    ABOVE_AVERAGE,
    AT_AVERAGE,
    BELOW_ALL,
    BELOW_AVERAGE,
    OUR_CAFE,
    SIZES,
)


def add_canonical(menus: pd.DataFrame, matches: pd.DataFrame) -> pd.DataFrame:
    result = menus.copy()

    lookup = matches.set_index(["cafe", "item"])["matched_to"]

    keys = pd.MultiIndex.from_frame(result[["cafe", "item"]])
    result["canonical"] = lookup.reindex(keys).to_numpy()

    our_rows = result["cafe"] == OUR_CAFE
    result.loc[our_rows, "canonical"] = result.loc[our_rows, "item"]

    return result


def price_table(menus: pd.DataFrame) -> pd.DataFrame:
    known = menus.dropna(subset=["canonical"])
    table = known.pivot_table(index=["canonical", "size"], columns="cafe",
                              values="price", aggfunc="first")
    order = {size: rank for rank, size in enumerate(SIZES)}
    return table.sort_index(key=lambda level: level.map(order) if level.name == "size"
                            else level)


def price_position(ours: float, low: float, average: float, high: float) -> str:
    if ours < low:
        return BELOW_ALL
    if ours > high:
        return ABOVE_ALL
    if ours < average:
        return BELOW_AVERAGE
    if ours > average:
        return ABOVE_AVERAGE
    return AT_AVERAGE



def compare_prices(prices: pd.DataFrame) -> pd.DataFrame:
    rival_cafes = [cafe for cafe in prices.columns if cafe != OUR_CAFE]
    rivals = prices[rival_cafes]
    ours = prices[OUR_CAFE]

    valid = ours.notna() & rivals.notna().any(axis=1)

    rivals = rivals[valid]
    ours = ours[valid]

    result = rivals.copy()
    result.insert(0, "size", result.index.get_level_values("size"))
    result.insert(0, "canonical", result.index.get_level_values("canonical"))
    result.insert(2, "our_price", ours)

    result["rival_avg"] = rivals.mean(axis=1).round(2)

    result["our_position"] = result.apply(
        lambda row: price_position(
            row["our_price"],
            row[rival_cafes].min(),
            row[rival_cafes].mean(),
            row[rival_cafes].max()
        ),
        axis=1
    )

    return result.reset_index(drop=True)



def gap_analysis(menus: pd.DataFrame) -> pd.DataFrame:
    known = menus.dropna(subset=["canonical"])

    our_items = known[
        known["cafe"] == OUR_CAFE
    ][["canonical", "kind"]].drop_duplicates()

    rival_items = known[
        known["cafe"] != OUR_CAFE
    ][["canonical", "kind", "cafe"]]

    rival_items = rival_items.groupby(
        ["canonical", "kind"]
    ).agg(
        rivals=("cafe", "nunique"),
        sold_by=("cafe", lambda names: ", ".join(sorted(set(names))))
    ).reset_index()

    result = our_items.merge(
        rival_items,
        on=["canonical", "kind"],
        how="outer",
        indicator=True
    )

    result["where"] = result["_merge"].map({
        "left_only": "only us",
        "right_only": "only them",
        "both": "both"
    })

    result["rivals"] = result["rivals"].fillna(0).astype(int)
    result["sold_by"] = result["sold_by"].fillna("")

    result["where"] = pd.Categorical(
        result["where"],
        categories=["only them", "only us", "both"],
        ordered=True
    )

    result = result.sort_values(
        ["where", "rivals", "canonical"],
        ascending=[True, False, True]
    )

    return result[
        ["canonical", "kind", "where", "rivals", "sold_by"]
    ].reset_index(drop=True)