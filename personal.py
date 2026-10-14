"""Contest Travel Command Center - portfolio project by Utkarsh Pandey (all data is fictional)."""
import random
from datetime import date, datetime, timedelta
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Contest Travel Command Center", page_icon="🧭", layout="wide")
st.markdown("<style>.block-container{padding-top:2rem;max-width:1150px}</style>", unsafe_allow_html=True)

TODAY = date.today()
EVENT_DATE = TODAY + timedelta(days=7)
VENUE = "Bhopal"
STATUSES = ["Confirmed", "Pending", "Rescheduled", "Cancelled"]
COLORS = {"Confirmed": "#d1fae5", "Pending": "#fef3c7", "Rescheduled": "#dbeafe", "Cancelled": "#fee2e2"}
BUDGET = {"Tickets": 150000, "Stay": 90000, "Local Transport": 30000, "Food": 40000, "Miscellaneous": 15000}
OTHER_ACTUAL = {"Stay": 71500, "Local Transport": 22800, "Food": 31200, "Miscellaneous": 16400}
inr = lambda x: f"₹{x:,.0f}"


def show(df, **kw):
    """Full-width table that works on old and new Streamlit versions."""
    try:
        st.dataframe(df, hide_index=True, width="stretch", **kw)
    except Exception:
        st.dataframe(df, hide_index=True, use_container_width=True, **kw)


@st.cache_data
def make_data():
    r = random.Random(42)
    first = ["Aarav", "Riya", "Kabir", "Ananya", "Vihaan", "Isha", "Arjun", "Meera", "Rohan", "Sneha", "Karan", "Tanvi", "Dev", "Pooja", "Nikhil"]
    last = ["Sharma", "Verma", "Patel", "Singh", "Mishra", "Joshi", "Gupta", "Iyer", "Khan", "Nair"]
    src = [("Team Phoenix", "Indore"), ("Code Titans", "Jaipur"), ("Pixel Pirates", "Delhi"), ("Byte Brigade", "Mumbai"),
           ("Neon Nerds", "Pune"), ("Alpha Squad", "Lucknow"), ("Quantum Quest", "Nagpur"), ("Rapid Rockets", "Ahmedabad"),
           ("Data Dynamos", "Hyderabad"), ("Logic Lions", "Bengaluru"), ("Cyber Chiefs", "Kolkata"), ("Zen Zebras", "Raipur")]
    teams, trav, n = [], [], 1
    for name, city in src:
        teams.append({"Team": name, "City": city, "Captain": f"{r.choice(first)} {r.choice(last)}",
                      "Phone": f"9{r.randint(100000000, 999999999)}",
                      "Last Contacted": TODAY - timedelta(days=r.randint(0, 6)),
                      "Next Follow-up": TODAY + timedelta(days=r.randint(-2, 3))})
        for _ in range(r.randint(3, 5)):
            mode = r.choice(["Train", "Train", "Flight", "Bus"])
            cost = {"Train": r.randint(600, 2500), "Flight": r.randint(3500, 8000), "Bus": r.randint(500, 1500)}[mode]
            status = r.choices(STATUSES, [60, 25, 10, 5])[0]
            trav.append({"ID": f"TR{n:03d}", "Team": name, "Name": f"{r.choice(first)} {r.choice(last)}", "From": city,
                         "Mode": mode, "Travel Date": EVENT_DATE - timedelta(days=r.randint(1, 2)),
                         "Ticket Status": status, "Stay": "Booked" if status == "Confirmed" and r.random() < .85 else "Pending",
                         "Ticket Cost": cost})
            n += 1
    comments = ["Smooth pickup and clear updates.", "Ticket info came a bit late.", "Very responsive on calls.",
                "Hotel check-in was quick.", "Needed more clarity on timings.", "Great coordination overall.", "Food arrangement was good."]
    feedback = pd.DataFrame([{"Team": r.choice(src)[0], "Category": r.choice(["Travel", "Stay", "Coordination", "Food"]),
                              "Rating": r.choices([1, 2, 3, 4, 5], [2, 5, 15, 40, 38])[0], "Comment": r.choice(comments)} for _ in range(40)])
    issues = pd.DataFrame([
        {"Team": "Code Titans", "Issue": "Train delayed by 3 hrs", "Priority": "High", "Status": "Open"},
        {"Team": "Pixel Pirates", "Issue": "Flight rescheduled by airline", "Priority": "High", "Status": "Open"},
        {"Team": "Neon Nerds", "Issue": "Name mismatch on ticket", "Priority": "Medium", "Status": "Open"},
        {"Team": "Zen Zebras", "Issue": "Hotel needs 2 extra beds", "Priority": "Low", "Status": "Resolved"},
        {"Team": "Alpha Squad", "Issue": "Captain not reachable", "Priority": "Medium", "Status": "Open"}])
    return pd.DataFrame(trav), pd.DataFrame(teams), feedback, issues


