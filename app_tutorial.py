
import streamlit as st

st.title("This is my first application")

st.header("Compare and contrast CSBA's against one another")

st.subheader("Use this information to help you detemine where to invest")

st.markdown("this is a description")



text_input = st.text_input("Enter some data:", "")
st.markdown(f"my input is : {text_input}")

text_area_input = st.text_area("Enter a short description")
number_input = st.number_input("Enter some number:", 
                               min_value=0,
                               max_value=100,
                               value=50,
                               step=1
                            )

if name !="":
    st.markdown(
        f"""

""")


# st.markdown(
#     "lorem ipsum"
#             )

# st.markdown(
#     '''
#     this is a second description
# '''
# )

# st.markdown("*this is italic text*")

# st.markdown("**BOLD**")

# st.markdown("* first")
# st.markdown("* second")

# st.info("this is information")
# st.warning("this is a warning")
# st.error("error")


# json_response = {"status": 200, "text": "text succeed!"}

# st.write(json_response)

# list_data = ["item1", "item2", "item3"]

# st.write(list_data)



