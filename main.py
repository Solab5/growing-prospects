import streamlit as st
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import plotly.graph_objects as go
from config import CREDENTIALS_FILE, SHEET_ID, SHEET_NAMES
from google_sheets_service import GoogleSheetsService
from data_processor import DataProcessor
from metrics_calculator import MetricsCalculator

def hide_streamlit_elements():
    """Hide unnecessary Streamlit elements."""
    hide_style = """
        <style>
        div[data-testid="stToolbar"], div[data-testid="stDecoration"], 
        div[data-testid="stStatusWidget"], #MainMenu, header, footer {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        </style>
    """
    st.markdown(hide_style, unsafe_allow_html=True)

@st.cache_data(ttl=60, show_spinner=False)  # Cache for 5 minutes
def load_and_process_data():
    sheets_service = GoogleSheetsService()
    dfs = {sheet_name: DataProcessor.create_dataframe(sheets_service.read_sheet(SHEET_ID, sheet_name)) 
           for sheet_name in SHEET_NAMES}

    members_df = dfs['01_Members']
    monthly_collection_df = dfs['02_MonthlyCollection']
    disbursement_df = dfs['03_Disbursement']
    admin_costs_df = dfs['04_AdministrativeCosts']

    # Process data
    monthly_collection_df = DataProcessor.extract_month(monthly_collection_df, "Date")
    monthly_collection_df = DataProcessor.convert_to_float(monthly_collection_df, ['AmountContributed', 'CommitmentFeePaid', 'AdminFeePaid'])
    disbursement_df = DataProcessor.extract_month(disbursement_df, "Date")
    disbursement_df = DataProcessor.convert_to_float(disbursement_df, ['AmountDisbursed'])
    admin_costs_df = DataProcessor.extract_month(admin_costs_df, "Date")
    admin_costs_df = DataProcessor.convert_to_float(admin_costs_df, ['AmountSpent'])

    # Calculate metrics
    operational_cash_flow = MetricsCalculator.calculate_operational_cash_flow(monthly_collection_df)
    commitment_fee_analysis = MetricsCalculator.calculate_commitment_fee_analysis(monthly_collection_df, members_df)
    total_contribution_analysis = MetricsCalculator.calculate_total_contribution_analysis(monthly_collection_df, members_df)
    admin_fee_analysis = MetricsCalculator.calculate_admin_fee_analysis(monthly_collection_df, admin_costs_df)
    disbursement_analysis = MetricsCalculator.calculate_disbursement_analysis(disbursement_df)
    summary_metrics = MetricsCalculator.calculate_summary_metrics(monthly_collection_df, disbursement_df, admin_costs_df)

    return (members_df, monthly_collection_df, disbursement_df, admin_costs_df,
            operational_cash_flow, commitment_fee_analysis, total_contribution_analysis,
            admin_fee_analysis, disbursement_analysis, summary_metrics)

