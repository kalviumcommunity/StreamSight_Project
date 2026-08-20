import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import sys
import logging

# Add export module to path
sys.path.insert(0, str(Path(__file__).parent))
from export.email_delivery import EmailDelivery

logger = logging.getLogger(__name__)


def month_year_from_date_series(s: pd.Series):
    s = pd.to_datetime(s)
    latest = s.max()
    return latest.month, latest.year


def prior_month_year(month: int, year: int):
    if month == 1:
        return 12, year - 1
    return month - 1, year


def percent_change(current, prior):
    if prior == 0 or prior is None:
        return 0.0
    return (current - prior) / prior * 100.0


def get_trend_indicator(change_pct, metric_name):
    # For churn: down is good
    if metric_name == "Churn Rate":
        if change_pct < -2:
            return "↓", "#10b981"  # Green
        elif change_pct > 2:
            return "↑", "#ef4444"  # Red
        else:
            return "→", "#f59e0b"  # Yellow
    else:
        if change_pct > 2:
            return "↑", "#10b981"  # Green
        elif change_pct < -2:
            return "↓", "#ef4444"  # Red
        else:
            return "→", "#f59e0b"  # Yellow


def format_currency(x):
    try:
        return f"${x:,.0f}" if abs(x) >= 1000 else f"${x:,.2f}"
    except Exception:
        return str(x)


def compute_kpis(base: Path | str = None, sales_df=None, engagement_df=None):
    """
    Compute KPIs from provided or cached DataFrames.
    If sales_df and engagement_df are provided, use them instead of loading from disk.
    """
    if sales_df is None or engagement_df is None:
        base = Path(base) if base else Path(__file__).parent
        sales_path = base / "output" / "processed_sales.csv"
        engagement_path = base / "output" / "validated_engagement_data.csv"

        sales_df = pd.read_csv(sales_path, parse_dates=["transaction_date"]) if sales_path.exists() else pd.DataFrame()
        engagement_df = pd.read_csv(engagement_path, parse_dates=["transaction_date"]) if engagement_path.exists() else pd.DataFrame()

    candidates = []
    if not sales_df.empty:
        candidates.append(sales_df["transaction_date"]) 
    if not engagement_df.empty:
        candidates.append(engagement_df["transaction_date"]) 

    if not candidates:
        raise RuntimeError("No data available to compute KPIs")

    all_dates = pd.concat(candidates)
    cur_month, cur_year = month_year_from_date_series(all_dates)
    prior_m, prior_y = prior_month_year(cur_month, cur_year)

    def filter_month(df, month, year):
        if df.empty:
            return df
        s = pd.to_datetime(df["transaction_date"]) 
        return df[(s.dt.month == month) & (s.dt.year == year)]

    sales_cur = filter_month(sales_df, cur_month, cur_year)
    sales_prior = filter_month(sales_df, prior_m, prior_y)

    eng_cur = filter_month(engagement_df, cur_month, cur_year)
    eng_prior = filter_month(engagement_df, prior_m, prior_y)

    # KPI calculations
    current_revenue = sales_cur["amount"].sum()
    prior_revenue = sales_prior["amount"].sum()

    current_users = int(eng_cur["user_id"].nunique()) if not eng_cur.empty else 0
    prior_users = int(eng_prior["user_id"].nunique()) if not eng_prior.empty else 0

    current_aov = float(sales_cur["amount"].mean()) if not sales_cur.empty else 0.0
    prior_aov = float(sales_prior["amount"].mean()) if not sales_prior.empty else 0.0

    # churn based on customers who purchased in prior month but not in current month
    prior_customers = set(sales_prior["customer_id"].unique()) if not sales_prior.empty else set()
    current_customers = set(sales_cur["customer_id"].unique()) if not sales_cur.empty else set()
    if len(prior_customers) == 0:
        current_churn = 0.0
    else:
        lost = len([c for c in prior_customers if c not in current_customers])
        current_churn = (lost / len(prior_customers)) * 100.0

    # prior churn: compute churn between prior and prior-1 (best-effort)
    prior2_m, prior2_y = prior_month_year(prior_m, prior_y)
    sales_prior2 = filter_month(sales_df, prior2_m, prior2_y)
    prior2_customers = set(sales_prior2["customer_id"].unique()) if not sales_prior2.empty else set()
    if len(prior2_customers) == 0:
        prior_churn = 0.0
    else:
        lost_prior = len([c for c in prior2_customers if c not in prior_customers])
        prior_churn = (lost_prior / len(prior2_customers)) * 100.0

    # satisfaction: use completion_rate from engagement data and map to 5-point scale
    def to_star_scale(x):
        return (x / 20.0) if pd.notna(x) else None

    current_satisfaction_raw = eng_cur["completion_rate"].mean() if not eng_cur.empty else 0.0
    prior_satisfaction_raw = eng_prior["completion_rate"].mean() if not eng_prior.empty else 0.0
    current_satisfaction = to_star_scale(current_satisfaction_raw)
    prior_satisfaction = to_star_scale(prior_satisfaction_raw)

    # percent changes
    revenue_change = percent_change(current_revenue, prior_revenue)
    users_change = percent_change(current_users, prior_users)
    aov_change = percent_change(current_aov, prior_aov)
    churn_change = percent_change(current_churn, prior_churn)
    satisfaction_change = percent_change(current_satisfaction_raw, prior_satisfaction_raw)

    kpis = [
        {
            "Metric": "Total Revenue",
            "Current": current_revenue,
            "Prior": prior_revenue,
            "Change_Pct": revenue_change,
        },
        {
            "Metric": "Active Users",
            "Current": current_users,
            "Prior": prior_users,
            "Change_Pct": users_change,
        },
        {
            "Metric": "Average Order Value",
            "Current": current_aov,
            "Prior": prior_aov,
            "Change_Pct": aov_change,
        },
        {
            "Metric": "Churn Rate",
            "Current": current_churn,
            "Prior": prior_churn,
            "Change_Pct": churn_change,
        },
        {
            "Metric": "Customer Satisfaction",
            "Current": current_satisfaction,
            "Prior": prior_satisfaction,
            "Change_Pct": satisfaction_change,
        },
    ]

    df_kpis = pd.DataFrame(kpis)
    df_kpis["Change_Display"] = df_kpis["Change_Pct"].apply(lambda x: f"{x:+.1f}%" if x != 0 else "0%")

    return kpis, df_kpis, (cur_month, cur_year), sales_df, engagement_df


