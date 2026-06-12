import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from goaliescout.data.database import GoalieDatabase
from goaliescout.ai.services import OpenAIService

st.set_page_config(
    page_title="GoalieScout Decision Support",
    page_icon="GS",
    layout="wide",
)

st.title("GoalieScout Decision Support")
st.caption(
    "Evidence-first goalie evaluation with AI-assisted interpretation and "
    "explicit human-review boundaries."
)

with st.sidebar:
    st.header("Demo controls")
    player_id = st.text_input("Player ID", value="hellebuyck_37")
    generate_report = st.button(
        "Generate grounded report",
        type="primary",
        width="stretch",
    )
    st.info(
        "Portfolio alpha: the demo uses a curated sample dataset. "
        "It is not a live NHL statistics service."
    )

if generate_report:
    if not player_id.strip():
        st.warning("Please enter a Player ID.")
    else:
        db = GoalieDatabase("data/sample_database.json")
        goalie = db.get_goalie(player_id.strip())

        if goalie is None:
            st.error(f"No goalie found for Player ID: {player_id}")
        else:
            profile_data = (
                goalie.to_dict()
                if hasattr(goalie, "to_dict")
                else goalie.__dict__
            )
            demographics = profile_data.get("demographics", {})
            metrics = profile_data.get("performance_metrics", [])
            latest = metrics[-1] if metrics else {}
            analysis = profile_data.get("ai_analysis") or {}

            st.header(demographics.get("name", "Unknown goalie"))
            st.caption(
                f"{profile_data.get('current_team', 'Unknown team')} | "
                f"{profile_data.get('league', 'Unknown league')} | "
                f"Dataset updated {profile_data.get('last_updated', 'Unknown')}"
            )

            overview_columns = st.columns(5)
            overview_columns[0].metric(
                "Season",
                latest.get("season", "N/A"),
            )
            overview_columns[1].metric(
                "Games",
                latest.get("games_played", "N/A"),
            )
            overview_columns[2].metric(
                "Record",
                (
                    f"{latest.get('wins', 0)}-"
                    f"{latest.get('losses', 0)}-"
                    f"{latest.get('overtime_losses', 0)}"
                ),
            )
            overview_columns[3].metric(
                "Save %",
                (
                    f"{latest.get('save_percentage', 0):.3f}"
                    if latest
                    else "N/A"
                ),
            )
            overview_columns[4].metric(
                "GAA",
                (
                    f"{latest.get('goals_against_average', 0):.2f}"
                    if latest
                    else "N/A"
                ),
            )

            evidence_tab, context_tab, methods_tab = st.tabs(
                ["Evidence", "Evaluation context", "Method and limits"]
            )

            with evidence_tab:
                left, right = st.columns(2)
                with left:
                    st.subheader("Season record")
                    if latest:
                        st.dataframe(
                            [{
                                "Season": latest.get("season"),
                                "GP": latest.get("games_played"),
                                "W": latest.get("wins"),
                                "L": latest.get("losses"),
                                "OTL": latest.get("overtime_losses"),
                                "SV%": latest.get("save_percentage"),
                                "GAA": latest.get("goals_against_average"),
                                "SO": latest.get("shutouts"),
                            }],
                            hide_index=True,
                            width="stretch",
                        )
                    else:
                        st.warning("No season statistics are available.")
                with right:
                    st.subheader("Notable achievements")
                    achievements = profile_data.get(
                        "notable_achievements", []
                    )
                    if achievements:
                        for achievement in achievements:
                            st.markdown(f"- {achievement}")
                    else:
                        st.write("No achievements are recorded.")

                st.subheader("Sources")
                for source in profile_data.get("data_sources", []):
                    st.markdown(f"- {source}")

            with context_tab:
                st.warning(
                    "The items below are curated scouting interpretations. "
                    "They are not direct measurements unless a metric is shown."
                )
                rating_col, role_col = st.columns(2)
                rating_col.metric(
                    "Curated rating",
                    (
                        f"{analysis.get('overall_rating')}/100"
                        if analysis.get("overall_rating") is not None
                        else "N/A"
                    ),
                )
                role_col.metric(
                    "Role assessment",
                    analysis.get("nhl_readiness", "Not assessed"),
                )
                strengths_col, risks_col = st.columns(2)
                with strengths_col:
                    st.subheader("Interpreted strengths")
                    for strength in analysis.get("strengths", []):
                        st.markdown(f"- {strength}")
                with risks_col:
                    st.subheader("Risks and questions")
                    for weakness in analysis.get("weaknesses", []):
                        st.markdown(f"- {weakness}")

            with methods_tab:
                st.markdown(
                    """
                    **What the AI may do**

                    - Summarize supplied statistics and curated context
                    - Separate evidence from interpretation
                    - Recommend follow-up questions for a human scout

                    **What the AI may not do**

                    - Invent current statistics, awards, injuries, or traits
                    - Treat mental or technical observations as measured facts
                    - Replace video review, medical evaluation, or judgment
                    """
                )

            with st.spinner("Generating AI scouting report..."):
                ai_service = OpenAIService()
                report = ai_service.generate_scouting_report(profile_data)

            st.subheader("Grounded AI Report")
            st.markdown(report)
            st.download_button(
                "Download report",
                data=report,
                file_name=f"{player_id.strip()}_grounded_report.md",
                mime="text/markdown",
            )
