import os

import pandas as pd
import streamlit as st

from rivals import CAFES, MENUS_FILE, OUR_CAFE, run_scraper

st.title("Salt City: Scrape the Rivals")
st.markdown("Pick the cafes to scrape")

cafes = st.multiselect(
    "Cafés",
    options=list(CAFES),
    default=list(CAFES),
    key="cafes"
)

# Choice Button
if st.button("Scrape", key="scrape"):
    if cafes:
        with st.spinner("Scraping menus..."):
            result = run_scraper(cafes)

        if result.returncode == 0:
            message = result.stdout.strip().splitlines()[-1]
            st.success(message)
        else:
            st.error("The scraper failed.")
            st.code(result.stderr[-2000:])
    else:
        st.warning("Select at least 1 cafe")

if not os.path.exists(MENUS_FILE):
    st.info("Click Scrape to collect the menus.")
    st.stop()

# load data
menus = pd.read_csv(MENUS_FILE)

theirs = menus[menus["cafe"] != OUR_CAFE]

cafe_count = theirs["cafe"].nunique()
item_count = theirs[["cafe", "item"]].drop_duplicates().shape[0]
row_count = len(theirs)

col1, col2, col3 = st.columns(3)

col1.metric("Cafés", cafe_count)
col2.metric("Items", item_count)
col3.metric("Rows", row_count)

# Download
st.dataframe(menus, hide_index=True)

st.download_button(
    "Download the dataset",
    menus.to_csv(index=False),
    file_name="menus.csv",
    mime="text/csv",
    key="download"
)
