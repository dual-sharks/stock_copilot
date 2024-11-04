import re
import json
from crewai import Task, Crew, Process

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
        # Use the agent's tool to get stock data
        json_data = agent.tools[0].get_stock_info(symbol)
        if 'error' not in json_data:
            return summarize_json(agent, json_data)
        else:
            return json_data['error']
    else:
        # Create a temporary task and Crew to handle the non-stock task description
        task = Task(
            description=task_description,
            expected_output="Detailed response with insights.",
            agent=agent  # Assign the agent to the task
        )
        
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential
        )
        
        result = crew.kickoff()
        return result if result else "No relevant data found or unable to process."

# Function to summarize JSON data using an agent
def summarize_json(agent, json_data):
    """Summarize JSON data using the agent through a Crew task."""
    json_string = json.dumps(json_data, indent=2)
    task_description = (
        f"Summarize the following JSON data into a comprehensive report:\n\n{json_string}\n\n"
        "Highlight key points and relevant details."
    )

    task = Task(
        description=task_description,
        expected_output="Summarized report with key insights.",
        agent=agent
    )

    crew = Crew(
        agents=[agent],
        tasks=[task],
        process=Process.sequential
    )

    result = crew.kickoff()
    return result if result else "No relevant data found or unable to process."
