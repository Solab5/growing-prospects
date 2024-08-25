class MetricsCalculator:
    @staticmethod
    def calculate_operational_cash_flow(df):
        return df.groupby('MonthName')['AmountContributed'].sum().reset_index()

    @staticmethod
    def calculate_commitment_fee_analysis(monthly_df, members_df):
        analysis = monthly_df.groupby('MemberID')['CommitmentFeePaid'].sum().reset_index()
        return analysis.merge(members_df, on='MemberID')

    @staticmethod
    def calculate_total_contribution_analysis(monthly_df, members_df):
        monthly_df['TotalContribution'] = monthly_df['AmountContributed'] + monthly_df['CommitmentFeePaid']
        analysis = monthly_df.groupby('MemberID')['TotalContribution'].sum().reset_index()
        return analysis.merge(members_df, on='MemberID')

    @staticmethod
    def calculate_admin_fee_analysis(monthly_df, admin_costs_df):
        admin_fee_collected = monthly_df.groupby('MonthName')['AdminFeePaid'].sum().reset_index()
        admin_fee_spent = admin_costs_df.groupby('MonthName')['AmountSpent'].sum().reset_index()
        analysis = admin_fee_collected.merge(admin_fee_spent, on='MonthName', how='outer').fillna(0)
        analysis['NetAdminFee'] = analysis['AdminFeePaid'] - analysis['AmountSpent']
        return analysis
    
    @staticmethod
    def calculate_disbursement_analysis(df):
        return df.groupby('MonthName')['AmountDisbursed'].sum().reset_index()

    @staticmethod
    def calculate_summary_metrics(monthly_df, disbursement_df, admin_costs_df):
        total_contributions = monthly_df['AmountContributed'].sum()
        total_disbursements = disbursement_df['AmountDisbursed'].sum()
        total_admin_costs = admin_costs_df['AmountSpent'].sum()
        net_position = total_contributions - total_disbursements - total_admin_costs
        return {
            'Total Contributions': total_contributions,
            'Total Disbursements': total_disbursements,
            'Total Admin Costs': total_admin_costs,
            'Net Position': net_position
        }