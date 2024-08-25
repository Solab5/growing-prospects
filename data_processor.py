import pandas as pd

class DataProcessor:
    @staticmethod
    def create_dataframe(data):
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])

    @staticmethod
    def extract_month(df, date_column):
        df[date_column] = pd.to_datetime(df[date_column])
        df['Month'] = df[date_column].dt.month
        df['MonthName'] = df[date_column].dt.strftime('%B')
        return df

    @staticmethod
    def convert_to_float(df, columns):
        for col in columns:
            df[col] = df[col].astype(float)
        return df