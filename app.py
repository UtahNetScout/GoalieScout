import os
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from goaliescout.data.database import GoalieDatabase
from goaliescout.ai.services import OpenAIService


st.title("GoalieScout AI Demo")

st.write("Try searching for Player ID: hellebuyck_37")

player_id = st.text_input("Player ID")

if st.button("Generate AI Scouting Report"):
    if not player_id.strip():
        st.warning("Please enter a Player ID.")
    else:
        db = GoalieDatabase("data/sample_database.json")
        goalie = db.get_goalie(player_id.strip())

        if goalie is None:
            st.error(f"No goalie found for Player ID: {player_id}")
        else:
            profile_data = goalie.to_dict() if hasattr(goalie, "to_dict") else goalie.__dict__

            with st.spinner("Generating AI scouting report..."):
                ai_service = OpenAIService()
                report = ai_service.generate_scouting_report(profile_data)

            st.subheader("AI Scouting Report")
            st.markdown(report)

st.subheader("Scouting Notes")
st.write(report.get("scouting_notes", "N/A"))
