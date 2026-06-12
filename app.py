import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from goaliescout.ai.services import OpenAIService
from goaliescout.analytics.decision_support import (
    COMPONENT_LABELS,
    DEMO_CANDIDATES,
    SCENARIO_WEIGHTS,
    build_decision_brief,
    build_sensitivity_rows,
    normalize_weights,
    rank_candidates,
)
from goaliescout.data.database import GoalieDatabase


st.set_page_config(
    page_title="GoalieScout Decision Support",
    page_icon="GS",
    layout="wide",
)

st.title("GoalieScout Decision Support")
st.caption(
    "Evidence-first goalie evaluation, transparent scoring, and accountable "
    "human review."
)

page = st.sidebar.radio(
    "Workspace",
    ["Decision Room", "Grounded Report", "Product Case Study"],
)
st.sidebar.info(
    "Portfolio alpha. Real-player records and illustrative decision packets "
    "are clearly separated throughout the product."
)


def render_grounded_report():
    st.header("Grounded Player Report")
    st.write(
        "Inspect the stored evidence before generating AI-assisted "
        "interpretation."
    )
    player_id = st.text_input("Player ID", value="hellebuyck_37")
    generate_report = st.button(
        "Generate grounded report",
        type="primary",
        width="stretch",
    )

    if not generate_report:
        return
    if not player_id.strip():
        st.warning("Please enter a Player ID.")
        return

    goalie = GoalieDatabase("data/sample_database.json").get_goalie(
        player_id.strip()
    )
    if goalie is None:
        st.error(f"No goalie found for Player ID: {player_id}")
        return

    profile_data = goalie.to_dict()
    demographics = profile_data.get("demographics", {})
    metrics = profile_data.get("performance_metrics", [])
    latest = metrics[-1] if metrics else {}
    analysis = profile_data.get("ai_analysis") or {}

    st.subheader(demographics.get("name", "Unknown goalie"))
    st.caption(
        f"{profile_data.get('current_team', 'Unknown team')} | "
        f"{profile_data.get('league', 'Unknown league')} | "
        f"Dataset updated {profile_data.get('last_updated', 'Unknown')}"
    )

    overview_columns = st.columns(5)
    overview_columns[0].metric("Season", latest.get("season", "N/A"))
    overview_columns[1].metric("Games", latest.get("games_played", "N/A"))
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
        f"{latest.get('save_percentage', 0):.3f}" if latest else "N/A",
    )
    overview_columns[4].metric(
        "GAA",
        f"{latest.get('goals_against_average', 0):.2f}" if latest else "N/A",
    )

    evidence_tab, context_tab, methods_tab = st.tabs(
        ["Evidence", "Evaluation context", "Method and limits"]
    )
    with evidence_tab:
        left, right = st.columns(2)
        with left:
            st.subheader("Season record")
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
        with right:
            st.subheader("Notable achievements")
            for achievement in profile_data.get("notable_achievements", []):
                st.markdown(f"- {achievement}")
        st.subheader("Sources")
        for source in profile_data.get("data_sources", []):
            st.markdown(f"- {source}")

    with context_tab:
        st.warning(
            "These are curated interpretations, not direct measurements "
            "unless a metric is shown."
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
            **The AI may**

            - Summarize supplied statistics and curated context
            - Separate evidence from interpretation
            - Recommend follow-up questions for a human scout

            **The AI may not**

            - Invent current statistics, awards, injuries, or traits
            - Treat mental or technical observations as measured facts
            - Replace video review, medical evaluation, or judgment
            """
        )

    with st.spinner("Generating evidence-grounded report..."):
        report = OpenAIService().generate_scouting_report(profile_data)

    st.subheader("Grounded AI Report")
    st.markdown(report)
    st.download_button(
        "Download report",
        data=report,
        file_name=f"{player_id.strip()}_grounded_report.md",
        mime="text/markdown",
    )


def render_decision_room():
    st.header("Decision Room")
    st.write(
        "Compare anonymized candidates, change organizational priorities, "
        "test ranking stability, and record human approval."
    )
    st.warning(
        "The three candidate packets are illustrative portfolio data, not "
        "evaluations of real players."
    )

    controls, results = st.columns([1, 2], gap="large")
    with controls:
        st.subheader("1. Set the decision")
        scenario = st.selectbox(
            "Evaluation scenario",
            list(SCENARIO_WEIGHTS),
        )
        st.caption(
            "Start with a documented preset, then adjust priorities. "
            "Weights are normalized automatically."
        )
        base_weights = SCENARIO_WEIGHTS[scenario]
        raw_weights = {}
        for key, label in COMPONENT_LABELS.items():
            raw_weights[key] = st.slider(
                label,
                min_value=0,
                max_value=50,
                value=int(round(base_weights[key] * 100)),
                step=5,
                key=f"weight_{scenario}_{key}",
            )
        weights = normalize_weights(raw_weights)
        st.caption(
            "Normalized total: "
            f"{sum(weights.values()) * 100:.0f}%"
        )

    rankings = rank_candidates(DEMO_CANDIDATES, weights)
    leader = rankings[0]

    with results:
        st.subheader("2. Review the recommendation")
        leader_col, confidence_col, completeness_col = st.columns(3)
        leader_col.metric("Recommended candidate", leader["name"])
        confidence_col.metric(
            "GoalieScout score",
            f"{leader['black_ops_score']:.2f}/100",
        )
        completeness_col.metric(
            "Data completeness",
            f"{leader['data_completeness'] * 100:.0f}%",
        )

        ranking_rows = [{
            "Rank": position,
            "Candidate": item["name"],
            "Role": item["role"],
            "Score": item["black_ops_score"],
            "Tier": item["tier"],
            "Completeness": f"{item['data_completeness'] * 100:.0f}%",
            "95% interval": (
                f"{item['confidence_interval']['lower']:.1f}-"
                f"{item['confidence_interval']['upper']:.1f}"
            ),
        } for position, item in enumerate(rankings, start=1)]
        st.dataframe(ranking_rows, hide_index=True, width="stretch")

        chart_data = pd.DataFrame(
            {
                item["name"]: item["component_scores"]
                for item in rankings
            }
        )
        st.caption(
            "Normalized component scores. Missing evidence is neutrally "
            "imputed at 50 and remains visible in completeness."
        )
        st.bar_chart(chart_data)

    evidence_tab, sensitivity_tab, review_tab, governance_tab = st.tabs(
        [
            "Evidence packets",
            "Ranking sensitivity",
            "Human approval",
            "Model governance",
        ]
    )

    with evidence_tab:
        for item in rankings:
            with st.expander(
                f"{item['name']} | {item['role']} | "
                f"{item['black_ops_score']:.2f}"
            ):
                st.caption(item["sample"])
                left, right = st.columns(2)
                with left:
                    st.markdown("**Supporting evidence**")
                    for evidence in item["evidence"]:
                        st.markdown(f"- {evidence}")
                with right:
                    st.markdown("**Open questions**")
                    for question in item["open_questions"]:
                        st.markdown(f"- {question}")

    with sensitivity_tab:
        sensitivity_rows = build_sensitivity_rows(DEMO_CANDIDATES)
        sensitivity_frame = pd.DataFrame(sensitivity_rows)
        winners = sensitivity_frame[sensitivity_frame["Rank"] == 1]
        winner_counts = winners["Candidate"].value_counts()
        stable_winner = winner_counts.index[0]
        stable_count = int(winner_counts.iloc[0])
        st.metric(
            "Most scenario-resilient candidate",
            stable_winner,
            f"Ranks first in {stable_count} of {len(SCENARIO_WEIGHTS)} presets",
        )
        st.dataframe(
            sensitivity_frame,
            hide_index=True,
            width="stretch",
        )
        st.caption(
            "A recommendation that changes across scenarios is not a model "
            "failure. It signals that stakeholder priorities materially affect "
            "the decision."
        )

    with review_tab:
        st.subheader("3. Complete accountable human review")
        evidence_reviewed = st.checkbox(
            "Evidence packet and source labels reviewed"
        )
        video_reviewed = st.checkbox(
            "Video review completed for technical claims"
        )
        medical_reviewed = st.checkbox(
            "Medical and availability review completed"
        )
        freshness_reviewed = st.checkbox(
            "Data freshness and sample size accepted"
        )
        review_status = {
            "Evidence packet and source labels reviewed": evidence_reviewed,
            "Video review completed for technical claims": video_reviewed,
            "Medical and availability review completed": medical_reviewed,
            "Data freshness and sample size accepted": freshness_reviewed,
        }
        completed = sum(review_status.values())
        st.progress(completed / len(review_status))
        if completed == len(review_status):
            st.success("Human review complete. Decision brief may be approved.")
        else:
            st.info(
                f"{completed} of {len(review_status)} approval gates complete."
            )

        decision_brief = build_decision_brief(
            scenario,
            rankings,
            weights,
            review_status,
        )
        st.download_button(
            "Export executive decision brief",
            data=decision_brief,
            file_name="goaliescout_decision_brief.md",
            mime="text/markdown",
            width="stretch",
        )

    with governance_tab:
        average_completeness = sum(
            item["data_completeness"] for item in rankings
        ) / len(rankings)
        missing_count = sum(
            1
            for candidate in DEMO_CANDIDATES
            for value in candidate["inputs"].values()
            if value is None
        )
        metric_columns = st.columns(4)
        metric_columns[0].metric(
            "Candidates evaluated",
            len(rankings),
        )
        metric_columns[1].metric(
            "Average completeness",
            f"{average_completeness * 100:.0f}%",
        )
        metric_columns[2].metric(
            "Neutral imputations",
            missing_count,
        )
        metric_columns[3].metric(
            "Scenario tests",
            len(SCENARIO_WEIGHTS),
        )
        st.markdown(
            """
            **Controls demonstrated**

            - Explicit separation of real records and illustrative demo packets
            - Visible data completeness and neutral missing-value treatment
            - Adjustable priorities with normalized weights
            - Scenario sensitivity rather than false certainty
            - Human approval gates before a decision is considered complete
            - Exportable decision record with model and evidence limitations
            """
        )
        st.code(
            "score = sum(normalized_component * stakeholder_weight)\n"
            "missing_component = neutral_score(50)\n"
            "decision = model_output + sensitivity + human_review",
            language="text",
        )


def render_case_study():
    st.header("Product Case Study")
    problem, solution, measurement = st.columns(3)
    with problem:
        st.subheader("User problem")
        st.write(
            "Scouts must reconcile statistics, technical observations, "
            "organizational priorities, and incomplete evidence under time "
            "pressure."
        )
    with solution:
        st.subheader("Product hypothesis")
        st.write(
            "A transparent decision workspace can reduce synthesis time while "
            "keeping human judgment and evidence boundaries visible."
        )
    with measurement:
        st.subheader("Success measures")
        st.write(
            "Time to comparison, report approval rate, disputed-claim rate, "
            "data completeness, ranking stability, and reviewer corrections."
        )

    st.subheader("System flow")
    st.code(
        "data sources -> normalization -> validation -> persistence\n"
        "             -> analytics -> scenario scoring\n"
        "             -> AI interpretation -> human approval -> decision brief",
        language="text",
    )

    left, right = st.columns(2)
    with left:
        st.subheader("Product decisions")
        st.markdown(
            """
            - Missing values remain visible instead of being hidden
            - Scenario weights are treated as hypotheses
            - AI prose is downstream of structured evidence
            - Review gates prevent unapproved automation
            - Illustrative data is never presented as real-player evidence
            """
        )
    with right:
        st.subheader("Next validated steps")
        st.markdown(
            """
            - Interview scouts and hockey operations staff
            - Measure baseline report-preparation time
            - Add authenticated reviewer roles and audit persistence
            - Calibrate scoring against broader historical datasets
            - Add live-source contracts and production observability
            """
        )


if page == "Decision Room":
    render_decision_room()
elif page == "Grounded Report":
    render_grounded_report()
else:
    render_case_study()
