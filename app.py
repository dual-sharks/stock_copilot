import streamlit as st

from beta_crew import second_chatbot
st.title("Research Article")
st.write("Click the button below to generate an article.")

if st.button("Generate Article"):
        # Run the crew task and display the result
    result = second_chatbot()
    if result:
            st.write("Result:")
            # Display the result in a text area to avoid truncation
            st.text_area("Generated Article", result, height=300)
    else:
        st.warning("No result was returned.")