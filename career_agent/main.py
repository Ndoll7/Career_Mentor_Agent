import os
from dotenv import load_dotenv
import streamlit as st
import asyncio
import nest_asyncio  
from roadmap_tool import get_career_roadmap
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig

nest_asyncio.apply() 

# Load API Key
load_dotenv()
external_client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

# Define agents
career_agent = Agent(
    name="CareerAgent",
    instructions="You ask about interests and suggest a career field.",
    model=model
)

skill_agent = Agent(
    name="SkillAgent",
    instructions="You share the roadmap using the get_career_roadmap tool.",
    model=model,
    tools=[get_career_roadmap]
)

job_agent = Agent(
    name="JobAgent",
    instructions="You suggest job titles in the chosen career.",
    model=model
)

# --- Streamlit UI ---
async def run_agents(interest):
    result1 = await Runner.run(career_agent, interest, run_config=config)
    field = result1.final_output.strip()

    result2 = await Runner.run(skill_agent, field, run_config=config)
    skills = result2.final_output.strip()

    result3 = await Runner.run(job_agent, field, run_config=config)
    jobs = result3.final_output.strip()

    return field, skills, jobs

# Streamlit UI
st.set_page_config(page_title="🎓 Career Mentor", page_icon="🎓")
st.title("🎓 Career Mentor Agent")

with st.form("career_form"):
    interest = st.text_input("💬 What are your interests?")
    submitted = st.form_submit_button("Find My Career Path")

if submitted and interest:
    with st.spinner("🤖 Thinking..."):
        field, skills, jobs = asyncio.get_event_loop().run_until_complete(run_agents(interest))

    st.success(f"📌 **Suggested Career**: {field}")
    st.info(f"📝 **Required Skills**:\n{skills}")
    st.warning(f"💼 **Possible Jobs**:\n{jobs}")


