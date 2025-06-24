import streamlit as st
import pandas as pd
import numpy as np

# ---- Login ----
USERNAME = "D1Rect0R"
PASSWORD = "AHSTigerB@nd"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🎺 Uniform Manager Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.authenticated = True
            st.experimental_rerun()
        else:
            st.error("Incorrect username or password")
    st.stop()

# ---- App ----
st.title("🎷 Marching Band Uniform Manager (Web Edition)")

# ---- Load CSV ----
uploaded_file = st.file_uploader("📄 Upload Uniform Data (.csv)", type="csv")
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.DataFrame(columns=["Name", "Height", "Waist", "Seat", "InUse"])

df["InUse"] = df["InUse"].fillna(0).astype(bool)

# ---- Add Uniform ----
with st.expander("➕ Add New Uniform"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        new_name = st.text_input("Name")
    with col2:
        new_height = st.number_input("Height", min_value=0.0, step=0.1)
    with col3:
        new_waist = st.number_input("Waist", min_value=0.0, step=0.1)
    with col4:
        new_seat = st.number_input("Seat", min_value=0.0, step=0.1)
    if st.button("Add Uniform"):
        if new_name:
            df.loc[len(df)] = [new_name, new_height, new_waist, new_seat, False]
            st.success("Uniform added!")

# ---- Save Button ----
st.download_button("📂 Download Updated CSV", df.to_csv(index=False), file_name="uniforms.csv", mime="text/csv")

# ---- Search Area ----
st.header("🔍 Find a Match")

with st.form("match_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        s_height = st.number_input("Target Height", step=0.1)
    with col2:
        s_waist = st.number_input("Target Waist", step=0.1)
    with col3:
        s_seat = st.number_input("Target Seat", step=0.1)

    st.write("### Filters")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        min_height = st.number_input("Min Height", value=0.0, step=0.1)
    with c2:
        max_height = st.number_input("Max Height", value=999.0, step=0.1)
    with c3:
        min_waist = st.number_input("Min Waist", value=0.0, step=0.1)
    with c4:
        max_waist = st.number_input("Max Waist", value=999.0, step=0.1)

    c5, c6 = st.columns(2)
    with c5:
        min_seat = st.number_input("Min Seat", value=0.0, step=0.1)
    with c6:
        max_seat = st.number_input("Max Seat", value=999.0, step=0.1)

    match_count = st.selectbox("Number of Matches", [1, 3, 5, 7, 10], index=3)
    hide_in_use = st.checkbox("Hide Checked Out", value=False)

    submitted = st.form_submit_button("Find Matches")

# ---- Matching Logic ----
if submitted:
    filtered_df = df[
        (df["Height"] >= min_height) & (df["Height"] <= max_height) &
        (df["Waist"] >= min_waist) & (df["Waist"] <= max_waist) &
        (df["Seat"] >= min_seat) & (df["Seat"] <= max_seat)
    ]
    if hide_in_use:
        filtered_df = filtered_df[~filtered_df["InUse"]]

    def score(row):
        return abs(row["Height"] - s_height) + abs(row["Waist"] - s_waist) + abs(row["Seat"] - s_seat)

    if not filtered_df.empty:
        filtered_df["Score"] = filtered_df.apply(score, axis=1)
        match_df = filtered_df.sort_values(by="Score").head(match_count)

        st.write("### 🎯 Top Matches")
        for idx, row in match_df.iterrows():
            bg_color = "#C8FACC" if row["Score"] <= 2 else "#FFF6AA" if row["Score"] <= 5 else "#FFCCCC"
            if row["InUse"]:
                bg_color = "#DDDDDD"

            st.markdown(
                f"""
                <div style='background-color:{bg_color}; padding:10px; border-radius:5px; margin-bottom:10px'>
                    <b>{row['Name']}</b> {"(In Use)" if row["InUse"] else ""}<br>
                    Height: {row["Height"]} | Waist: {row["Waist"]} | Seat: {row["Seat"]}<br>
                    <small>Closeness Score: {row["Score"]:.2f}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.session_state["match_ids"] = match_df.index.tolist()
    else:
        st.warning("No matches found.")

# ---- Check Out / Return ----
if "match_ids" in st.session_state:
    st.write("### 🔒 Toggle Check Out Status")
    selected = st.selectbox("Select a matched uniform", st.session_state["match_ids"])
    if st.button("Check Out / Return"):
        df.at[selected, "InUse"] = not df.at[selected, "InUse"]
        st.success("Status updated!")
