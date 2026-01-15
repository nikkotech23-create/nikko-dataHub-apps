import streamlit as st
import pandas as pd
import numpy as np

st.title("Interactive Data Explorer")

st.write("Move the slider to change how much data is generated.")

# User input
rows = st.slider("Number of rows", min_value=10, max_value=500, value=50)

# Generate random data
data = pd.DataFrame({
    "x": np.arange(rows),
    "y": np.random.randn(rows).cumsum()
})

# Show dataframe
st.subheader("Generated Data")
st.dataframe(data)

# Line chart
st.subheader("Line Chart")
st.line_chart(data, x="x", y="y")

# Text input example
name = st.text_input("Your name")
if name:
    st.success(f"Welcome, {name}! Enjoy exploring the data.")