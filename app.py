import sys
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

sys.path.insert(0, str(SRC))

from goaliescout.data.database import GoalieDatabase
from goaliescout.ai.services import OpenAIService


st.title("GoalieScout AI Demo")

st.write("Try searching for Player ID: hellebuyck_37")

player_id = st.text_input("Player ID")

if st.button("Generate AI Scouting Report"):
    if not player_id:
        st.warning("Please enter a Player ID.")
    else:
        db = GoalieDatabase()
        goalie = db.get_goalie(player_id)

        if goalie is None:
            st.error(f"No goalie found for Player ID: {player_id}")
        else:
            with st.spinner("Generating AI scouting report..."):
                ai_service = OpenAIService()
                report = ai_service.analyze_goalie(goalie)

            st.subheader("AI Scouting Report")
            st.write(report)
