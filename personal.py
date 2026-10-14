"""ShayarArea Open Mic Command Center - demo by Utkarsh Pandey (all data is fictional)."""
import random
from datetime import date, datetime, timedelta
from urllib.parse import quote

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ShayarArea Command Center", page_icon="🎤", layout="wide")
st.markdown("<style>.block-container{padding-top:2rem;max-width:1150px}</style>", unsafe_allow_html=True)

# ---- Easy to change for a real event ----
BRAND = "ShayarArea"
EVENT_NAME = "Open Mic Night"
VENUE = "Bhopal"
TODAY = date.today()
EVENT_DATE = TODAY + timedelta(days=7)
# -----------------------------------------
CATS = ["Poet", "Shayar", "Comedian", "Storyteller"]
STATUSES = ["Confirmed", "Pending", "Rescheduled", "Cancelled"]
COLORS = {"Confirmed": "#d1fae5", "Pending": "#fef3c7", "Rescheduled": "#dbeafe", "Cancelled": "#fee2e2"}
BUDGET = {"Tickets": 60000, "Stay": 40000, "Local Transport": 12000, "Food": 15000, "Miscellaneous": 6000}
OTHER_ACTUAL = {"Stay": 31500, "Local Transport": 8800, "Food": 12400, "Miscellaneous": 6900}
inr = lambda x: f"₹{x:,.0f}"


def show(df, **kw):
    """Full-width table that works on old and new Streamlit versions."""
    try:
        st.dataframe(df, hide_index=True, width="stretch", **kw)
    except Exception:
        st.dataframe(df, hide_index=True, use_container_width=True, **kw)


@st.cache_data
def make_data():
    r = random.Random(7)
    first = ["Aarav", "Riya", "Kabir", "Ananya", "Vihaan", "Isha", "Arjun", "Meera", "Rohan", "Sneha", "Karan", "Tanvi", "Dev", "Pooja", "Nikhil", "Zoya"]
    last = ["Sharma", "Verma", "Patel", "Singh", "Mishra", "Joshi", "Gupta", "Iyer", "Khan", "Nair", "Qureshi", "Dubey"]
    cities = ["Indore", "Jaipur", "Delhi", "Mumbai", "Pune", "Lucknow", "Nagpur", "Ahmedabad", "Hyderabad", "Kolkata", "Raipur", "Jabalpur"]
    n_perf = 24
    order = list(range(n_perf))
    r.shuffle(order)
    base = datetime.combine(EVENT_DATE, datetime.min.time()).replace(hour=18)
    perf = []
    for n in range(n_perf):
        city, mode = r.choice(cities), r.choice(["Train", "Train", "Flight", "Bus"])
        cost = {"Train": r.randint(600, 2500), "Flight": r.randint(3500, 8000), "Bus": r.randint(500, 1500)}[mode]
        status = r.choices(STATUSES, [60, 25, 10, 5])[0]
        slot = base + timedelta(minutes=10 * order[n])
        perf.append({"ID": f"SA{n + 1:03d}", "Performer": f"{r.choice(first)} {r.choice(last)}", "Category": r.choice(CATS),
                     "From": city, "Slot": f"{slot:%I:%M %p}", "Arrive By": f"{slot - timedelta(minutes=60):%I:%M %p}",
                     "Mode": mode, "Travel Date": EVENT_DATE - timedelta(days=r.randint(0, 2)), "Ticket Status": status,
                     "Stay": "Booked" if status == "Confirmed" and r.random() < .85 else "Pending", "Ticket Cost": cost,
                     "Phone": f"9{r.randint(100000000, 999999999)}",
                     "Last Contacted": TODAY - timedelta(days=r.randint(0, 6)),
                     "Next Follow-up": TODAY + timedelta(days=r.randint(-2, 3))})
    perf = pd.DataFrame(perf).sort_values("Slot", key=lambda s: pd.to_datetime(s, format="%I:%M %p")).reset_index(drop=True)
    comments = ["Loved the stage and the crowd.", "Travel details came a bit late.", "Very responsive on calls.",
                "Sound check was quick and smooth.", "Needed more clarity on my slot time.", "Great coordination overall.",
                "Stay was comfortable and close to the venue."]
    feedback = pd.DataFrame([{"Performer": r.choice(perf["Performer"].tolist()),
                              "Category": r.choice(["Travel", "Stay", "Communication", "Stage & Sound"]),
                              "Rating": r.choices([1, 2, 3, 4, 5], [2, 5, 15, 40, 38])[0], "Comment": r.choice(comments)} for _ in range(40)])
    issues = pd.DataFrame([
        {"Performer": perf.loc[2, "Performer"], "Issue": "Train delayed by 3 hrs", "Priority": "High", "Status": "Open"},
        {"Performer": perf.loc[7, "Performer"], "Issue": "Flight rescheduled by airline", "Priority": "High", "Status": "Open"},
        {"Performer": perf.loc[11, "Performer"], "Issue": "Name mismatch on ticket", "Priority": "Medium", "Status": "Open"},
        {"Performer": perf.loc[15, "Performer"], "Issue": "Needs an extra hotel night", "Priority": "Low", "Status": "Resolved"},
        {"Performer": perf.loc[19, "Performer"], "Issue": "Not reachable on phone", "Priority": "Medium", "Status": "Open"}])
    return perf, feedback, issues


