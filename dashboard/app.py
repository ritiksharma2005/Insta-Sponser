import sys
from pathlib import Path
from http.server import BaseHTTPRequestHandler

# Dummy handler for Vercel Python runtime inspector
class app(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b"<h1>News NIT IIT Sponsor Engine</h1><p>Streamlit Dashboard running locally or on Streamlit Cloud.</p>")

# Add project root to sys.path at the absolute top
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd

from sponsor_engine.database.sqlite_db import SQLiteDatabase
from sponsor_engine.analytics.analytics import AnalyticsEngine
from sponsor_engine.outreach.approval import ApprovalManager
from sponsor_engine.outreach.instagram_sender import InstagramSender
from sponsor_engine.scheduler.daily_job import DailySponsorshipJob
from config.media_profile import get_media_profile, update_media_profile
from config.settings import get_settings

# Page Config
st.set_page_config(
    page_title="News NIT IIT - Sponsor Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    .main {
        background-color: #0E1117;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E2640 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .lead-card {
        background: #1E293B;
        border-left: 4px solid #38BDF8;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .badge-hot {
        background-color: #EF4444;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .badge-high {
        background-color: #F59E0B;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    .badge-medium {
        background-color: #3B82F6;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Core Services
db = SQLiteDatabase()
analytics = AnalyticsEngine(db)
approval_mgr = ApprovalManager(db)
sender = InstagramSender(db)
settings = get_settings()

# Sidebar Navigation
st.sidebar.image("https://img.icons8.com/isometric/96/rocket.png", width=64)
st.sidebar.title("News NIT IIT")
st.sidebar.caption("AI Sponsorship Lead & Outreach Engine")

nav_option = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard Overview", "✅ Human Approval Queue", "🔄 Pipeline Tracker", "📈 Analytics & Insights", "⚙️ Media Profile & Config"]
)

def safe_reset_leads(db_instance):
    """Safely resets all lead statuses to APPROVAL_PENDING across all environment versions."""
    # Clear any stale session state error messages
    keys_to_clear = [k for k in st.session_state.keys() if k.startswith("outreach_res_")]
    for k in keys_to_clear:
        del st.session_state[k]

    try:
        if hasattr(db_instance, "reset_all_leads_to_pending"):
            return db_instance.reset_all_leads_to_pending()
    except Exception:
        pass
    
    with db_instance._get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE leads SET status = 'APPROVAL_PENDING', last_contacted = 'Not Contacted'")
        count = cursor.rowcount
        conn.commit()
        return count

# Run Daily Job & Utility Buttons in Sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Run Daily Lead Discovery", use_container_width=True):
    with st.spinner("Executing 12-step lead discovery pipeline..."):
        job = DailySponsorshipJob()
        res = job.run_daily_pipeline()
        st.sidebar.success(f"Discovered {len(res['top_leads'])} new top prospects!")
        st.rerun()

if st.sidebar.button("🔄 Reset Leads to Pending Queue", use_container_width=True):
    reset_cnt = safe_reset_leads(db)
    st.sidebar.success(f"Reset {reset_cnt} leads to Approval Queue!")
    st.rerun()

st.sidebar.markdown("---")
settings = get_settings()

tok_preview = f"`{settings.META_ACCESS_TOKEN[:12]}...`" if settings.META_ACCESS_TOKEN else "`MISSING`"
st.sidebar.info(f"**DRY RUN Mode**: `{settings.DRY_RUN}`\n\n**Active Token**: {tok_preview}")

# 1. OVERVIEW PAGE
if nav_option == "📊 Dashboard Overview":
    st.title("📊 Dashboard Overview")
    st.caption("Real-time summary of sponsorship lead generation & outreach pipeline")

    metrics = analytics.get_summary_metrics()

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["total_leads"]}</div><div class="metric-label">Total Leads</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #EF4444;">{metrics["hot_leads"]}</div><div class="metric-label">🔥 Hot Leads</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #F59E0B;">{metrics["high_leads"]}</div><div class="metric-label">⚡ High Leads</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #10B981;">{metrics["pending_approval"]}</div><div class="metric-label">Approval Pending</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: #A855F7;">{metrics["contacted_leads"]}</div><div class="metric-label">Contacted</div></div>', unsafe_allow_html=True)

    st.markdown("### 🏆 Top Verified Prospects")
    all_leads = db.get_all_leads()
    if all_leads:
        df = pd.DataFrame([l.model_dump() for l in all_leads[:10]])
        st.dataframe(
            df[["business_name", "category", "city", "lead_score", "lead_tier", "instagram", "status"]],
            use_container_width=True
        )
    else:
        st.warning("No lead data stored yet. Click 'Run Daily Lead Discovery' in the sidebar to start!")

