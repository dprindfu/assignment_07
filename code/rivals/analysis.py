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
    """`menus` plus a `canonical` column: the one name every café's item goes by.

    Our rows: their own `item`. Rival rows: the `matched_to` from `matches` for
    that (`cafe`, `item`) — missing for items the owner has not reviewed yet.
    Every row of `menus` is kept, in order; `menus` itself is not changed.
    """
    result = menus.copy()

    lookup = matches.set_index(["cafe", "item"])["matched_to"]

    keys = pd.MultiIndex.from_frame(result[["cafe", "item"]])
    result["canonical"] = lookup.reindex(keys).to_numpy()

    our_rows = result["cafe"] == OUR_CAFE
    result.loc[our_rows, "canonical"] = result.loc[our_rows, "item"]

    return result


def price_table(menus: pd.DataFrame) -> pd.DataFrame:
    """Price per (canonical item, size) per café.  *(Provided.)*

    Rows are (`canonical`, `size`), sizes in menu order (S, M, L, Each); columns
    are the cafés; values are prices. Rows with no canonical name (not reviewed
    yet) are left out.
    """
    known = menus.dropna(subset=["canonical"])
    table = known.pivot_table(index=["canonical", "size"], columns="cafe",
                              values="price", aggfunc="first")
    order = {size: rank for rank, size in enumerate(SIZES)}
    return table.sort_index(key=lambda level: level.map(order) if level.name == "size"
                            else level)


def price_position(ours: float, low: float, average: float, high: float) -> str:
    """Where our price stands against the rivals' prices for the same item and size.

    `low`, `average` and `high` are the rivals' lowest, average and highest price.
    Returns one of the five labels in settings — the names, not the text:

        ours below `low`                 -> BELOW_ALL       "👍👍 Lowest Price"
        ours above `high`                -> ABOVE_ALL       "👎👎 Highest Price"
        otherwise, ours below `average`  -> BELOW_AVERAGE   "👍 Lower than average"
        otherwise, ours above `average`  -> ABOVE_AVERAGE   "👎 Higher than average"
        otherwise (ours equals average)  -> AT_AVERAGE      "👉👈 Average"

    Check them in that order: with one rival, low, average and high are the same.
    """
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
    """Our price next to every rival's, for every item and size we both sell.

    `prices` is price_table's result. Returns one row per (canonical, size) where
    we have a price *and* at least one rival does, in price_table's order, with
    columns:

        canonical  size  our_price  <one column per rival>  rival_avg  our_position

    - `our_price`: the settings.OUR_CAFE column, renamed.
    - the rival columns: every other column of `prices`, in the same order
      (missing where that rival doesn't sell it).
    - `rival_avg`: the average of the rivals' prices, ignoring missing ones,
      rounded to 2 places.
    - `our_position`: price_position(our_price, the rivals' lowest, rival_avg, the
      rivals' highest) for that row.

    Plain index.
    """
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
    """Which items only we sell, which only rivals sell, and which we both do.

    `menus` must have a `canonical` column (add_canonical). Rival rows with no
    canonical name (unreviewed) are left out. Returns one row per (canonical, kind):

        canonical  kind  where  rivals  sold_by

    - `where`: "only us", "only them" or "both" — an outer merge of our items with
      the rivals' items with `indicator=True`, its `_merge` column relabelled.
    - `rivals`: how many different rivals sell it (0 for "only us").
    - `sold_by`: those rivals' names, sorted, joined with ", " ("" for "only us").

    Sorted by `where` ("only them" first, then "only us", then "both"), then
    `rivals` (most first), then `canonical`; plain index.
    """
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