if "data_ready" not in st.session_state:
    p, f, i = make_data()
    st.session_state.update(data_ready=True, data_perf=p.copy(), data_feedback=f.copy(), data_issues=i.copy(), data_log=[])


def log(msg):
    st.session_state.data_log.append(f"{datetime.now():%H:%M} - {msg}")


def fu_flag(d):
    return "🔴 Overdue" if d < TODAY else "🟡 Due today" if d == TODAY else "🟢 Upcoming"


def ready(row):
    if row["Ticket Status"] == "Cancelled":
        return "❌ Cancelled"
    return "✅ Ready" if row["Ticket Status"] == "Confirmed" and row["Stay"] == "Booked" else "⏳ In progress"


perf, feedback, issues = st.session_state.data_perf, st.session_state.data_feedback, st.session_state.data_issues
perf["Ready"] = perf.apply(ready, axis=1)
ticket_spend = int(perf[perf["Ticket Status"] != "Cancelled"]["Ticket Cost"].sum())
due_mask = perf["Next Follow-up"].map(lambda d: d <= TODAY)
overdue_mask = perf["Next Follow-up"].map(lambda d: d < TODAY)

with st.sidebar:
    st.title(f"🎤 {BRAND}")
    st.caption("Demo command center with fictional data: performer travel, slots, follow-ups, issues, feedback and daily reports.")
    st.markdown("**Built by Utkarsh Pandey**  \nBhopal, Madhya Pradesh  \n[LinkedIn](https://www.linkedin.com/in/utkarsh-pandey-255b21366/)")
    st.info(f"{EVENT_NAME}: **{EVENT_DATE:%d %b %Y}**, {VENUE}  \n{(EVENT_DATE - TODAY).days} days to go")
    if st.button("Reset demo data"):
        st.session_state.clear()
        st.rerun()

st.title(f"{BRAND} Command Center")
st.caption("Every performer's travel, slot, follow-up and feedback in one place, so everything stays on time and on track.")
tab_over, tab_perf, tab_follow, tab_if, tab_report = st.tabs(["Overview", "Performers", "Follow-ups", "Issues & Feedback", "Daily Report"])

# ---------------- Overview ----------------
with tab_over:
    c = st.columns(4)
    c[0].metric("Performers", len(perf))
    c[1].metric("Ready for show", f"{(perf['Ready'] == '✅ Ready').mean() * 100:.0f}%")
    c[2].metric("Pending tickets", int((perf["Ticket Status"] == "Pending").sum()))
    c[3].metric("Open issues", int((issues["Status"] == "Open").sum()))
    mix = perf["Category"].value_counts()
    st.caption(" · ".join(f"{k}s: {v}" for k, v in mix.items()))
    left, right = st.columns([3, 2], gap="large")
    with left:
        st.subheader("Needs attention")
        show(perf[perf["Ticket Status"] == "Pending"][["Slot", "Performer", "Category", "From", "Mode"]].head(8))
        if overdue_mask.any():
            st.warning("Follow-ups overdue: " + ", ".join(perf[overdue_mask]["Performer"].head(6)) + (" ..." if overdue_mask.sum() > 6 else ""))
    with right:
        st.subheader("Ticket status")
        st.bar_chart(perf["Ticket Status"].value_counts())
    with st.expander("Budget"):
        actual = {"Tickets": ticket_spend, **OTHER_ACTUAL}
        tb, ta = sum(BUDGET.values()), sum(actual.values())
        st.progress(min(ta / tb, 1.0), text=f"{inr(ta)} spent of {inr(tb)} ({ta / tb * 100:.0f}%)")
        exp = pd.DataFrame({"Category": list(BUDGET), "Budget": list(BUDGET.values()), "Actual": [actual[k] for k in BUDGET]})
        exp["Status"] = ["🔴 Over" if a > b else "🟢 OK" for a, b in zip(exp["Actual"], exp["Budget"])]
        show(exp)

