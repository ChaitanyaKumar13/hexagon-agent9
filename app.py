"""
Agent 9 - Marketing Campaign Agent
Proof of concept for the AI-Based Marketing & Sales Intelligence Platform (SOW, Section 5)
Hexagon Geosystems India

Pipeline: Strategist -> Campaign Writer -> Human Editor
Model: Claude Sonnet 5 via the Anthropic API
"""

import time

import streamlit as st
from anthropic import Anthropic

# ---------------------------------------------------------------------------
# Configuration (branding and industries are configurable here - no code
# changes needed elsewhere in the app)
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-5"

BRANDING = {
    "company": "HEXAGON",
    "platform": "AI-Based Marketing & Sales Intelligence Platform",
    # theme: "navy" matches the Hexagon corporate presentation (dark navy +
    # lime highlights); "light" matches Hexagon document templates (white +
    # blue). Colours below are close approximations of the corporate deck -
    # swap in exact hex codes if the brand team provides them.
    "theme": "navy",
    "accent": "#0096D6",
    "lime": "#C9DD28",
    "navy_bg": "#0C2C40",
    "navy_panel": "#123B54",
    "text_light": "#1A1A1A",
    "logo_path": None,     # e.g. "logo.png" placed in the repo root
}

# Target segments per manager input. Add a new industry by adding a line here.
SECTORS = [
    "Mining",
    "Surveying & Geospatial",
    "Railways",
    "Defence",
    "Infrastructure",
]

st.set_page_config(
    page_title="Hexagon_AG9 · Marketing Campaign Agent",
    page_icon="⬡",
    layout="wide",
)

ACCENT = BRANDING["accent"]
LIME = BRANDING["lime"]

if BRANDING["theme"] == "navy":
    BG = BRANDING["navy_bg"]
    PANEL = BRANDING["navy_panel"]
    HEADING = "#FFFFFF"
    BODY = "#D7E3EC"
    SUB = "#9DB4C4"
    EYEBROW = LIME
    BTN = LIME
    BTN_TEXT = BRANDING["navy_bg"]
    BTN_HOVER = "#B8CC1E"
    TOPBAR = f"linear-gradient(90deg, {LIME} 30%, {ACCENT} 30%, {ACCENT} 55%, #1E4A66 55%)"