def main():
    st.set_page_config(
        page_title="Growing Prospects Metrics",
        page_icon="🏦",
        layout="wide"
    )
  
    # Hide Streamlit elements
    hide_streamlit_elements()
  
    # Add custom font and styles
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Oswald:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
        body {
            font-family: 'Oswald', sans-serif;
        }
        h1 {
            font-family: 'Oswald', sans-serif;
            font-weight: 700;
            font-size: 36px;
            text-align: center;
            color: #0066CC;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 30px;
        }
        h2, h3, h4, h5, h6 {
            font-family: 'Oswald', sans-serif;
        }
        .stTabs [data-baseweb="tab-list"] {
            font-family: 'Oswald', sans-serif;
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'Oswald', sans-serif;
        }
        .metric-container {
            height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .metric-label {
            font-size: 14px;
            font-weight: 300;
            text-transform: uppercase;
            margin: 0;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 700;
            margin: 5px 0 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Use styled heading
    st.markdown("<h1>Growing Prospects Metrics Dashboard</h1>", unsafe_allow_html=True)

    # Load and process data (cached)
    (members_df, monthly_collection_df, disbursement_df, admin_costs_df,
     operational_cash_flow, commitment_fee_analysis, total_contribution_analysis,
     admin_fee_analysis, disbursement_analysis, summary_metrics) = load_and_process_data()

    # Add this near the top of the main() function, after st.set_page_config()
    count = st_autorefresh(interval=2000, limit=None, key="fizzbuzzcounter")

    # Display summary metrics
    st.header("Summary Metrics")
    
    col1, col2, col3, col4 = st.columns(4)

    metric_styles = [
        {"label": "Total Contributions", "color": "#E6F3FF", "text_color": "#0066CC"},
        {"label": "Total Disbursements", "color": "#FFF0E6", "text_color": "#CC6600"},
        {"label": "Total Admin Costs", "color": "#E6FFE6", "text_color": "#006600"},
        {"label": "Net Position", "color": "#FFE6E6", "text_color": "#CC0000"}
    ]

    for col, metric in zip([col1, col2, col3, col4], metric_styles):
        col.markdown(
            f"""
            <div style="background-color: {metric['color']}; padding: 10px; border-radius: 5px;">
                <h4 style="color: {metric['text_color']}; margin: 0;">{metric['label']}</h4>
                <p style="font-size: 24px; font-weight: bold; color: {metric['text_color']}; margin: 5px 0;">
                    UGX {summary_metrics[metric['label']]:,.2f}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Add this after the summary metrics section and before the "Financial Analysis" header
    st.header("Spotlight Metrics")
    carousel_metrics = [
        {"label": "Total Members", "value": f"{len(members_df)}"},
        {"label": "Average Contribution", "value": f"UGX {summary_metrics['Total Contributions'] / len(members_df):,.2f}"},
        {"label": "Latest Month", "value": f"{operational_cash_flow['MonthName'].iloc[-1]}"},
        {"label": "Active Contributors", "value": f"{monthly_collection_df['MemberID'].nunique()}"},
    ]

    current_metric = carousel_metrics[count % len(carousel_metrics)]
    st.markdown(
        f"""
        <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; text-align: center;">
            <h3 style="margin-bottom: 10px; color: black;">{current_metric['label']}</h3>
            <p style="font-size: 24px; font-weight: bold; color: black;">{current_metric['value']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Display charts
    st.header("Financial Analysis")
    tab1, tab2, tab3, tab4 = st.tabs(["Cash Flow", "Member Analysis", "Admin Fee", "Disbursements"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            fig_cash_flow = px.bar(operational_cash_flow, x='MonthName', y='AmountContributed', title='Monthly Operational Cash Flow')
            st.plotly_chart(fig_cash_flow, use_container_width=True)
        with col2:
            fig_disbursement = px.bar(disbursement_analysis, x='MonthName', y='AmountDisbursed', title='Monthly Disbursements')
            st.plotly_chart(fig_disbursement, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            fig_commitment = px.scatter(commitment_fee_analysis, x='Name', y='CommitmentFeePaid', title='Commitment Fee by Member')
            st.plotly_chart(fig_commitment, use_container_width=True)
        with col2:
            fig_contribution = px.bar(total_contribution_analysis, x='Name', y='TotalContribution', title='Total Contribution by Member')
            st.plotly_chart(fig_contribution, use_container_width=True)

    with tab3:
        fig_admin = go.Figure()
        fig_admin.add_trace(go.Bar(x=admin_fee_analysis['MonthName'], y=admin_fee_analysis['AdminFeePaid'], name='Admin Fee Collected'))
        fig_admin.add_trace(go.Bar(x=admin_fee_analysis['MonthName'], y=admin_fee_analysis['AmountSpent'], name='Admin Fee Spent'))
        fig_admin.add_trace(go.Scatter(x=admin_fee_analysis['MonthName'], y=admin_fee_analysis['NetAdminFee'], name='Net Admin Fee'))
        fig_admin.update_layout(title='Admin Fee Collection vs Spending', barmode='group')
        st.plotly_chart(fig_admin, use_container_width=True)

    with tab4:
        fig_disbursement_pie = px.pie(disbursement_df, values='AmountDisbursed', names='MemberID', title='Disbursement by Beneficiary')
        st.plotly_chart(fig_disbursement_pie, use_container_width=True)

    # Add navigation bar at the bottom
    st.markdown(
        """
        <style>
        .footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            color: black;
            text-align: center;
            padding: 10px 0;
            font-family: 'Oswald', sans-serif;
        }
        </style>
        <div class="footer">
            <p>© 2024 Growing Prospects. All rights reserved.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()