# ---------------- Performers ----------------
with tab_perf:
    f1, f2, f3, f4 = st.columns([2, 2, 2, 2])
    sel_cat = f1.multiselect("Category", CATS)
    sel_status = f2.multiselect("Ticket status", STATUSES)
    q = f3.text_input("Search name")
    mode_view = f4.radio("View", ["Travel", "Line-up"], horizontal=True)
    view = perf.copy()
    if sel_cat: view = view[view["Category"].isin(sel_cat)]
    if sel_status: view = view[view["Ticket Status"].isin(sel_status)]
    if q: view = view[view["Performer"].str.contains(q, case=False)]
    if mode_view == "Travel":
        t = view[["ID", "Performer", "Category", "From", "Mode", "Travel Date", "Ticket Status", "Stay"]]
        styler = t.style
        paint = styler.map if hasattr(styler, "map") else styler.applymap
        show(paint(lambda v: f"background-color: {COLORS[v]}; color: #1f2937; font-weight: 600" if v in COLORS else "", subset=["Ticket Status"]))
    else:
        show(view[["Slot", "Performer", "Category", "From", "Arrive By", "Ready"]])
    st.caption(f"{len(view)} of {len(perf)} performers")
    st.download_button("Download CSV", view.drop(columns=["Phone"]).to_csv(index=False), "performers.csv", "text/csv")
    with st.expander("Update a record"):
        names = dict(zip(perf["ID"], perf["Performer"]))
        with st.form("form_update"):
            u1, u2, u3 = st.columns(3)
            pid = u1.selectbox("Performer", perf["ID"], format_func=lambda i: f"{names[i]} ({i})")
            new_status = u2.selectbox("Ticket status", STATUSES)
            new_stay = u3.selectbox("Stay", ["Booked", "Pending"])
            if st.form_submit_button("Save"):
                perf.loc[perf["ID"] == pid, ["Ticket Status", "Stay"]] = [new_status, new_stay]
                log(f"{names[pid]}: ticket {new_status}, stay {new_stay}")
                st.rerun()

# ---------------- Follow-ups ----------------
with tab_follow:
    templates = {
        "Travel confirmation": "Hi {c}, this is Utkarsh from the {b} team. Your ticket from {city} to {v} is confirmed. Please check the details and reply OK.",
        "Slot reminder": "Hi {c}, reminder: {b} open mic is on {d}. Your slot is at {slot}. Please reach the venue by {arr} for sound check.",
        "Delay notice": "Hi {c}, we noticed a delay on your travel. We are arranging an alternative and will update you shortly.",
        "Feedback request": "Hi {c}, thank you for performing at {b}! Please share quick feedback on travel, stay and the show.",
    }
    only_due = st.checkbox("Show only due or overdue")
    tpl = st.selectbox("Message template", list(templates))
    fmt = lambda row: templates[tpl].format(c=row["Performer"].split()[0], b=BRAND, city=row["From"], v=VENUE,
                                            d=f"{EVENT_DATE:%d %b}", slot=row["Slot"], arr=row["Arrive By"])
    board = perf[due_mask] if only_due else perf
    board = board.copy()
    board["Follow-up"] = board["Next Follow-up"].map(fu_flag)
    board["WhatsApp"] = ["https://wa.me/91" + row["Phone"] + "?text=" + quote(fmt(row)) for _, row in board.iterrows()]
    show(board[["Performer", "Category", "Phone", "Follow-up", "WhatsApp"]],
         column_config={"WhatsApp": st.column_config.LinkColumn("WhatsApp", display_text="Open chat")})
    m1, m2 = st.columns(2, gap="large")
    names = dict(zip(perf["ID"], perf["Performer"]))
    pick = m1.selectbox("Performer", perf["ID"], format_func=lambda i: names[i], key="follow_pick")
    if m1.button("Mark as contacted"):
        perf.loc[perf["ID"] == pick, ["Last Contacted", "Next Follow-up"]] = [TODAY, TODAY + timedelta(days=2)]
        log(f"Contacted {names[pick]}; next follow-up in 2 days")
        st.rerun()
    m2.caption("Message preview")
    m2.code(fmt(perf[perf["ID"] == pick].iloc[0]), language=None)