def main():
    # Use compute_kpis to get values then render with Streamlit
    kpis, df_kpis, report_month = compute_kpis()

    st.markdown(f"**Report month:** {report_month[0]}/{report_month[1]}")
    cols = st.columns(5)
    for col, kpi in zip(cols, kpis):
        metric = kpi["Metric"]
        change = kpi["Change_Pct"]
        arrow, color = get_trend_indicator(change, metric)

        if metric == "Total Revenue":
            display_value = format_currency(kpi['Current'])
            delta = f"{change:+.1f}%"
        elif metric == "Average Order Value":
            display_value = format_currency(kpi['Current']) if kpi['Current'] else "$0"
            delta = f"{change:+.1f}%"
        elif metric == "Churn Rate":
            display_value = f"{kpi['Current']:.1f}%"
            delta = f"{change:+.1f}%"
        elif metric == "Customer Satisfaction":
            display_value = f"{kpi['Current']:.1f}/5" if kpi['Current'] is not None else "N/A"
            delta = f"{change:+.1f}%"
        else:
            display_value = f"{kpi['Current']:,}"
            delta = f"{change:+.1f}%"

        with col:
            st.metric(label=metric, value=display_value, delta=delta)
            st.markdown(f"<div style='margin-top:6px'><span style='font-weight:bold'>Trend:</span> <span style='color:{color}'> {arrow} </span></div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("KPI Table")
    st.dataframe(df_kpis.rename(columns={"Change_Pct": "Change_Pct_raw"}))

    st.markdown("**Data Sources:**")
    st.markdown("- Total Revenue: output/processed_sales.csv (sum of `amount` by month)")
    st.markdown("- Active Users: output/validated_engagement_data.csv (unique `user_id` by month)")
    st.markdown("- AOV: output/processed_sales.csv (mean `amount` by month)")
    st.markdown("- Churn Rate: computed from `customer_id` activity across months in output/processed_sales.csv")
    st.markdown("- Customer Satisfaction: `completion_rate` in output/validated_engagement_data.csv mapped to 5-point scale")

    # ============ INSIGHT DELIVERY SECTION ============
    st.divider()
    st.subheader("📧 Insight Delivery - Email Report")
    st.markdown("Send structured KPI reports directly to stakeholders. No manual exports needed.")

    with st.sidebar:
        st.header("Report Actions")
        st.markdown("Generate and email your KPI insights to stakeholders.")

        recipient = st.text_input(
            "Recipient Email",
            placeholder="stakeholder@company.com",
            help="Enter email address to receive the report"
        )

        cc_emails_input = st.text_input(
            "CC Emails (optional)",
            placeholder="email1@company.com, email2@company.com",
            help="Comma-separated list of CC recipients"
        )

        include_csv = st.checkbox("Include CSV attachment", value=True)

        if st.button("📨 Generate & Send Report", type="primary"):
            if not recipient:
                st.sidebar.error("❌ Please enter a recipient email address.")
            else:
                try:
                    # Initialize email delivery
                    email_service = EmailDelivery()

                    # Get data for report
                    kpis_data, _, _, sales_df, engagement_df = compute_kpis()

                    # Combine data for analysis
                    combined_df = pd.DataFrame()
                    if not sales_df.empty:
                        combined_df = sales_df.copy()

                    # Generate structured report
                    additional_kpis_dict = {
                        kpi["Metric"]: f"{kpi['Current']:.2f} ({kpi['Change_Pct']:+.1f}%)"
                        for kpi in kpis_data
                    }

                    report_text = EmailDelivery.generate_structured_report(
                        data_df=combined_df,
                        report_date=datetime.now().date(),
                        segment_column="segment" if "segment" in combined_df.columns else None,
                        revenue_column="amount" if "amount" in combined_df.columns else "revenue",
                        customer_column="customer_id",
                        additional_kpis=additional_kpis_dict
                    )

                    # Prepare attachments
                    attachments = []
                    if include_csv and not combined_df.empty:
                        csv_path = Path(__file__).parent / "output" / "processed_sales.csv"
                        if csv_path.exists():
                            attachments.append(str(csv_path))

                    # Parse CC emails
                    cc_list = None
                    if cc_emails_input:
                        cc_list = [email.strip() for email in cc_emails_input.split(",")]

                    # Send email
                    success = email_service.send_report(
                        recipient_email=recipient,
                        subject=f"Weekly Analytics Report - {datetime.now().strftime('%B %d, %Y')}",
                        body=report_text,
                        attachments=attachments if attachments else None,
                        cc_emails=cc_list
                    )

                    if success:
                        st.sidebar.success(f"✅ Report sent successfully to {recipient}!")
                        st.sidebar.info("💡 Tip: The stakeholder will receive the KPI summary, key findings, and recommended actions in their inbox.")
                    else:
                        st.sidebar.error("❌ Failed to send report. Check your email configuration in .env file.")
                        st.sidebar.info("📝 Configure SENDER_EMAIL and SENDER_PASSWORD in .env file. See .env.example for details.")

                except Exception as e:
                    st.sidebar.error(f"❌ Error: {str(e)}")
                    logger.exception("Failed to send email report")

        st.markdown("---")
        st.markdown("**Email Configuration:**")
        st.markdown("""
        1. Copy `.env.example` to `.env`
        2. Add your SMTP credentials (Gmail app password recommended)
        3. Reports will be sent automatically with this section visible
        """)
        
        if not EmailDelivery().sender_email:
            st.warning("⚠️ Email not configured. Please set up .env file with SENDER_EMAIL and SENDER_PASSWORD.")


if __name__ == "__main__":
    main()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       