if "data_ready" not in st.session_state:
    t, tm, f, i = make_data()
    st.session_state.update(data_ready=True, data_trav=t.copy(), data_teams=tm.copy(),
                            data_feedback=f.copy(), data_issues=i.copy(), data_log=[])


def log(msg):
    st.session_state.data_log.append(f"{datetime.now():%H:%M} - {msg}")


def fu_flag(d):
    return "🔴 Overdue" if d < TODAY else "🟡 Due today" if d == TODAY else "🟢 Upcoming"


tr, teams = st.session_state.data_trav, st.session_state.data_teams
feedback, issues = st.session_state.data_feedback, st.session_state.data_issues
ticket_spend = int(tr[tr["Ticket Status"] != "Cancelled"]["Ticket Cost"].sum())

with st.sidebar:
    st.title("🧭 Travel Command Center")
    st.caption("Demo tool with fictional data: travel tracking, team follow-ups, issues, feedback and daily reporting.")
    st.markdown("**Built by Utkarsh Pandey**  \nBhopal, Madhya Pradesh  \n[LinkedIn](https://www.linkedin.com/in/utkarsh-pandey-255b21366/)")
    st.info(f"Contest day: **{EVENT_DATE:%d %b %Y}**  \n{(EVENT_DATE - TODAY).days} days to go")
    if st.button("Reset demo data"):
        st.session_state.clear()
        st.rerun()

st.title("Contest Travel Command Center")
tab_over, tab_travel, tab_teams, tab_if, tab_report = st.tabs(["Overview", "Travel", "Teams", "Issues & Feedback", "Daily Report"])

# ---------------- Overview ----------------
with tab_over:
    open_issues = int((issues["Status"] == "Open").sum())
    c = st.columns(4)
    c[0].metric("Travellers", len(tr))
    c[1].metric("Tickets confirmed", f"{(tr['Ticket Status'] == 'Confirmed').mean() * 100:.0f}%")
    c[2].metric("Pending tickets", int((tr["Ticket Status"] == "Pending").sum()))
    c[3].metric("Open issues", open_issues)
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Needs attention")
        show(tr[tr["Ticket Status"] == "Pending"][["Team", "Name", "Mode", "Travel Date"]].head(8))
        overdue = teams[teams["Next Follow-up"] < TODAY]["Team"].tolist()
        if overdue:
            st.warning("Follow-ups overdue: " + ", ".join(overdue))
    with right:
        st.subheader("Ticket status")
        st.bar_chart(tr["Ticket Status"].value_counts())
    with st.expander("Budget"):
        actual = {"Tickets": ticket_spend, **OTHER_ACTUAL}
        tb, ta = sum(BUDGET.values()), sum(actual.values())
        st.progress(min(ta / tb, 1.0), text=f"{inr(ta)} spent of {inr(tb)} ({ta / tb * 100:.0f}%)")
        exp = pd.DataFrame({"Category": list(BUDGET), "Budget": list(BUDGET.values()), "Actual": [actual[k] for k in BUDGET]})
        exp["Status"] = ["🔴 Over" if a > b else "🟢 OK" for a, b in zip(exp["Actual"], exp["Budget"])]
        show(exp)

