
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "industrialpulse.duckdb"
MANIFEST_PATH = ROOT / "data" / "raw" / "ai4i_manifest.json"
DBT_RUN_RESULTS = ROOT / "target" / "run_results.json"

BG = "#07111D"
PANEL = "#101F30"
PANEL_ALT = "#14283A"
TEAL = "#39E6C4"
CYAN = "#49B9FF"
AMBER = "#FFBD69"
RED = "#FF647C"
TEXT = "#E8F1FA"
MUTED = "#91A6BB"

st.set_page_config(
    page_title="IndustrialPulse | Energy Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------------------------------------
# VISUAL SYSTEM
# ---------------------------------------------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {{
        --bg: {BG};
        --panel: {PANEL};
        --teal: {TEAL};
        --cyan: {CYAN};
        --text: {TEXT};
        --muted: {MUTED};
    }}

    html, body, [class*="css"] {{
        font-family: 'Manrope', sans-serif;
    }}

    .stApp {{
        background:
            radial-gradient(ellipse at 5% 0%, #123448 0%, transparent 36%),
            radial-gradient(ellipse at 95% 10%, #102C35 0%, transparent 30%),
            var(--bg);
        color: var(--text);
    }}

    [data-testid="stHeader"] {{
        background: rgba(7,17,29,0.75);
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #0D1C2B 0%, #08121E 100%);
        border-right: 1px solid #22394B;
    }}

    [data-testid="stSidebar"] * {{
        color: var(--text);
    }}

    .block-container {{
        padding-top: 1.7rem;
        padding-bottom: 3rem;
        max-width: 1600px;
    }}

    .brand {{
        font-size: 1.5rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        color: #FFFFFF;
    }}

    .brand span {{
        color: var(--teal);
    }}

    .eyebrow {{
        font-family: 'DM Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 0.70rem;
        color: var(--teal);
    }}

    .hero {{
        position: relative;
        overflow: hidden;
        padding: 30px 32px;
        border-radius: 22px;
        border: 1px solid #2A5263;
        background: linear-gradient(115deg, #122B3D 0%, #0D1C2C 58%, #12352F 100%);
        margin-bottom: 24px;
    }}

    .hero h1 {{
        font-size: clamp(2rem, 3.5vw, 3.25rem);
        line-height: 1.06;
        letter-spacing: -1.8px;
        margin: 12px 0;
        color: #FFFFFF;
    }}

    .hero p {{
        color: #B5C8D8;
        max-width: 720px;
        font-size: 0.98rem;
        line-height: 1.8;
    }}

    .hero-orb {{
        position: absolute;
        width: 250px;
        height: 250px;
        right: 5%;
        top: -55px;
        border-radius: 50%;
        border: 1px solid #3DDCC3;
        box-shadow: 0 0 45px #25CDAA22, inset 0 0 55px #25CDAA17;
        opacity: 0.7;
    }}

    .hero-orb:after {{
        content: "";
        position: absolute;
        inset: 27px;
        border: 1px dashed #42BFE6;
        border-radius: 50%;
    }}

    .metric-card {{
        background: linear-gradient(145deg, #142638, #0D1B29);
        border: 1px solid #243D50;
        border-radius: 17px;
        padding: 19px 20px;
        min-height: 136px;
        box-shadow: 0 8px 30px #00000012;
    }}

    .metric-label {{
        color: #A8BDCF;
        font-size: 0.78rem;
        font-weight: 600;
        margin-bottom: 11px;
    }}

    .metric-value {{
        color: #F5FAFF;
        font-size: clamp(1.5rem, 2.3vw, 2.2rem);
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1.15;
    }}

    .metric-note {{
        color: var(--teal);
        font-size: 0.72rem;
        margin-top: 9px;
    }}

    .section-title {{
        color: #F4F8FC;
        font-size: 1.16rem;
        font-weight: 800;
        letter-spacing: -0.3px;
        margin-top: 10px;
        margin-bottom: 3px;
    }}

    .section-subtitle {{
        color: var(--muted);
        font-size: 0.82rem;
        margin-bottom: 15px;
    }}

    .status-pill {{
        display: inline-block;
        border: 1px solid #2B776D;
        border-radius: 100px;
        color: #69F1D5;
        background: #143D3A;
        font-family: 'DM Mono', monospace;
        font-size: 0.7rem;
        padding: 6px 10px;
    }}

    .info-panel {{
        background: #102132;
        border: 1px solid #243E52;
        border-radius: 15px;
        padding: 18px 20px;
    }}

    .mono {{
        font-family: 'DM Mono', monospace;
        color: #A7C1D5;
        font-size: 0.76rem;
    }}

    div[data-testid="stMetric"] {{
        background: #102132;
        border: 1px solid #243D50;
        border-radius: 14px;
        padding: 15px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: #A8BDCF;
    }}

    div[data-testid="stMetricValue"] {{
        color: #F4FAFF;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 9px;
        background: #102132;
        border: 1px solid #23394C;
        padding: 9px 17px;
    }}

    .stTabs [aria-selected="true"] {{
        background: #163A3B !important;
        border-color: #39E6C4 !important;
    }}

    div[data-testid="stDataFrame"] {{
        border: 1px solid #243D50;
        border-radius: 12px;
        overflow: hidden;
    }}

    .footer {{
        color: #6F879B;
        font-size: 0.74rem;
        border-top: 1px solid #203446;
        padding-top: 17px;
        margin-top: 35px;
    }}

    @media (max-width: 750px) {{
        .hero {{ padding: 23px 20px; }}
        .hero-orb {{ right: -140px; opacity: 0.3; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------
# DATA ACCESS
# ---------------------------------------------------------

@st.cache_data(show_spinner="Loading industrial observations...")
def load_observations(db_path: str, modified_time: float) -> pd.DataFrame:
    """Load the dbt intermediate model from DuckDB."""

    del modified_time  # Included in cache key to refresh after rebuilds.

    if not Path(db_path).exists():
        raise FileNotFoundError(
            f"DuckDB database not found at {db_path}. "
            "Run the ingestion and dbt pipeline first."
        )

    connection = duckdb.connect(db_path, read_only=True)

    try:
        return connection.execute(
            """
            SELECT *
            FROM main.int_machine_observations
            """
        ).df()
    finally:
        connection.close()


@st.cache_data
def load_mart(db_path: str, modified_time: float) -> pd.DataFrame:
    del modified_time

    connection = duckdb.connect(db_path, read_only=True)

    try:
        return connection.execute(
            """
            SELECT *
            FROM main.mart_maintenance_kpis
            ORDER BY machine_type
            """
        ).df()
    finally:
        connection.close()


def load_json(path: Path) -> dict:
    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def load_dbt_test_status() -> dict:
    """Read the most recent available dbt run-results artifact."""

    result = load_json(DBT_RUN_RESULTS)
    results = result.get("results", [])

    if not results:
        return {
            "available": False,
            "passed": 0,
            "failed": 0,
            "total": 0,
        }

    tests = [
        item for item in results
        if item.get("unique_id", "").startswith("test.")
    ]

    passed = sum(
        item.get("status") == "pass"
        for item in tests
    )

    failed = sum(
        item.get("status") in {"fail", "error"}
        for item in tests
    )

    return {
        "available": bool(tests),
        "passed": int(passed),
        "failed": int(failed),
        "total": len(tests),
    }


# ---------------------------------------------------------
# CHART HELPERS
# ---------------------------------------------------------

def style_chart(fig, height=350):
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Manrope, sans-serif",
            color=TEXT,
            size=11,
        ),
        margin=dict(l=12, r=12, t=35, b=12),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            borderwidth=0,
        ),
        xaxis=dict(
            gridcolor="#23394A",
            zerolinecolor="#23394A",
            linecolor="#23394A",
        ),
        yaxis=dict(
            gridcolor="#23394A",
            zerolinecolor="#23394A",
            linecolor="#23394A",
        ),
        hoverlabel=dict(
            bgcolor="#13283A",
            bordercolor=TEAL,
            font_color=TEXT,
        ),
    )
    return fig


def section_heading(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="section-subtitle">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label, value, note, accent=TEAL):
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 2px solid {accent}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

if not DB_PATH.exists():
    st.error("Local warehouse not found.")
    st.code(
        ".\\.venv\\Scripts\\python.exe -m ingestion.load_local_warehouse\n"
        ".\\.venv\\Scripts\\dbt.exe run"
    )
    st.stop()

db_modified = DB_PATH.stat().st_mtime

try:
    data = load_observations(str(DB_PATH), db_modified)
    mart = load_mart(str(DB_PATH), db_modified)
except Exception as exc:
    st.error(f"Unable to load the dbt models: {exc}")
    st.info("Build the project with `dbt run` and refresh the page.")
    st.stop()

if data.empty:
    st.warning("The intermediate model contains no observations.")
    st.stop()

manifest = load_json(MANIFEST_PATH)
dbt_status = load_dbt_test_status()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand">INDUSTRIAL<span>PULSE</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="mono">ENERGY & ASSET INTELLIGENCE</div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")

    page = st.radio(
        "NAVIGATION",
        [
            "Command Centre",
            "Failure Intelligence",
            "Sensor Laboratory",
            "Data Quality",
            "Data Explorer",
        ],
        label_visibility="visible",
    )

    st.markdown("---")
    st.markdown('<div class="eyebrow">OBSERVATION FILTERS</div>',
                unsafe_allow_html=True)

    available_types = sorted(data["machine_type"].dropna().unique().tolist())

    selected_types = st.multiselect(
        "Machine type",
        available_types,
        default=available_types,
    )

    failure_filter = st.selectbox(
        "Failure status",
        ["All observations", "Failure only", "No recorded failure"],
    )

    wear_min = int(data["tool_wear_min"].min())
    wear_max = int(data["tool_wear_min"].max())

    wear_range = st.slider(
        "Tool wear (minutes)",
        min_value=wear_min,
        max_value=wear_max,
        value=(wear_min, wear_max),
    )

    st.markdown("---")
    st.markdown(
        """
        <div class="mono">
        DATA SOURCE<br>
        UCI AI4I 2020<br><br>
        WAREHOUSE<br>
        DuckDB · Local<br><br>
        TRANSFORMATIONS<br>
        dbt Core + SQL
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Refresh data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()


# ---------------------------------------------------------
# APPLY FILTERS
# ---------------------------------------------------------

filtered = data.copy()

if selected_types:
    filtered = filtered[filtered["machine_type"].isin(selected_types)]
else:
    filtered = filtered.iloc[0:0]

filtered = filtered[
    filtered["tool_wear_min"].between(wear_range[0], wear_range[1])
]

if failure_filter == "Failure only":
    filtered = filtered[filtered["machine_failure"] == 1]
elif failure_filter == "No recorded failure":
    filtered = filtered[filtered["machine_failure"] == 0]

total = len(filtered)
failures = int(filtered["machine_failure"].sum()) if total else 0
failure_rate = failures / total * 100 if total else 0.0
avg_delta = (
    float(filtered["temperature_delta_k"].mean())
    if total else 0.0
)
avg_torque = float(filtered["torque_nm"].mean()) if total else 0.0


# ---------------------------------------------------------
# GLOBAL HEADER
# ---------------------------------------------------------

left, right = st.columns([4, 1])

with left:
    st.markdown(
        '<div class="eyebrow">INDUSTRIAL ANALYTICS PLATFORM / LIVE LOCAL MODEL</div>',
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        '<div style="text-align:right"><span class="status-pill">● WAREHOUSE CONNECTED</span></div>',
        unsafe_allow_html=True,
    )

st.write("")


# ---------------------------------------------------------
# PAGE 1: COMMAND CENTRE
# ---------------------------------------------------------

if page == "Command Centre":

    st.markdown(
        """
        <div class="hero">
            <div class="hero-orb"></div>
            <div class="eyebrow">RELIABILITY · PERFORMANCE · INTELLIGENCE</div>
            <h1>See the signals.<br>Understand the system.</h1>
            <p>
                An interactive maintenance intelligence workspace that transforms
                industrial sensor observations into measurable reliability KPIs,
                supported by a tested dbt transformation pipeline.
            </p>
            <span class="status-pill">● SYNTHETIC RESEARCH DATASET</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if failure_filter != "All observations":
        st.info(
            "KPIs and charts reflect your current failure-status filter. "
            "Select 'All observations' for an overall overview."
        )

    st.markdown('<div class="eyebrow">SYSTEM SNAPSHOT</div>',
                unsafe_allow_html=True)
    st.write("")

    cols = st.columns(4)

    with cols[0]:
        metric_card(
            "OBSERVATIONS",
            f"{total:,}",
            "Records in current selection",
            CYAN,
        )

    with cols[1]:
        metric_card(
            "OBSERVED FAILURES",
            f"{failures:,}",
            f"{failure_rate:.2f}% of selection",
            RED,
        )

    with cols[2]:
        metric_card(
            "AVG TEMPERATURE DELTA",
            f"{avg_delta:.2f} K",
            "Process minus air temperature",
            TEAL,
        )

    with cols[3]:
        metric_card(
            "AVG TORQUE",
            f"{avg_torque:.2f} Nm",
            "Mean sensor torque",
            AMBER,
        )

    st.write("")
    chart_left, chart_right = st.columns([1.2, 1])

    with chart_left:
        section_heading(
            "Failure rate by machine type",
            "Observed failures divided by observations within each type.",
        )

        if total:
            by_type = (
                filtered.groupby("machine_type", as_index=False)
                .agg(
                    observations=("machine_failure", "size"),
                    failures=("machine_failure", "sum"),
                )
            )

            by_type["failure_rate_pct"] = (
                by_type["failures"] / by_type["observations"] * 100
            )

            fig = px.bar(
                by_type,
                x="machine_type",
                y="failure_rate_pct",
                color="failure_rate_pct",
                color_continuous_scale=["#238A8D", TEAL, AMBER, RED],
                text=by_type["failure_rate_pct"].map(lambda x: f"{x:.2f}%"),
                hover_data=["observations", "failures"],
            )
            fig.update_traces(
                textposition="outside",
                marker_line_width=0,
            )
            fig.update_coloraxes(showscale=False)
            fig.update_yaxes(title="Failure rate (%)")
            fig.update_xaxes(title="Machine type")
            st.plotly_chart(style_chart(fig), use_container_width=True)
        else:
            st.info("No observations match the current filters.")

    with chart_right:
        section_heading(
            "Failure-mode signals",
            "Flag counts; multiple flags may occur in one observation.",
        )

        failure_columns = {
            "tool_wear_failure": "Tool wear",
            "heat_dissipation_failure": "Heat dissipation",
            "power_failure": "Power",
            "overstrain_failure": "Overstrain",
            "random_failure": "Random",
        }

        mode_values = pd.DataFrame(
            [
                {
                    "Failure mode": label,
                    "Flag count": int(filtered[column].sum()) if total else 0,
                }
                for column, label in failure_columns.items()
            ]
        ).sort_values("Flag count")

        fig = px.bar(
            mode_values,
            x="Flag count",
            y="Failure mode",
            orientation="h",
            color="Flag count",
            color_continuous_scale=["#1B6475", TEAL],
            text="Flag count",
        )
        fig.update_traces(textposition="outside")
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(style_chart(fig), use_container_width=True)

    st.write("")
    section_heading(
        "Sensor operating envelope",
        "Explore torque against rotational speed; colour shows the recorded failure label.",
    )

    if total:
        fig = px.scatter(
            filtered,
            x="rotational_speed_rpm",
            y="torque_nm",
            color="is_machine_failure",
            color_discrete_map={True: RED, False: TEAL},
            category_orders={"is_machine_failure": [False, True]},
            labels={
                "rotational_speed_rpm": "Rotational speed (RPM)",
                "torque_nm": "Torque (Nm)",
                "is_machine_failure": "Recorded failure",
            },
            hover_data=[
                "source_record_id",
                "machine_type",
                "tool_wear_min",
                "temperature_delta_k",
            ],
            opacity=0.72,
        )
        st.plotly_chart(style_chart(fig, 420), use_container_width=True)

    st.caption(
        "The dataset contains synthetic observations, not live plant telemetry. "
        "No time-series history is available, so the dashboard does not claim "
        "real-time monitoring or forecast future failures."
    )


# ---------------------------------------------------------
# PAGE 2: FAILURE INTELLIGENCE
# ---------------------------------------------------------

elif page == "Failure Intelligence":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">RELIABILITY ENGINEERING</div>
            <h1>Failure Intelligence</h1>
            <p>
                Compare failure observations, inspect failure-mode signals,
                and investigate how operating conditions differ in the
                available synthetic dataset.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("Observations", f"{total:,}")
    c2.metric("Recorded failures", f"{failures:,}")
    c3.metric("Observed failure rate", f"{failure_rate:.2f}%")

    left, right = st.columns(2)

    with left:
        section_heading(
            "Failure rate and sample size",
            "Rates should be interpreted alongside the number of observations.",
        )

        if total:
            type_summary = (
                filtered.groupby("machine_type", as_index=False)
                .agg(
                    observations=("machine_failure", "size"),
                    failures=("machine_failure", "sum"),
                )
            )
            type_summary["rate"] = (
                type_summary["failures"] / type_summary["observations"] * 100
            )

            fig = px.bar(
                type_summary,
                x="machine_type",
                y="rate",
                text=type_summary["rate"].map(lambda x: f"{x:.2f}%"),
                hover_data=["observations", "failures"],
                color="rate",
                color_continuous_scale=["#238A8D", TEAL, RED],
            )
            fig.update_coloraxes(showscale=False)
            fig.update_traces(textposition="outside")
            fig.update_yaxes(title="Failure rate (%)")
            st.plotly_chart(style_chart(fig), use_container_width=True)

    with right:
        section_heading(
            "Recorded failure-mode flags",
            "Flags are not mutually exclusive.",
        )

        if total:
            mode_df = pd.DataFrame(
                [
                    {
                        "Mode": label,
                        "Count": int(filtered[column].sum()),
                    }
                    for column, label in {
                        "tool_wear_failure": "Tool wear",
                        "heat_dissipation_failure": "Heat dissipation",
                        "power_failure": "Power",
                        "overstrain_failure": "Overstrain",
                        "random_failure": "Random",
                    }.items()
                ]
            )

            fig = px.pie(
                mode_df,
                names="Mode",
                values="Count",
                hole=0.62,
                color_discrete_sequence=[
                    TEAL, CYAN, AMBER, RED, "#A38BFF"
                ],
            )
            fig.update_traces(
                textposition="inside",
                textinfo="label+percent",
            )
            st.plotly_chart(style_chart(fig), use_container_width=True)

    section_heading(
        "Failure versus non-failure observations",
        "Sensor distributions help identify patterns for further investigation.",
    )

    if total:
        compare = filtered.copy()
        compare["Outcome"] = compare["machine_failure"].map(
            {0: "No recorded failure", 1: "Recorded failure"}
        )

        sensor_choice = st.selectbox(
            "Sensor metric to compare",
            [
                "torque_nm",
                "rotational_speed_rpm",
                "tool_wear_min",
                "temperature_delta_k",
            ],
            format_func=lambda x: {
                "torque_nm": "Torque (Nm)",
                "rotational_speed_rpm": "Rotational speed (RPM)",
                "tool_wear_min": "Tool wear (minutes)",
                "temperature_delta_k": "Temperature delta (K)",
            }[x],
        )

        fig = px.box(
            compare,
            x="Outcome",
            y=sensor_choice,
            color="Outcome",
            color_discrete_map={
                "No recorded failure": TEAL,
                "Recorded failure": RED,
            },
            points="outliers",
        )
        st.plotly_chart(style_chart(fig, 400), use_container_width=True)

    st.warning(
        "Association is not causation. This exploratory view does not establish "
        "root causes or validate a predictive-maintenance model."
    )


# ---------------------------------------------------------
# PAGE 3: SENSOR LABORATORY
# ---------------------------------------------------------

elif page == "Sensor Laboratory":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">SENSOR ANALYTICS WORKBENCH</div>
            <h1>Explore the signals.</h1>
            <p>
                Select sensor variables, inspect relationships, and compare
                recorded failure outcomes. Use this space to formulate
                hypotheses for later statistical analysis and modelling.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sensor_labels = {
        "air_temperature_k": "Air temperature (K)",
        "process_temperature_k": "Process temperature (K)",
        "temperature_delta_k": "Temperature delta (K)",
        "rotational_speed_rpm": "Rotational speed (RPM)",
        "torque_nm": "Torque (Nm)",
        "tool_wear_min": "Tool wear (minutes)",
        "failure_mode_count": "Failure-mode flag count",
    }

    choices = list(sensor_labels)

    x_col, y_col, colour_col = st.columns(3)

    with x_col:
        x_sensor = st.selectbox(
            "X-axis sensor",
            choices,
            index=3,
            format_func=lambda x: sensor_labels[x],
        )

    with y_col:
        y_sensor = st.selectbox(
            "Y-axis sensor",
            choices,
            index=4,
            format_func=lambda x: sensor_labels[x],
        )

    with colour_col:
        colour_by = st.selectbox(
            "Colour observations by",
            ["machine_failure", "machine_type", "primary_failure_category"],
            format_func=lambda x: {
                "machine_failure": "Recorded failure outcome",
                "machine_type": "Machine type",
                "primary_failure_category": "Primary reporting category",
            }[x],
        )

    if total:
        fig = px.scatter(
            filtered,
            x=x_sensor,
            y=y_sensor,
            color=colour_by,
            symbol="machine_type",
            hover_data=[
                "source_record_id",
                "machine_type",
                "machine_failure",
                "tool_wear_min",
            ],
            labels={
                **sensor_labels,
                "machine_failure": "Recorded failure",
                "machine_type": "Machine type",
                "primary_failure_category": "Reporting category",
            },
            opacity=0.72,
        )
        st.plotly_chart(style_chart(fig, 520), use_container_width=True)

        st.write("")
        left, right = st.columns(2)

        with left:
            section_heading(
                "Correlation matrix",
                "Pearson correlations across numeric sensor and label fields.",
            )

            numeric_columns = [
                "air_temperature_k",
                "process_temperature_k",
                "temperature_delta_k",
                "rotational_speed_rpm",
                "torque_nm",
                "tool_wear_min",
                "machine_failure",
            ]

            corr = filtered[numeric_columns].corr()

            fig = px.imshow(
                corr,
                text_auto=".2f",
                color_continuous_scale=[
                    "#123B4B", "#142638", "#2CA99A", "#D6FFF6"
                ],
                zmin=-1,
                zmax=1,
                aspect="auto",
            )
            st.plotly_chart(style_chart(fig, 480), use_container_width=True)

        with right:
            section_heading(
                "Descriptive statistics",
                "Summary of selected observations after sidebar filters.",
            )

            stats = filtered[
                list(sensor_labels)
            ].describe().T.reset_index()

            stats = stats.rename(columns={"index": "Sensor"})
            stats["Sensor"] = stats["Sensor"].map(sensor_labels)

            st.dataframe(
                stats.round(3),
                use_container_width=True,
                hide_index=True,
            )

    st.caption(
        "Correlations are exploratory and may be affected by class imbalance, "
        "synthetic data generation, and the dataset's sampling design."
    )


# ---------------------------------------------------------
# PAGE 4: DATA QUALITY
# ---------------------------------------------------------

elif page == "Data Quality":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">TRUST · LINEAGE · REPRODUCIBILITY</div>
            <h1>Data Quality Centre</h1>
            <p>
                Inspect source validation metadata, dbt test artifacts,
                transformation lineage, and the controls that make this
                analytics workflow reproducible.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    raw_rows = manifest.get("row_count", "Not recorded")
    raw_columns = manifest.get("column_count", "Not recorded")
    missing = manifest.get("missing_values", "Not recorded")
    validation = manifest.get("validation_status", "Not recorded")

    a, b, c, d = st.columns(4)

    a.metric("Source rows", f"{raw_rows:,}" if isinstance(raw_rows, int) else raw_rows)
    b.metric("Source columns", raw_columns)
    c.metric("Missing source values", missing)
    d.metric("Source validation", str(validation).upper())

    st.write("")

    left, right = st.columns(2)

    with left:
        section_heading(
            "dbt test artifact",
            "Status is read from target/run_results.json when available.",
        )

        if dbt_status["available"]:
            t1, t2, t3 = st.columns(3)
            t1.metric("Passed", dbt_status["passed"])
            t2.metric("Failed / errors", dbt_status["failed"])
            t3.metric("Tests in artifact", dbt_status["total"])

            if dbt_status["failed"] == 0:
                st.success("No failed tests were recorded in this artifact.")
            else:
                st.error("The latest available artifact includes failed tests.")
        else:
            st.info(
                "No dbt test results were found in target/run_results.json. "
                "Run `dbt test` to generate the artifact."
            )

    with right:
        section_heading(
            "Source manifest",
            "Metadata produced by the ingestion validation step.",
        )

        if manifest:
            st.json({
                "dataset": manifest.get("dataset"),
                "source": manifest.get("source"),
                "dataset_id": manifest.get("dataset_id"),
                "row_count": manifest.get("row_count"),
                "column_count": manifest.get("column_count"),
                "missing_values": manifest.get("missing_values"),
                "sha256": manifest.get("sha256"),
                "validation_status": manifest.get("validation_status"),
                "validated_at_utc": manifest.get("validated_at_utc"),
                "data_character": manifest.get("data_character"),
            })
        else:
            st.warning("Source manifest not found.")

    st.write("")
    section_heading(
        "Transformation lineage",
        "The flow from source data to business reporting.",
    )

    lineage_cols = st.columns(4)

    lineage = [
        ("01", "SOURCE", "AI4I CSV", "Validated and hashed"),
        ("02", "STAGING", "stg_ai4i_machine_data", "Standardized columns"),
        ("03", "INTERMEDIATE", "int_machine_observations", "Derived features"),
        ("04", "MART", "mart_maintenance_kpis", "Business aggregates"),
    ]

    for column, (number, layer, name, description) in zip(lineage_cols, lineage):
        with column:
            st.markdown(
                f"""
                <div class="metric-card" style="min-height:170px">
                    <div class="eyebrow">{number} / {layer}</div>
                    <div style="font-weight:800;margin:12px 0;color:#F4FAFF">
                        {name}
                    </div>
                    <div style="color:#91A6BB;font-size:0.8rem">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    section_heading(
        "Data contracts and controls",
        "Implemented checks and their purpose.",
    )

    controls = pd.DataFrame([
        ["Schema validation", "Expected source columns", "Ingestion validation"],
        ["Completeness", "No missing source values", "Ingestion validation"],
        ["Source integrity", "SHA-256 checksum manifest", "Ingestion validation"],
        ["Primary-key quality", "Non-null and unique source record IDs", "dbt tests"],
        ["Domain validation", "Machine types L, M, H", "dbt tests"],
        ["Flag validation", "Binary failure flags", "dbt tests"],
        ["KPI logic", "Valid failure counts and percentages", "Singular dbt test"],
    ], columns=["Control", "Rule", "Layer"])

    st.dataframe(controls, use_container_width=True, hide_index=True)

    st.caption(
        "The dbt results shown here depend on the latest available run-results "
        "artifact. The UI does not independently rerun tests when the page opens."
    )


# ---------------------------------------------------------
# PAGE 5: DATA EXPLORER
# ---------------------------------------------------------

elif page == "Data Explorer":

    st.markdown(
        """
        <div class="hero">
            <div class="eyebrow">TRANSPARENCY · INVESTIGATION · EXPORT</div>
            <h1>Observation Explorer</h1>
            <p>
                Browse the transformed observations behind the charts.
                Apply the global filters, inspect records, and export the
                selected dataset for further analysis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.metric("Rows in current selection", f"{total:,}")

    if total:
        search_id = st.text_input(
            "Find source record ID",
            placeholder="Enter an exact record ID, e.g. 1234",
        )

        displayed = filtered.copy()

        if search_id.strip():
            if search_id.strip().isdigit():
                displayed = displayed[
                    displayed["source_record_id"] == int(search_id.strip())
                ]
            else:
                displayed = displayed.iloc[0:0]

        st.dataframe(
            displayed,
            use_container_width=True,
            hide_index=True,
            height=480,
        )

        csv_bytes = displayed.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download filtered observations (CSV)",
            data=csv_bytes,
            file_name="industrialpulse_filtered_observations.csv",
            mime="text/csv",
            use_container_width=False,
        )
    else:
        st.info("No observations match the current filters.")


# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown(
    """
    <div class="footer">
        INDUSTRIALPULSE · INDEPENDENT PORTFOLIO PROJECT<br>
        Built with Python, Streamlit, Plotly, DuckDB and dbt.<br>
        Dataset: UCI AI4I 2020 Predictive Maintenance Dataset.
        Synthetic observations only; not live industrial telemetry.
    </div>
    """,
    unsafe_allow_html=True,
)
