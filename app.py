import streamlit as st
import time
from epsilon_crew import create_crew, route_agent_to_tool_and_summarize, researcher

# Streamlit app function
def main():
    st.title("Dynamic Report Generator with Stock Analysis")
    st.write("Enter a topic for which you want a report to be generated. For stock questions, ensure to include the ticker symbol.")

    # User input for the topic
    user_input = st.text_input("Topic", placeholder="Enter a topic, e.g., 'Stock analysis for AAPL'")

    if st.button("Generate Report"):
        if user_input:
            crew = create_crew(user_input, researcher)
            result = route_agent_to_tool_and_summarize(researcher, user_input)

            # Ensure result is extracted as a string from the CrewOutput object
            if hasattr(result, 'content'):
                report_text = result.content  # Extract content from CrewOutput object
            else:
                report_text = str(result)  # Convert to string in case it's not plain text

            if report_text:
                st.write("Generated Summary Report:")
                placeholder = st.empty()  # Create an empty container for progressive display

                words = report_text.split()
                full_text = ""
                for word in words:
                    full_text += word + " "
                    placeholder.markdown(f"{full_text}")  # Update the placeholder with markdown
                    time.sleep(0.05)  # Adjust the speed of the display (e.g., 0.05 seconds)

            else:
                st.warning("No relevant data found.")
        else:
            st.warning("Please enter a topic before generating the report.")

if __name__ == "__main__":
    main()
