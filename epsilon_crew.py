from textwrap import dedent
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI
from tools import PolygonAPITool
import re
import json
import streamlit as st

# Initialize the Polygon API tool
polygon_tool = PolygonAPITool()

# Set up the LLM
llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

# Define the agents with a more generic purpose
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
)

researcher = Agent(
    role="Researcher",
    goal="Conduct thorough research on any given topic. If the topic is related to stocks, use the stock tool to fetch data.",
    backstory="You're a versatile researcher, capable of delving into any subject matter, with a specialization in stock market analysis when needed.",
    allow_delegation=False,
    tools=[polygon_tool],  # Add the tool for stock data retrieval
    llm=llm
)

writer = Agent(
    role="Writer",
    goal="Create well-crafted reports on any given topic",
    backstory="You're an experienced writer who can produce high-quality content across various domains.",
    allow_delegation=False,
    llm=llm
)

# Function to extract stock symbols from task descriptions
def extract_stock_symbol(task_description):
    """Extract potential stock symbols from a task description."""
    pattern = r'\b[A-Z]{1,5}\b'
    matches = re.findall(pattern, task_description)
    return matches[0] if matches else None

# Function to route agent tasks and summarize JSON data if applicable
def route_agent_to_tool_and_summarize(agent, task_description):
    """Route tasks to the appropriate tool and summarize JSON data if required."""
    symbol = extract_stock_symbol(task_description)
    if symbol:
        json_data = agent.tools[0].get_stock_info(symbol)
        if 'error' not in json_data:
            # Summarize JSON using the agent
            return summarize_json(agent, json_data)
        else:
            return json_data['error']
    else:
        return agent.run_task(task_description)

def summarize_json(agent, json_data):
    """Summarize JSON data using the agent through a Crew task."""
    json_string = json.dumps(json_data, indent=2)
    task_description = (
        f"Summarize the following JSON data into a comprehensive report:\n\n{json_string}\n\n"
        "Highlight key points and relevant details."
    )

    # Create a temporary task for summarizing the JSON data and assign the agent
    task = Task(
        description=task_description,
        expected_output="Summarized report with key insights.",
        agent=agent  # Assign the agent to the task
    )

    # Create a crew instance for this specific task
    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential  # Use a valid process type
    )

    # Execute the task and get the result
    result = crew.kickoff()

    # Debugging: Print the result to inspect the data
    print("Result from crew.kickoff():", result)

    # Directly return the result without unnecessary conditions
    return result if result else "No relevant data found or unable to process."

# Function to create a dynamic crew instance
def create_crew(topic, agent):
    """Create a dynamic Crew instance with the agent assigned to the task."""
    task = Task(
        description=dedent(
            f"""
            Write a comprehensive report on the topic: {topic}.
            Include key points, in-depth analysis, and takeaways.
            """
        ),
        expected_output="Detailed report with analysis and takeaways.",
        agent=agent  # Explicitly assign the agent to the task
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential  # Use a valid process type
    )
    return crew

def generate_detailed_report(topic):
    """Generate a detailed report using the Crew framework."""
    crew = create_crew(topic, researcher)
    result = route_agent_to_tool_and_summarize(researcher, topic)
    return result