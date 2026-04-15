import os
import json
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# Set up the page
st.title("Lab 09: Multi-Agent Trip Planner")
st.write("A Supervisor agent coordinates three specialist agents — Research, Budget, and Itinerary — to collaboratively plan a trip.")

# Load the OpenAI API key
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# Create two ChatOpenAI instances
agent_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
supervisor_llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)

# Load the travel data
with open('travel_data.json', 'r') as f:
    TRAVEL_DATA = json.load(f)

@tool
def search_destination(query: str) -> str:
    """Look up travel info about a destination. Returns highlights, best time to visit, culture tips, and weather for the requested city."""
    for city, info in TRAVEL_DATA["destinations"].items():
        if city.lower() in query.lower():
            return json.dumps({city: info})
    return json.dumps({
        "message": "Destination not found in database. Available destinations: " + ", ".join(TRAVEL_DATA["destinations"].keys())
    })

@tool
def calculate_budget(destination: str, days: int, budget_level: str) -> str:
    """Estimate trip costs for a destination. Takes the city name, number of days, and budget level (budget, moderate, or luxury). Returns a cost breakdown including flights, accommodation, food, transport, activities, and money-saving tips."""
    daily_costs = TRAVEL_DATA["daily_costs"].get(budget_level.lower(), TRAVEL_DATA["daily_costs"]["moderate"])
    
    flight_cost = 0
    for city in TRAVEL_DATA["flight_estimates"]:
        if city.lower() in destination.lower():
            flight_cost = TRAVEL_DATA["flight_estimates"][city]
            break
    
    total_accommodation = daily_costs["accommodation"] * days
    total_food = daily_costs["food"] * days
    total_transport = daily_costs["transport"] * days
    total_activities = daily_costs["activities"] * days
    total_misc = daily_costs["misc"] * days
    total_daily = total_accommodation + total_food + total_transport + total_activities + total_misc
    grand_total = total_daily + flight_cost
    
    result = {
        "destination": destination,
        "days": days,
        "budget_level": budget_level,
        "flight_cost": flight_cost,
        "daily_breakdown": daily_costs,
        "total_daily_costs": total_daily,
        "grand_total": grand_total,
        "money_saving_tips": TRAVEL_DATA["money_saving_tips"]
    }
    return json.dumps(result)

@tool
def create_schedule(destination: str, days: int, interests: str) -> str:
    """Build a day-by-day itinerary for a trip. Takes the city name, number of days, and a comma-separated string of interests (e.g. 'Food, History, Art'). Returns a schedule with morning, afternoon, and evening slots for each day."""
    interest_list = [i.strip().lower() for i in interests.split(",")]
    
    matching_activities = []
    for category, activities in TRAVEL_DATA["activities"].items():
        if category.lower() in interest_list:
            matching_activities.extend(activities)
    
    if not matching_activities:
        for activities in TRAVEL_DATA["activities"].values():
            matching_activities.extend(activities)
    
    schedule = {}
    activity_index = 0
    for day in range(1, days + 1):
        day_plan = {}
        for slot in ["morning", "afternoon", "evening"]:
            if activity_index < len(matching_activities):
                day_plan[slot] = matching_activities[activity_index]
                activity_index += 1
            else:
                activity_index = 0
                day_plan[slot] = matching_activities[activity_index]
                activity_index += 1
        schedule[f"Day {day}"] = day_plan
    
    result = {
        "destination": destination,
        "days": days,
        "interests": interest_list,
        "schedule": schedule
    }
    return json.dumps(result)

# Create the three specialist agents
research_agent = create_react_agent(
    model=agent_llm,
    tools=[search_destination],
    name='research_agent',
    prompt='You are a travel research specialist. Always use the search_destination tool to look up information. Never make up information — only use what the tool returns.'
)

budget_agent = create_react_agent(
    model=agent_llm,
    tools=[calculate_budget],
    name='budget_agent',
    prompt='You are a budget specialist for trip planning. Always use the calculate_budget tool to estimate costs. Never make up numbers — only use what the tool returns.'
)

itinerary_agent = create_react_agent(
    model=agent_llm,
    tools=[create_schedule],
    name='itinerary_agent',
    prompt='You are an itinerary specialist. Always use the create_schedule tool to build day-by-day plans. Never make up activities — only use what the tool returns.'
)

# Create the Supervisor
workflow = create_supervisor(
    agents=[research_agent, budget_agent, itinerary_agent],
    model=supervisor_llm,
    prompt=(
        "You are a trip planning supervisor coordinating three specialist agents. "
        "You have these agents available:\n"
        "- research_agent: handles destination questions (highlights, culture, weather)\n"
        "- budget_agent: handles cost and budget questions\n"
        "- itinerary_agent: handles schedule and itinerary questions\n\n"
        "Route questions as follows:\n"
        "- Destination questions → research_agent\n"
        "- Cost/budget questions → budget_agent\n"
        "- Schedule/itinerary questions → itinerary_agent\n"
        "- Full trip planning → ALL three agents\n\n"
        "Synthesize all responses into one organized plan."
    )
)

# Compile the workflow
multi_agent_app = workflow.compile()

# Session state for storing results
if 'ma_result' not in st.session_state:
    st.session_state.ma_result = None
if 'ma_messages' not in st.session_state:
    st.session_state.ma_messages = None

# Sidebar controls
with st.sidebar:
    destination = st.text_input("Destination", value="Paris")
    days = st.slider("Trip Duration (days)", 1, 14, 5)
    budget_level = st.selectbox("Budget Level", ["Budget", "Moderate", "Luxury"])
    interests = st.multiselect("Interests", ["Food", "History", "Art", "Nature", "Adventure", "Shopping", "Nightlife"])

# Build the query string from sidebar inputs
interests_str = ", ".join(interests) if interests else "General sightseeing"
trip_query = f"Plan a {days}-day trip to {destination}. My budget level is {budget_level.lower()}. My interests include: {interests_str}. Please provide destination research, a budget breakdown, and a day-by-day itinerary."

# Plan My Trip button
if st.button("Plan My Trip", type="primary"):
    with st.spinner("Planning your trip... This may take a moment."):
        result = multi_agent_app.invoke({
            'messages': [{'role': 'user', 'content': trip_query}]
        })
        st.session_state.ma_result = result
        st.session_state.ma_messages = result['messages']

# Display the result
if st.session_state.ma_result:
    st.markdown(st.session_state.ma_result['messages'][-1].content)