# ---------------- Issues & Feedback ----------------
with tab_if:
    a, b = st.columns(2, gap="large")
    with a:
        st.subheader("Issues")
        show(issues)
        st.caption("High priority issues are escalated to the organiser immediately.")
        with st.expander("Log or resolve an issue"):
            with st.form("form_issue"):
                it = st.selectbox("Performer", perf["Performer"])
                txt = st.text_input("Issue")
                pr = st.selectbox("Priority", ["High", "Medium", "Low"])
                if st.form_submit_button("Log issue") and txt:
                    st.session_state.data_issues = pd.concat(
                        [issues, pd.DataFrame([{"Performer": it, "Issue": txt, "Priority": pr, "Status": "Open"}])], ignore_index=True)
                    log(f"Issue for {it}: {txt} ({pr})" + (" - ESCALATED" if pr == "High" else ""))
                    st.rerun()
            open_rows = issues[issues["Status"] == "Open"]
            if len(open_rows):
                with st.form("form_resolve"):
                    rid = st.selectbox("Open issue", open_rows.index, format_func=lambda i: f"{open_rows.loc[i, 'Performer']}: {open_rows.loc[i, 'Issue']}")
                    if st.form_submit_button("Mark resolved"):
                        issues.loc[rid, "Status"] = "Resolved"
                        log(f"Issue resolved: {issues.loc[rid, 'Issue']}")
                        st.rerun()
    with b:
        st.subheader("Performer feedback")
        st.metric("Average rating", f"{feedback['Rating'].mean():.2f} / 5", f"{len(feedback)} responses", delta_color="off")
        st.bar_chart(feedback.groupby("Category")["Rating"].mean().round(2))
        with st.expander("Low ratings to follow up"):
            show(feedback[feedback["Rating"] <= 2])
        with st.expander("Add feedback"):
            with st.form("form_feedback"):
                ft = st.selectbox("Performer", perf["Performer"])
                fc = st.selectbox("Category", ["Travel", "Stay", "Communication", "Stage & Sound"])
                fr = st.slider("Rating", 1, 5, 4)
                fcm = st.text_input("Comment")
                if st.form_submit_button("Submit"):
                    st.session_state.data_feedback = pd.concat(
                        [feedback, pd.DataFrame([{"Performer": ft, "Category": fc, "Rating": fr, "Comment": fcm}])], ignore_index=True)
                    log(f"Feedback from {ft} ({fr} stars)")
                    st.rerun()

# ---------------- Daily Report ----------------
with tab_report:
    counts = perf["Ticket Status"].value_counts()
    pend = perf[perf["Ticket Status"] == "Pending"]
    spent = ticket_spend + sum(OTHER_ACTUAL.values())
    actions = "\n".join("- " + l for l in st.session_state.data_log) or "- (none yet - update records in the other tabs)"
    report = f"""{BRAND.upper()} - DAILY STATUS REPORT - {TODAY:%d %b %Y}
Prepared by: Utkarsh Pandey | {EVENT_NAME}: {EVENT_DATE:%d %b %Y}, {VENUE}

PERFORMERS
- {len(perf)} performers: {', '.join(f'{v} {k.lower()}s' for k, v in perf['Category'].value_counts().items())}
- Ready for show: {int((perf['Ready'] == '✅ Ready').sum())} | In progress: {int((perf['Ready'] == '⏳ In progress').sum())} | Cancelled: {int((perf['Ready'] == '❌ Cancelled').sum())}

TRAVEL
- Confirmed: {counts.get('Confirmed', 0)} | Pending: {counts.get('Pending', 0)} | Rescheduled: {counts.get('Rescheduled', 0)} | Cancelled: {counts.get('Cancelled', 0)}
- Stay pending: {int((perf['Stay'] == 'Pending').sum())}
- Pending tickets: {', '.join(pend['Performer'] + ' (' + pend['Slot'] + ')') or 'None'}

FOLLOW-UPS
- Overdue: {', '.join(perf[overdue_mask]['Performer']) or 'None'}

ISSUES
- Open: {int((issues['Status'] == 'Open').sum())} (High priority: {int(((issues['Status'] == 'Open') & (issues['Priority'] == 'High')).sum())})

FEEDBACK
- Average rating: {feedback['Rating'].mean():.2f}/5 from {len(feedback)} responses

BUDGET
- Spent {inr(spent)} of {inr(sum(BUDGET.values()))}

ACTIONS TAKEN TODAY
{actions}"""
    st.text_area("Auto-generated report", report, height=480)
    st.download_button("Download report (.txt)", report, f"shayararea_report_{TODAY}.txt")
