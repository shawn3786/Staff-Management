import streamlit as st

st.set_page_config(page_title="Shift Manager Test", layout="wide")
st.title("✅ Streamlit is working!")

tab1, tab2 = st.tabs(["Manager", "Employee"])

with tab1:
    st.subheader("Manager Dashboard")
    if st.button("Add Task"):
        st.success("Task added!")

with tab2:
    st.subheader("Employee Dashboard")
    st.write("Here you will see your tasks.")