else:
    BG = "#FFFFFF"
    PANEL = "#F4F8FB"
    HEADING = BRANDING["text_light"]
    BODY = "#333333"
    SUB = "#555555"
    EYEBROW = ACCENT
    BTN = ACCENT
    BTN_TEXT = "#FFFFFF"
    BTN_HOVER = "#007AB0"
    TOPBAR = f"linear-gradient(90deg, {ACCENT} 40%, #E5E5E5 40%)"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;600;700;800&display=swap');

    /* Hide Streamlit's default chrome for a clean client-facing demo */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .stAppDeployButton {{display: none;}}
    header[data-testid="stHeader"] {{background: transparent;}}

    html, body, .stApp, .stApp * {{ font-family: 'Hanken Grotesk', -apple-system, sans-serif; }}
    /* Restore Streamlit's icon font (otherwise icons render as raw text) */
    [data-testid="stIconMaterial"], span[translate="no"], .material-symbols-rounded {{
        font-family: 'Material Symbols Rounded' !important;
    }}
    .stApp {{
        background:
            radial-gradient(1100px 560px at 88% -8%, rgba(111,214,255,0.10), transparent 60%),
            radial-gradient(900px 520px at -8% 108%, rgba(201,221,40,0.07), transparent 55%),
            {BG};
    }}
    .stApp, .stApp p, .stApp li, .stApp label {{ color: {BODY}; }}
    .stApp p, .stApp li {{ font-size: 1.02rem; line-height: 1.65; }}
    hr {{ border-color: rgba(255,255,255,0.08) !important; }}
    ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(255,255,255,0.14); border-radius: 8px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}

    h1 {{
        font-weight: 800 !important;
        letter-spacing: -0.03em;
        background: linear-gradient(100deg, #FFFFFF 55%, {LIME} 85%, #6FD6FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    h2, h3 {{ color: {HEADING} !important; font-weight: 700; letter-spacing: -0.01em; }}

    section[data-testid="stSidebar"] {{
        background: {PANEL};
        border-right: 1px solid rgba(255,255,255,0.06);
    }}
    /* Manager request: inputs panel = 30% of screen, agent screen = 70% */
    @media (min-width: 900px) {{
        section[data-testid="stSidebar"] {{
            width: 30vw !important;
            min-width: 30vw !important;
            max-width: 30vw !important;
        }}
    }}
    section[data-testid="stSidebar"] * {{ color: {BODY}; }}

    /* Input text visibility (Windows renders the default too dull) */
    .stTextInput input, .stTextArea textarea, [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {{
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        background: rgba(255,255,255,0.07) !important;
        caret-color: {LIME};
        font-size: 1rem !important;
    }}
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
        color: rgba(215,227,236,0.45) !important;
        -webkit-text-fill-color: rgba(215,227,236,0.45) !important;
    }}
    [data-baseweb="select"] * {{ color: #FFFFFF !important; }}
    [data-baseweb="select"] > div {{ background: rgba(255,255,255,0.07) !important; }}

    /* Animated brand gradient bar */
    .hx-topbar {{
        height: 6px;
        background: linear-gradient(90deg, {LIME}, #6FD6FF, {ACCENT}, {LIME});
        background-size: 300% 100%;
        animation: hxflow 9s ease infinite;
        border-radius: 3px;
        margin-bottom: 1.4rem;
    }}
    @keyframes hxflow {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    /* Content entrance motion */
    .block-container {{ animation: hxrise 0.55s cubic-bezier(0.22, 1, 0.36, 1); }}
    @keyframes hxrise {{
        from {{ opacity: 0; transform: translateY(14px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    .hx-eyebrow {{
        color: {EYEBROW};
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }}
    .hx-sub {{ color: {SUB}; font-size: 0.98rem; margin-top: -0.4rem; }}

    /* Buttons: lift + glow on hover */
    div.stButton > button, div.stDownloadButton > button {{
        background: {BTN};
        color: {BTN_TEXT};
        border: none;
        font-weight: 700;
        padding: 0.65rem 1.7rem;
        border-radius: 8px;
        transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease;
    }}
    div.stButton > button:hover, div.stDownloadButton > button:hover {{
        background: {BTN_HOVER};
        color: {BTN_TEXT};
        transform: translateY(-2px);
        box-shadow: 0 10px 26px rgba(201, 221, 40, 0.25);
    }}
    /* Button labels render inside <p>; override the global text colour */
    div.stButton > button p, div.stDownloadButton > button p {{
        color: {BTN_TEXT} !important;
        font-weight: 700;
    }}

    /* Tabs: pill style with smooth hover */
    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 999px;
        padding: 6px 16px;
        transition: background 0.2s ease, color 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{ background: rgba(255,255,255,0.07); }}
    .stTabs [aria-selected="true"] {{ background: rgba(201, 221, 40, 0.12); }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {EYEBROW}; }}
    /* Output panels as cards */
    .stTabs [data-baseweb="tab-panel"] {{
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 14px;
        padding: 1.4rem 1.6rem;
        margin-top: 0.9rem;
    }}
    /* Info callout + status expander */
    [data-testid="stAlert"] {{
        background: rgba(111,214,255,0.08);
        border: 1px solid rgba(111,214,255,0.28);
        border-radius: 12px;
    }}
    [data-testid="stExpander"] {{
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 12px;
        background: rgba(255,255,255,0.02);
    }}

    /* Inputs: soft borders, lime focus ring */
    [data-baseweb="input"], [data-baseweb="textarea"], [data-baseweb="select"] > div {{
        border-radius: 8px !important;
        border-color: rgba(255,255,255,0.12) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-baseweb="input"]:focus-within, [data-baseweb="textarea"]:focus-within {{
        border-color: {LIME} !important;
        box-shadow: 0 0 0 3px rgba(201, 221, 40, 0.18);
    }}

    /* Status/progress accent */
    [data-testid="stStatusWidget"], .stSpinner > div {{ border-color: {LIME} transparent transparent transparent; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Demo presets - manager's priority products
# ---------------------------------------------------------------------------

PRESETS = {
    "— Select a scenario or fill manually —": {},
    "Leica GS18 GNSS RTK Rover · Surveying & Geospatial": {
        "product": "Leica GS18 GNSS RTK Rover",
        "sector": "Surveying & Geospatial",
        "audience": (
            "Government survey departments, town planning bodies, licensed "
            "private surveyors and engineering consultancies handling cadastral, "
            "corridor and infrastructure surveys"
        ),
        "goal": "Generate demo requests and position the GS18 as the default rover for large-area survey tenders",
        "message": (
            "Tilt compensation immune to magnetic disturbance - measure points "
            "you previously could not reach, without plumbing the pole, and cut "
            "field time on every job"
        ),
        "event": "Regional Hexagon customer roadshow / survey department demo days",
    },
    "IDS GeoRadar ArcSAR · Mining": {
        "product": "IDS GeoRadar ArcSAR slope monitoring radar",
        "sector": "Mining",
        "audience": (
            "Mine planning heads, geotechnical engineers and safety officers at "
            "Indian open-pit operations - Coal India subsidiaries, NMDC, and "
            "private iron ore, limestone and copper mines"
        ),
        "goal": "Create urgency around continuous slope stability monitoring and generate site assessment enquiries",
        "message": (
            "Continuous, real-time slope movement detection across the whole pit "
            "wall - early warning that protects people and equipment and keeps "
            "production moving"
        ),
        "event": "Mining safety week engagements and industry mining expos",
    },
    "Leica RTC360 Laser Scanner · Infrastructure": {
        "product": "Leica RTC360 3D laser scanner",
        "sector": "Infrastructure",
        "audience": (
            "BIM heads, project directors and digital construction teams at EPC "
            "contractors and consultants on metro, railway station and highway "
            "projects"
        ),
        "goal": "Drive enquiries for as-built capture and progress documentation workflows",
        "message": (
            "A complete high-detail scan with imagery in about two minutes per "
            "setup - document site conditions faster than the site changes"
        ),
        "event": "On-site demo programme with BIM teams on active metro projects",
    },
}

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

BRAND_VOICE = """Brand voice reference (from Hexagon's June 2026 corporate presentation \
and public materials):

Core identity: "At Hexagon, we are the global leader in measurement technologies. Our \
precision measurement, positioning, and autonomous solutions transform the world's most \
vital industries - providing the confidence that customers rely on to build, navigate, \
and innovate." Supporting lines used by the brand: "From microns to Mars, we drive \
productivity, quality, safety, and sustainability where it matters most" and "If it \
doesn't exist, Hexagon invents it." Closing tagline: "When it has to be right. It has to \
be Hexagon."

The relevant division for this campaign work is Infrastructure & Geospatial: geomatics, \
machine control, radar & monitoring, scanning & mapping - helping geodata-dependent \
industries capture, measure and visualise the physical world, turning data into \
actionable insights.

Hexagon's proof style (follow this pattern in campaign content): lead with a small \
number of large, concrete outcome metrics, then back them with a named-customer voice. \
Real examples from their materials: "27 km undersea tunnel / 392 m below sea level / \
3-5 cm tunnel alignment accuracy" (Skanska) and "7% fuel efficiency improvement / 4-8% \
reduction in cost / 12-15% reduction in time" (Maaden mining). Two or three hard numbers \
beat ten adjectives. Never invent fake customer names or fake statistics - for the demo, \
use placeholder brackets like [customer case study metric] where a real number would go, \
or speak to the outcome type without a fabricated figure.

The voice is precise, assured and understated: confidence comes from measured facts and \
proven outcomes, never from hype. Claims are concrete and verifiable. Sentences are \
clean and direct."""

STRATEGIST_SYSTEM = f"""You are the campaign strategist inside Hexagon Geosystems India's \
Marketing & Sales Intelligence Platform. Hexagon Geosystems sells surveying, reality \
capture, GNSS, monitoring radar, machine control and geospatial solutions (including the \
Leica Geosystems and IDS GeoRadar product lines) to B2B and government buyers in India: \
mining companies, survey departments, EPC contractors, railways, defence and \
infrastructure firms. Buying cycles are long, technical and tender-driven. Decision \
makers care about accuracy specs, uptime, safety, total cost of ownership, local service \
support and proof from comparable Indian projects.

{BRAND_VOICE}

Produce a tight campaign strategy brief. Be specific to the Indian market. No fluff, no \
generic marketing theory."""

WRITER_SYSTEM = f"""You are the campaign content writer inside Hexagon Geosystems India's \
Marketing & Sales Intelligence Platform. You write for technical B2B buyers in Indian \
mining, survey, railways, defence and infrastructure sectors. These readers are engineers \
and project heads. They distrust hype and respond to specifics: accuracy figures, time \
saved, safety outcomes, crew size reduced, tender compliance, service network.

{BRAND_VOICE}

LinkedIn house style (observed from Hexagon India's actual recent posts - follow this \
structure for every LinkedIn post):
1. Open with a one-line hook that states a belief or tension, e.g. "Reality capture \
should accelerate your project - not slow it down." or "Automation was just the warm-up; \
autonomy is the main event."
2. Body of 2-4 clean sentences with concrete specs and outcomes ("captures up to 2 \
million points per second and generates coloured point clouds in under two minutes").
3. Optionally a short checkmark list (3-4 items, each 2-5 words) introduced by a line \
like "The result?" - items like "Faster data capture / Increased field productivity / \
More time focused on project delivery".
4. Close with one short punchy line ("Capture more with less effort.").
5. If there is an offer or event, one line with the deadline, optionally prefixed with a \
calendar emoji.
6. A line tagging the local experts as placeholders: "Speak to our experts: [Expert Name] \
[Expert Name]".
7. Finish with 4-6 hashtags mixing product, technology and market tags, e.g. \
#LeicaRTC360 #RealityCapture #LaserScanning #Surveying #HexagonIndia.

Follow the campaign strategy brief you are given. Produce exactly the sections requested, \
in clean Markdown with clear ## headings."""

EDITOR_SYSTEM = """You are a senior human copy editor at an Indian B2B marketing agency. \
Your job is to take draft marketing content and rewrite it so it reads like an experienced \
human marketer wrote it - natural, direct and specific.

Rules you must apply:
- Remove AI-typical words and phrases entirely: "delve", "leverage", "unlock", "elevate", \
"seamless", "cutting-edge", "game-changer", "revolutionize", "in today's fast-paced world", \
"look no further", "unleash", "empower", "robust", "harness the power".
- Kill the "isn't a X. It's a Y." construction and its variants ("not just X - it's Y", \
"more than a X, it's a Y") wherever they appear, especially as closing lines. Also rewrite \
mirrored-antithesis closers ("Stale X is A. Fresh X is B.") into a single plain sentence. \
A closing line should sound like a person, not a slogan generator.
- Vary sentence length. Mix short punchy sentences with longer ones. Never let three \
sentences in a row follow the same structure.
- Cut every sentence that says nothing concrete. If a line could apply to any product, \
delete it or replace it with a specific claim.
- Reduce adjectives. One strong specific beats three vague ones.
- Almost no exclamation marks. No rocket, sparkle or fire emojis anywhere. LinkedIn \
posts follow Hexagon India's house conventions: a checkmark-style benefit list of 3-4 \
short items is fine, a single calendar emoji on an offer/deadline line is fine, and 4-6 \
hashtags at the end are expected. Everywhere outside LinkedIn posts (emails, webinar, \
exhibition, SEO), use no emojis and no hashtags.
- In emails and all other sections, keep bullet lists only where a human marketer would \
use them (feature comparisons, event details). Convert everything else to natural prose.
- Do not use em-dashes more than twice in the whole document.
- Keep the Indian B2B register: professional, slightly conversational, no American \
sales-bro tone. The Hexagon voice is precise and understated - "When it has to be right."
- Preserve the document structure and all ## section headings exactly. Do not add \
commentary, notes or explanations. Return only the edited document."""


def build_writer_prompt(inputs: dict, strategy: str) -> str:
    event_line = (
        f"- Event tie-in: {inputs['event']}" if inputs.get("event") else
        "- Event tie-in: none specified; propose a plausible one"
    )
    return f"""Campaign strategy brief:
{strategy}

Campaign inputs:
- Product: {inputs['product']}
- Sector: {inputs['sector']}
- Target audience: {inputs['audience']}
- Campaign goal: {inputs['goal']}
- Key message: {inputs['message']}
{event_line}

Write the full campaign kit with exactly these sections (matching Agent 9's scope in the \
platform SOW):

## Campaign Overview
3-4 sentences: the angle, the audience and what success looks like.

## LinkedIn Campaign
Three LinkedIn posts (label them Post 1, Post 2, Post 3), each following the Hexagon \
India house style from your instructions (hook line, spec-backed body, optional 3-4 item \
checkmark list, punchy closer, expert-tag placeholder line, 4-6 hashtags). Distinct \
angles: one proof/results-led, one problem-led, one event or demo push. Include a \
suggested visual for each in one line.

## Email Campaign
A three-email nurture sequence (Email 1, 2, 3). Each with a subject line, 100-150 word \
body, and one clear call to action. Emails should build on each other.

## Webinar Concept
Title, 3-4 agenda points, target speaker profile, and a 2-line promotional blurb.

## Product Launch & Exhibition Angle
How to present this product at the event tie-in above (or a relevant Indian trade \
exhibition for this sector) - booth hook, live demo idea, and a lead-capture mechanism.

## SEO Opportunities
Five search queries this audience actually types (mix English and Indian-market phrasing), \
each with a one-line content recommendation."""


HUMANIZE_PROMPT = """Edit the following draft campaign kit according to your rules. \
Return the full edited document.

Draft:
{draft}"""

# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------


def get_client() -> Anthropic | None:
    key = st.secrets.get("ANTHROPIC_API_KEY", None)
    if not key:
        return None
    return Anthropic(api_key=key)


def call_claude(client: Anthropic, system: str, prompt: str, max_tokens: int = 12000) -> str:
    """Call the model and return visible text.

    Sonnet 5 reasons internally (adaptive thinking) before answering, and that
    reasoning shares the max_tokens budget. Budgets are therefore generous, and
    if a call still returns no visible text we retry once with a bigger budget.
    """
    for attempt, budget in enumerate([max_tokens, max_tokens * 2]):
        response = client.messages.create(
            model=MODEL,
            max_tokens=budget,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in response.content if block.type == "text")
        if text.strip():
            return text
    return ""


def run_pipeline(client: Anthropic, inputs: dict, status) -> dict:
    status.update(label="Step 1 of 3 · Building campaign strategy…")
    strategy = call_claude(
        client,
        STRATEGIST_SYSTEM,
        f"""Create a campaign strategy brief for:
- Product: {inputs['product']}
- Sector: {inputs['sector']}
- Target audience: {inputs['audience']}
- Campaign goal: {inputs['goal']}
- Key message: {inputs['message']}

Cover: positioning angle, top 3 buyer pain points, proof points to emphasise, tone \
guidance, and the single most important thing every asset must communicate. \
Keep it under 350 words.""",
        max_tokens=6000,
    )
    if not strategy.strip():
        raise RuntimeError("The strategy step returned no text. Please click Generate again.")

    status.update(label="Step 2 of 3 · Writing campaign content…")
    draft = call_claude(client, WRITER_SYSTEM, build_writer_prompt(inputs, strategy), 16000)
    if not draft.strip():
        raise RuntimeError("The content step returned no text. Please click Generate again.")

    status.update(label="Step 3 of 3 · Human editor pass…")
    final = call_claude(client, EDITOR_SYSTEM, HUMANIZE_PROMPT.format(draft=draft), 16000)
    if not final.strip():
        # Editor failed - fall back to the unedited draft rather than losing the kit.
        final = draft

    return {"strategy": strategy, "final": final}


def split_sections(doc: str) -> dict:
    """Split the final markdown document into its ## sections for tabbed display."""
    sections: dict[str, str] = {}
    current = "Overview"
    buf: list[str] = []
    for line in doc.splitlines():
        if line.startswith("## "):
            if buf:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
        else:
            buf.append(line)
    if buf:
        sections[current] = "\n".join(buf).strip()
    return sections


def linkedin_posts(md: str) -> list[tuple[str, str, str]]:
    """Parse the LinkedIn section into (label, hook_line, visual_suggestion) tuples."""
    import re

    labels = re.findall(r"\*\*(Post\s*\d+[^*]*)\*\*", md)
    bodies = re.split(r"\*\*Post\s*\d+[^*]*\*\*", md)[1:]
    posts = []
    for label, body in zip(labels, bodies):
        hook = ""
        for line in body.splitlines():
            clean = line.strip()
            if clean and not clean.startswith(("#", "**Visual", "✅", "✔", "📅")):
                hook = clean.lstrip("*_ ").rstrip("*_ ")
                break
        visual_match = re.search(r"\*\*Visual:\*\*\s*(.+)", body)
        visual = visual_match.group(1).strip() if visual_match else ""
        posts.append((label.strip(), hook, visual))
    return posts


def creative_card_html(product: str, hook: str, visual: str) -> str:
    """Render a Hexagon-style LinkedIn creative card (matches their real ad layout)."""
    visual_note = (
        f'<div style="margin-top:14px;font-size:0.78rem;color:#9DB4C4;font-style:italic;">'
        f"Suggested imagery: {visual}</div>" if visual else ""
    )
    return f"""
    <div style="background:linear-gradient(135deg,#0C2C40 70%,#123B54 100%);
                border:1px solid rgba(255,255,255,0.14);border-radius:14px;
                padding:26px 30px;max-width:560px;position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;right:0;width:140px;height:6px;
                    background:linear-gradient(90deg,#C9DD28,#6FD6FF);"></div>
        <div style="font-weight:800;letter-spacing:0.06em;color:#FFFFFF;
                    font-size:0.95rem;">⬡ HEXAGON</div>
        <div style="margin-top:16px;font-size:0.8rem;color:#C9DD28;
                    letter-spacing:0.08em;text-transform:uppercase;">{product}</div>
        <div style="margin-top:8px;font-size:1.45rem;line-height:1.25;font-weight:800;
                    color:#FFFFFF;">{hook}</div>
        {visual_note}
    </div>
    """


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.markdown('<div class="hx-topbar"></div>', unsafe_allow_html=True)
if BRANDING["logo_path"]:
    st.image(BRANDING["logo_path"], width=160)
st.markdown(
    f'<div class="hx-eyebrow">{BRANDING["company"]} · {BRANDING["platform"]}</div>',
    unsafe_allow_html=True,
)
st.title("Hexagon_AG9 — Marketing Campaign Agent")
st.markdown(
    '<p class="hx-sub">Proof of concept · Generates a complete campaign kit: '
    "LinkedIn, email, webinar, exhibition and SEO recommendations</p>",
    unsafe_allow_html=True,
)
st.divider()

client = get_client()
if client is None:
    st.error(
        "No API key found. Add ANTHROPIC_API_KEY to your Streamlit secrets "
        "(see SETUP_GUIDE.md, Step 3) and reload."
    )
    st.stop()

with st.sidebar:
    st.markdown("### Campaign inputs")
    preset_name = st.selectbox("Demo scenario", list(PRESETS.keys()))
    preset = PRESETS[preset_name]

    product = st.text_input("Product / solution", value=preset.get("product", ""))

    sector_options = SECTORS + ["Other (type below)"]
    default_sector = preset.get("sector", SECTORS[0])
    sector_index = sector_options.index(default_sector) if default_sector in sector_options else 0
    sector_choice = st.selectbox("Sector", sector_options, index=sector_index)
    if sector_choice == "Other (type below)":
        sector = st.text_input("Custom sector / industry")
    else:
        sector = sector_choice

    audience = st.text_area("Target audience", value=preset.get("audience", ""), height=100)
    goal = st.text_input("Campaign goal", value=preset.get("goal", ""))
    message = st.text_area("Key message", value=preset.get("message", ""), height=90)
    event = st.text_input("Event tie-in (optional)", value=preset.get("event", ""))

    run = st.button("Generate campaign", use_container_width=True)

if run:
    if not all([product.strip(), sector.strip(), audience.strip(), goal.strip(), message.strip()]):
        st.warning("Please fill all five main inputs (or pick a demo scenario) before generating.")
        st.stop()

    inputs = {
        "product": product,
        "sector": sector,
        "audience": audience,
        "goal": goal,
        "message": message,
        "event": event.strip(),
    }

    t0 = time.time()
    with st.status("Starting Agent 9…", expanded=False) as status:
        try:
            result = st.session_state["result"] = run_pipeline(client, inputs, status)
            status.update(label=f"Campaign generated in {time.time() - t0:.0f}s", state="complete")
        except Exception as exc:  # noqa: BLE001
            status.update(label="Generation failed", state="error")
            st.error(f"Something went wrong while calling the API: {exc}")
            st.stop()

if "result" in st.session_state:
    result = st.session_state["result"]
    sections = split_sections(result["final"])

    tab_names = list(sections.keys()) + ["Strategy Brief"]
    tabs = st.tabs(tab_names)
    for tab, name in zip(tabs[:-1], sections.keys()):
        with tab:
            st.markdown(sections[name])
            if "linkedin" in name.lower():
                posts = linkedin_posts(sections[name])
                if posts:
                    st.markdown("---")
                    st.markdown("**Creative previews** · Click to expand each post's suggested creative")
                    for label, hook, visual in posts:
                        if not hook:
                            continue
                        with st.expander(f"🖼️ Creative preview — {label}"):
                            st.markdown(
                                creative_card_html(product, hook, visual),
                                unsafe_allow_html=True,
                            )
    with tabs[-1]:
        st.caption("Internal strategy brief produced in Step 1 of the pipeline.")
        st.markdown(result["strategy"])

    st.divider()
    st.download_button(
        "Download full campaign kit (.md)",
        data=result["final"],
        file_name="hexagon_agent9_campaign_kit.md",
        mime="text/markdown",
    )
else:
    st.info(
        "Pick a demo scenario in the sidebar (or enter your own inputs) and click "
        "**Generate campaign**. The agent runs a three-step pipeline: strategy, "
        "content, then a human-style editing pass."
    )
