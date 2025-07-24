import os
from dotenv import load_dotenv
import streamlit as st
import asyncio 
from roadmap_tool import get_career_roadmap
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.run import RunConfig
import nest_asyncio 
nest_asyncio.apply() 

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

async def run_agents(interest):
    result1 = await Runner.run(career_agent, interest, run_config=config)
    field = result1.final_output.strip()

    result2 = await Runner.run(skill_agent, field, run_config=config)
    skills = result2.final_output.strip()

    result3 = await Runner.run(job_agent, field, run_config=config)
    jobs = result3.final_output.strip()

    return field, skills, jobs

# Page Config
st.set_page_config(page_title="🎓 Career Mentor", page_icon="🎓", layout="wide")

st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        .main-title {font-size: 2rem; font-weight: bold; color: #1e3a8a; text-align: center;}
        .result-box {padding: 20px; border-radius: 12px; margin: 10px 0;}
        .career {background-color: #dbeafe; color: #1e40af;}
        .skills {background-color: #dcfce7; color: #166534;}
        .jobs {background-color: #fee2e2; color: #991b1b;}
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #e0f2fe 0%, #fdf2f8 100%);
        }
        [data-testid="stSidebar"] {
            background-color: #1e3a8a;
            color: white;
        }
        [data-testid="stSidebar"] * {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.sidebar.title("⚙️ Career Mentor Options")
st.sidebar.write("This AI agent helps you explore careers, skills, and job opportunities.")
st.sidebar.info("Tip: Enter something like **AI, Design, Finance** as your interest!")

st.markdown("<h1 class='main-title'>🎓 Career Mentor Agent</h1>", unsafe_allow_html=True)

with st.form("career_form"):
    interest = st.text_input("💬 What are your interests?")
    submitted = st.form_submit_button("Find My Career Path")

if submitted and interest:
    with st.spinner("🤖 Thinking..."):
        field, skills, jobs = asyncio.get_event_loop().run_until_complete(run_agents(interest))

    st.markdown(f"<div class='result-box career'>📌 <b>Suggested Career:</b> {field}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-box skills'>📝 <b>Required Skills:</b><br>{skills}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='result-box jobs'>💼 <b>Possible Jobs:</b><br>{jobs}</div>", unsafe_allow_html=True)