# ---------------- Travel ----------------
with tab_travel:
    f1, f2, f3 = st.columns(3)
    sel_team = f1.multiselect("Team", sorted(tr["Team"].unique()))
    sel_status = f2.multiselect("Ticket status", STATUSES)
    q = f3.text_input("Search name")
    view = tr.drop(columns=["Ticket Cost"])
    if sel_team: view = view[view["Team"].isin(sel_team)]
    if sel_status: view = view[view["Ticket Status"].isin(sel_status)]
    if q: view = view[view["Name"].str.contains(q, case=False)]
    styler = view.style
    paint = styler.map if hasattr(styler, "map") else styler.applymap
    show(paint(lambda v: f"background-color: {COLORS[v]}" if v in COLORS else "", subset=["Ticket Status"]))
    st.caption(f"{len(view)} of {len(tr)} travellers")
    st.download_button("Download CSV", view.to_csv(index=False), "travel_tracker.csv", "text/csv")
    with st.expander("Update a record"):
        with st.form("form_update"):
            u1, u2, u3 = st.columns(3)
            tid = u1.selectbox("Traveller ID", tr["ID"])
            new_status = u2.selectbox("Ticket status", STATUSES)
            new_stay = u3.selectbox("Stay", ["Booked", "Pending"])
            if st.form_submit_button("Save"):
                tr.loc[tr["ID"] == tid, ["Ticket Status", "Stay"]] = [new_status, new_stay]
                log(f"{tid} updated: ticket {new_status}, stay {new_stay}")
                st.rerun()

# ---------------- Teams ----------------
with tab_teams:
    templates = {
        "Travel confirmation": "Hi {c}, this is Utkarsh from the contest travel desk. Tickets for {t} to {v} are confirmed. Please check the details and reply OK.",
        "Reminder": "Hi {c}, a quick reminder: contest day is {d}. Please share your final arrival time at {v}.",
        "Delay notice": "Hi {c}, we noticed a delay for {t}. We are arranging an alternative and will update you shortly.",
        "Feedback request": "Hi {c}, thank you for being part of the contest! Please share your quick feedback with us.",
    }
    tpl = st.selectbox("Message template", list(templates))
    fmt = lambda row: templates[tpl].format(c=row["Captain"].split()[0], t=row["Team"], v=VENUE, d=f"{EVENT_DATE:%d %b}")
    board = teams.copy()
    board["Follow-up"] = board["Next Follow-up"].map(fu_flag)
    board["WhatsApp"] = ["https://wa.me/91" + row["Phone"] + "?text=" + quote(fmt(row)) for _, row in board.iterrows()]
    show(board[["Team", "Captain", "Phone", "Follow-up", "WhatsApp"]],
         column_config={"WhatsApp": st.column_config.LinkColumn("WhatsApp", display_text="Open chat")})
    m1, m2 = st.columns(2, gap="large")
    pick = m1.selectbox("Team", teams["Team"])
    if m1.button("Mark as contacted"):
        teams.loc[teams["Team"] == pick, ["Last Contacted", "Next Follow-up"]] = [TODAY, TODAY + timedelta(days=2)]
        log(f"Contacted {pick}; next follow-up in 2 days")
        st.rerun()
    m2.caption("Message preview")
    m2.code(fmt(teams[teams["Team"] == pick].iloc[0]), language=None)