# 2. HUMAN APPROVAL QUEUE
elif nav_option == "✅ Human Approval Queue":
    st.title("✅ Lead Review & Approval Queue")
    st.caption("Review AI-qualified leads and personalized DM messages before outreach")

    top_col1, top_col2 = st.columns([3, 1])
    with top_col2:
        if st.button("🔄 Reset All Leads to Pending", key="top_reset_btn", use_container_width=True):
            r_cnt = safe_reset_leads(db)
            st.success(f"Reset {r_cnt} leads!")
            st.rerun()

    all_leads = db.get_all_leads()
    pending_leads = [l for l in all_leads if l.status in ("APPROVAL_PENDING", "APPROVED")]

    if not pending_leads:
        st.success("🎉 No pending leads! All discovered leads have been contacted or reviewed.")
    else:
        st.info(f"Showing {len(pending_leads)} lead(s) ready for review or outreach delivery.")

        for lead in pending_leads:
            with st.container():
                st.markdown(f"""
                <div class="lead-card">
                    <h3>{lead.business_name} <span class="badge-{lead.lead_tier.lower()}">{lead.lead_tier} ({lead.lead_score}/100)</span></h3>
                    <p><b>Category:</b> {lead.category} | <b>Location:</b> {lead.city}, {lead.state} | <b>Instagram:</b> {lead.instagram} | <b>Status:</b> <code>{lead.status}</code></p>
                    <p><b>Why Suitable:</b> {lead.why_suitable}</p>
                    <p><b>Suggested Collaboration:</b> {lead.suggested_collaboration}</p>
                </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([3, 1])

                with col1:
                    edited_msg = st.text_area(
                        f"Personalized DM for {lead.business_name}:",
                        value=lead.personalized_message,
                        height=160,
                        key=f"msg_{lead.lead_id}"
                    )

                with col2:
                    st.write("**Action:**")
                    button_label = "🚀 Send / Retry DM" if lead.status == "APPROVED" else "👍 Approve & Send DM"
                    if st.button(button_label, key=f"app_{lead.lead_id}", use_container_width=True):
                        approval_mgr.approve_lead(lead.lead_id, custom_message=edited_msg)
                        
                        # Trigger live outreach
                        lead_obj = db.get_lead_by_id(lead.lead_id)
                        success, msg = sender.send_outreach(lead_obj)
                        
                        if success:
                            st.success(f"✅ {msg}")
                        else:
                            st.error(f"⚠️ {msg}")
                        st.rerun()

                    if st.button("❌ Reject Lead", key=f"rej_{lead.lead_id}", use_container_width=True):
                        approval_mgr.reject_lead(lead.lead_id, reason="User rejected in dashboard")
                        st.error(f"Rejected '{lead.business_name}'.")
                        st.rerun()

                    handle_clean = lead.instagram.lstrip("@").strip()
                    if handle_clean and handle_clean != "Not Available":
                        ig_url = f"https://ig.me/m/{handle_clean}"
                        st.markdown(f'<a href="{ig_url}" target="_blank" style="display: block; text-align: center; background-color: #E1306C; color: white; padding: 8px; border-radius: 6px; text-decoration: none; font-weight: bold; margin-top: 8px;">💬 Open IG Chat</a>', unsafe_allow_html=True)

                st.markdown("---")

# 3. PIPELINE TRACKER
elif nav_option == "🔄 Pipeline Tracker":
    st.title("🔄 Sponsorship Pipeline Tracker")
    st.caption("Track prospect progression from discovery to conversion")

    all_leads = db.get_all_leads()
    statuses = ["APPROVAL_PENDING", "APPROVED", "CONTACTED", "REPLIED", "INTERESTED", "NEGOTIATING", "CONVERTED", "REJECTED"]
    
    selected_status = st.selectbox("Filter by Status", ["ALL"] + statuses)

    filtered = [l for l in all_leads if selected_status == "ALL" or l.status == selected_status]

    st.write(f"Showing {len(filtered)} leads:")
    for l in filtered:
        with st.expander(f"{l.business_name} ({l.city}) - Status: {l.status} [Score: {l.lead_score}]"):
            st.write(f"**Category:** {l.category}")
            st.write(f"**Instagram:** {l.instagram} | **Website:** {l.website}")
            st.write(f"**Email:** {l.email} | **Phone:** {l.phone}")
            st.write(f"**Growth Signal:** {l.growth_signal}")
            st.write(f"**Outreach DM:**\n{l.personalized_message}")
            st.write(f"**Notes:** {l.notes}")

# 4. ANALYTICS & INSIGHTS
elif nav_option == "📈 Analytics & Insights":
    st.title("📈 Category & Geographic Analytics")
    st.caption("Category conversion rates and geographic distribution")

    metrics = analytics.get_summary_metrics()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Category Distribution")
        cat_df = pd.DataFrame(list(metrics["category_breakdown"].items()), columns=["Category", "Leads"])
        st.bar_chart(cat_df.set_index("Category"))

    with col2:
        st.subheader("Top Cities")
        city_df = pd.DataFrame(list(metrics["city_breakdown"].items()), columns=["City", "Leads"])
        st.bar_chart(city_df.set_index("City"))

# 5. MEDIA PROFILE EDITOR
elif nav_option == "⚙️ Media Profile & Config":
    st.title("⚙️ Configurable Media Profile")
    st.caption("Update initial @news.nit_iit statistics without editing code")

    profile = get_media_profile()

    with st.form("media_profile_form"):
        handle = st.text_input("Instagram Handle", value=profile.instagram_handle)
        followers = st.text_input("Followers Count", value=profile.followers)
        views = st.text_input("Monthly Views", value=profile.monthly_views)
        region = st.text_input("Strong Region", value=profile.strong_region)
        positioning = st.text_area("Page Positioning", value=profile.positioning)

        submitted = st.form_submit_button("Save Profile Settings")
        if submitted:
            update_media_profile({
                "instagram_handle": handle,
                "followers": followers,
                "monthly_views": views,
                "strong_region": region,
                "positioning": positioning
            })
            st.success("Successfully updated MEDIA_PROFILE configuration!")
