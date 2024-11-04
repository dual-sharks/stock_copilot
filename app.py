import streamlit as st

from alpha_crew import first_chatbot
st.title("Riddle Generator App")
st.write("Click the button below to generate a riddle.")

if st.button("Generate Riddle"):
        # Run the crew task and display the result
    result = first_chatbot()
    if result:
            st.write("Result:")
            # Display the result in a text area to avoid truncation
            st.text_area("Generated Riddle", result, height=300)
    else:
        st.warning("No result was returned.")