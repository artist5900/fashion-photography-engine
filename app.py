import json
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

import planner
from plan_to_prompts import markdown_for_plan


CAMPAIGN_TYPES = ["lookbook", "campaign", "ecommerce", "social"]


def brand_options() -> list[dict[str, str]]:
    brands = []
    for record in planner.load_records("brands"):
        brands.append({
            "id": str(record.get("id")),
            "name": str(record.get("name", record.get("id"))),
        })
    return sorted(brands, key=lambda brand: brand["name"])


def json_download(data: dict) -> str:
    return json.dumps(data, indent=2)


def render_recommendation(recommendation: dict) -> None:
    rank = recommendation.get("rank")
    shot = recommendation.get("shot", {})
    pose = recommendation.get("pose", {})
    lens = recommendation.get("lens", {})
    scene = recommendation.get("scene", {})

    with st.container(border=True):
        st.subheader(f"{rank}. {shot.get('name', shot.get('id', 'Shot'))}")
        st.write(recommendation.get("reason", ""))

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Pose:** {pose.get('name', 'Unknown')}")
            st.caption(pose.get("direction", ""))
            st.markdown(f"**Lens:** {lens.get('name', 'Unknown')}")
        with col2:
            st.markdown(f"**Scene:** {scene.get('name', 'Unknown')}")
            st.markdown(f"**Lighting:** {recommendation.get('lighting', 'Unknown')}")


def main() -> None:
    st.set_page_config(
        page_title="Fashion Photography Engine",
        layout="wide",
    )

    st.title("Fashion Photography Engine")
    st.write("Create a ranked fashion photography shot plan and export production-ready prompts.")

    brands = brand_options()
    brand_labels = {f"{brand['name']} ({brand['id']})": brand["id"] for brand in brands}

    with st.sidebar:
        st.header("Lookbook Inputs")
        garment = st.text_area(
            "Garment description",
            value=(
                "oversized black washed denim jacket with button front, point collar, "
                "chest pockets, panel seams, frayed cuff detail, and boxy silhouette"
            ),
            height=160,
        )
        brand_label = st.selectbox("Brand style", options=list(brand_labels.keys()))
        campaign_type = st.selectbox("Campaign type", options=CAMPAIGN_TYPES)
        shot_count = st.slider("Shot count", min_value=1, max_value=12, value=6)

        generate_plan = st.button("Generate Lookbook Plan", type="primary")
        generate_prompts = st.button(
            "Generate Prompts",
            disabled="lookbook_plan" not in st.session_state,
        )

    if generate_plan:
        request = {
            "garment": garment,
            "brand_style": brand_labels[brand_label],
            "campaign_type": campaign_type,
            "count": shot_count,
        }
        st.session_state.lookbook_request = request
        st.session_state.lookbook_plan = planner.build_plan(request)
        st.session_state.pop("lookbook_prompts", None)

    if generate_prompts and "lookbook_plan" in st.session_state:
        st.session_state.lookbook_prompts = markdown_for_plan(st.session_state.lookbook_plan)

    if "lookbook_plan" not in st.session_state:
        st.info("Enter a garment description, choose a brand style and campaign type, then generate a lookbook plan.")
        return

    st.header("Ranked Shot Plan")
    for recommendation in st.session_state.lookbook_plan.get("recommendations", []):
        render_recommendation(recommendation)

    st.header("Downloads")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            "Download lookbook_request.json",
            data=json_download(st.session_state.lookbook_request),
            file_name="lookbook_request.json",
            mime="application/json",
        )
    with col2:
        st.download_button(
            "Download lookbook_plan.json",
            data=json_download(st.session_state.lookbook_plan),
            file_name="lookbook_plan.json",
            mime="application/json",
        )
    with col3:
        prompts = st.session_state.get("lookbook_prompts", "")
        st.download_button(
            "Download lookbook_prompts.md",
            data=prompts,
            file_name="lookbook_prompts.md",
            mime="text/markdown",
            disabled=not prompts,
        )

    if "lookbook_prompts" in st.session_state:
        st.header("Production Prompts")
        st.markdown(st.session_state.lookbook_prompts)


if __name__ == "__main__":
    main()
