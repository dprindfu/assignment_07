import os

import pandas as pd
import streamlit as st

from rivals import (
    ABOVE_ALL,
    ABOVE_AVERAGE,
    BELOW_ALL,
    BELOW_AVERAGE,
    DECISIONS_FILE,
    MENUS_FILE,
    add_canonical,
    compare_prices,
    gap_analysis,
    match_items,
    price_table,
)
from rivals.settings import DECISION_COLUMNS

st.set_page_config(layout="wide")
st.title("Salt City: Prices and Gaps")

if not os.path.exists(MENUS_FILE):
    st.info("No menu data found. Please scrape the menus first.")
    st.stop()

menus = pd.read_csv(MENUS_FILE)

if os.path.exists(DECISIONS_FILE):
    decisions = pd.read_csv(DECISIONS_FILE)
else:
    decisions = pd.DataFrame(columns=DECISION_COLUMNS)

matches = match_items(menus, decisions)

waiting = len(matches[matches["status"] == "unreviewed"])

if waiting > 0:
    st.warning(
        f"{waiting} items have not been reviewed and are left out of the "
        "analysis. Finish reviewing them on the Review Matches page."
    )

menus = add_canonical(menus, matches)
prices = price_table(menus)
comparison = compare_prices(prices)
gaps = gap_analysis(menus)

prices_tab, gaps_tab = st.tabs(["Prices", "Gaps"])

with prices_tab:
    below = comparison[
        comparison["our_position"].isin([BELOW_ALL, BELOW_AVERAGE])
    ]

    above = comparison[
        comparison["our_position"].isin([ABOVE_ALL, ABOVE_AVERAGE])
    ]

    col1, col2 = st.columns(2)

    col1.metric("Priced below the market", len(below))
    col2.metric("Priced above the market", len(above))

    products = sorted(comparison["canonical"].dropna().unique())

    selected_products = st.multiselect(
        "Products",
        products,
        key="products",
        placeholder="All products"
    )

    if selected_products:
        shown = comparison[
            comparison["canonical"].isin(selected_products)
        ]
    else:
        shown = comparison

    st.dataframe(shown, hide_index=True)

    st.caption(
        "👍👍 lower than all of them · 👍 lower than their average · "
        "👉👈 average · 👎 higher than their average · "
        "👎👎 higher than all of them"
    )

with gaps_tab:
    st.subheader("Only them — what we don't sell yet")

    only_them = gaps[gaps["where"] == "only them"]
    st.dataframe(only_them, hide_index=True)

    st.subheader("Only us — what sets us apart")

    only_us = gaps[gaps["where"] == "only us"]
    st.dataframe(only_us, hide_index=True)
