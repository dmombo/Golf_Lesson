import streamlit as st
import pandas as pd
from pathlib import Path

# Base directory where this script lives
def get_base_dir():
    return Path(__file__).parent

# Discover available lesson folders (each containing a CSV and videos), ignoring virtualenv directories
def find_lessons(base_dir: Path):
    excluded = {"venv", ".venv"}
    return [d for d in base_dir.iterdir() if d.is_dir() and d.name not in excluded]

@st.cache_data
def load_data(csv_path: Path) -> pd.DataFrame:
    """Load CSV data with Windows-1252 encoding."""
    return pd.read_csv(csv_path, encoding='windows-1252')


def main():
    st.title("Golf Launch Monitor Viewer")
    base_dir = get_base_dir()

    # Lesson selection
    lessons = find_lessons(base_dir)
    lesson_names = [lesson.name for lesson in lessons]
    selected_lesson = st.sidebar.selectbox("Select Lesson Folder", lesson_names)
    lesson_dir = base_dir / selected_lesson

    # Load CSV file
    csv_files = list(lesson_dir.glob('*.csv'))
    if not csv_files:
        st.error(f"No CSV file found in {lesson_dir}")
        return
    df = load_data(csv_files[0])

    # Columns to preview in table
    preview_cols = ['Player', 'Time', 'Club', "Club Speed [mph]",'Shot Type', 'Carry [yds]', 'Radar Video']

    # Create tabs for shots table and video player
    tab_all, tab_video = st.tabs(["All Shots", "Video Player"])

    with tab_all:
        st.subheader(f"All Shots: {csv_files[0].name}")
        st.dataframe(df[preview_cols])

    with tab_video:
        st.subheader("Select a Shot to Play Video")

        # Formatter for selectbox
        def format_shot(idx):
            row = df.loc[idx]
            return f"{idx}: {row['Club']} | {row['Shot Type']} | Carry {row['Carry [yds]']} yd"

        selected_idx = st.selectbox(
            "Choose shot by index:", df.index.tolist(), format_func=format_shot
        )
        row = df.loc[selected_idx]

        # Desired metrics to display
        desired_metrics = [
            "Index",
            "Carry [yds]",
            "Total [yds]",
            "Smash",
            "Spin [rpm]",
            "Club Path [deg]",
            "V-Plane [deg]",
            "Height [ft]",
            "Club Speed [mph]",
            "AOA [deg]",
            "Low Point [in]",
            "Club",
            "Shot Type"
        ]
        # Build metrics dict in order
        metrics = {"Index": selected_idx}
        for col in desired_metrics[1:]:
            metrics[col] = row.get(col, "N/A")

        # Display metrics in up to 8 columns per row with smaller, uniform font
        st.subheader("Shot Metrics")
        items = list(metrics.items())
        n_cols = 8
        for i in range(0, len(items), n_cols):
            cols = st.columns(n_cols)
            for j, (label, value) in enumerate(items[i:i+n_cols]):
                # Render label and value with custom markdown styling
                markdown_str = (
                    f"<div style='text-align:center;'>"
                    f"<div style='font-size:0.8rem;color:#666;'>{label}</div>"
                    f"<div style='font-size:1rem;font-weight:bold;'>{value}</div>"
                    f"</div>"
                )
                cols[j].markdown(markdown_str, unsafe_allow_html=True)

        # Play the video
        video_file = lesson_dir / row['Radar Video']
        if video_file.exists():
            st.video(str(video_file))
        else:
            st.error(f"Video not found: {video_file}")

if __name__ == '__main__':
    main()

