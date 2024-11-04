from textwrap import dedent
import os
from crewai import Agent, Task, Crew, Process

from langchain_openai import ChatOpenAI

llm = OpenAIGPT4 = ChatOpenAI(model_name="gpt-4", temperature=0.7)


# Define the manager agent
manager = Agent(
    role="Project Manager",
    goal="Efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
)

task = Task(
    description="Generate a list of 5 interesting ideas for an article, then write one captivating paragraph for each idea that showcases the potential of a full article on this topic. Return the list of ideas with their paragraphs and your notes.",
    expected_output="5 bullet points, each with a paragraph and accompanying notes.",
)

researcher = Agent(
    role="Researcher",
    goal="Conduct thorough research and analysis on AI and AI agents",
    backstory="You're an expert researcher, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently researching for a new client.",
    allow_delegation=False,
)

writer = Agent(
    role="Senior Writer",
    goal="Create compelling content about AI and AI agents",
    backstory="You're a senior writer, specialized in technology, software engineering, AI, and startups. You work as a freelancer and are currently writing content for a new client.",
    allow_delegation=False,
)

# Instantiate your crew with a custom manager
def second_chatbot():
    crew = Crew(
        agents=[researcher, writer],
        tasks=[task],
        manager_agent=manager,
        process=Process.hierarchical,
    )
    result = crew.kickoff()
    return result