# ---------------- Issues & Feedback ----------------
with tab_if:
    a, b = st.columns(2, gap="large")
    with a:
        st.subheader("Issues")
        show(issues)
        st.caption("High priority issues are escalated to the coordinator immediately.")
        with st.expander("Log or resolve an issue"):
            with st.form("form_issue"):
                it = st.selectbox("Team", teams["Team"])
                txt = st.text_input("Issue")
                pr = st.selectbox("Priority", ["High", "Medium", "Low"])
                if st.form_submit_button("Log issue") and txt:
                    st.session_state.data_issues = pd.concat(
                        [issues, pd.DataFrame([{"Team": it, "Issue": txt, "Priority": pr, "Status": "Open"}])], ignore_index=True)
                    log(f"Issue logged for {it}: {txt} ({pr})" + (" - ESCALATED" if pr == "High" else ""))
                    st.rerun()
            open_rows = issues[issues["Status"] == "Open"]
            if len(open_rows):
                with st.form("form_resolve"):
                    rid = st.selectbox("Open issue", open_rows.index, format_func=lambda i: f"{open_rows.loc[i, 'Team']}: {open_rows.loc[i, 'Issue']}")
                    if st.form_submit_button("Mark resolved"):
                        issues.loc[rid, "Status"] = "Resolved"
                        log(f"Issue resolved: {issues.loc[rid, 'Issue']}")
                        st.rerun()
    with b:
        st.subheader("Feedback")
        st.metric("Average rating", f"{feedback['Rating'].mean():.2f} / 5", f"{len(feedback)} responses", delta_color="off")
        st.bar_chart(feedback.groupby("Category")["Rating"].mean().round(2))
        with st.expander("Low ratings to follow up"):
            show(feedback[feedback["Rating"] <= 2])
        with st.expander("Add feedback"):
            with st.form("form_feedback"):
                ft = st.selectbox("Team", teams["Team"])
                fc = st.selectbox("Category", ["Travel", "Stay", "Coordination", "Food"])
                fr = st.slider("Rating", 1, 5, 4)
                fcm = st.text_input("Comment")
                if st.form_submit_button("Submit"):
                    st.session_state.data_feedback = pd.concat(
                        [feedback, pd.DataFrame([{"Team": ft, "Category": fc, "Rating": fr, "Comment": fcm}])], ignore_index=True)
                    log(f"Feedback added from {ft} ({fr} stars)")
                    st.rerun()

# ---------------- Daily Report ----------------
with tab_report:
    counts = tr["Ticket Status"].value_counts()
    pend = tr[tr["Ticket Status"] == "Pending"]
    spent = ticket_spend + sum(OTHER_ACTUAL.values())
    actions = "\n".join("- " + l for l in st.session_state.data_log) or "- (none yet - update records in the other tabs)"
    report = f"""DAILY STATUS REPORT - {TODAY:%d %b %Y}
Prepared by: Utkarsh Pandey | Contest: {EVENT_DATE:%d %b %Y}, {VENUE}

TRAVEL
- {len(tr)} travellers across {len(teams)} teams
- Confirmed: {counts.get('Confirmed', 0)} | Pending: {counts.get('Pending', 0)} | Rescheduled: {counts.get('Rescheduled', 0)} | Cancelled: {counts.get('Cancelled', 0)}
- Stay pending: {int((tr['Stay'] == 'Pending').sum())} travellers
- Pending tickets: {', '.join(pend['Name'] + ' (' + pend['Team'] + ')') or 'None'}

FOLLOW-UPS
- Overdue: {', '.join(teams[teams['Next Follow-up'] < TODAY]['Team']) or 'None'}
- Due today: {', '.join(teams[teams['Next Follow-up'] == TODAY]['Team']) or 'None'}

ISSUES
- Open: {int((issues['Status'] == 'Open').sum())} (High priority: {int(((issues['Status'] == 'Open') & (issues['Priority'] == 'High')).sum())})

FEEDBACK
- Average rating: {feedback['Rating'].mean():.2f}/5 from {len(feedback)} responses

BUDGET
- Spent {inr(spent)} of {inr(sum(BUDGET.values()))}

ACTIONS TAKEN TODAY
{actions}"""
    st.text_area("Auto-generated report", report, height=460)
    st.download_button("Download report (.txt)", report, f"daily_report_{TODAY}.txt")
