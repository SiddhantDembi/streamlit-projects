import streamlit as st
from datetime import datetime
import mysql.connector
import pytz
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")
LOGIN_PASSWORD = os.getenv("DB_DATABASE")

# Create a MySQL connection
db_connection = mysql.connector.connect(
    host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
)

# Create a cursor to interact with the database
db_cursor = db_connection.cursor()


# Timestamp Functions
def login_page():
    password = st.text_input("Enter Password", type="password")
    return password


def save_current_datetime(password_entered):
    if password_entered == LOGIN_PASSWORD:

        ist_timezone = pytz.timezone("Asia/Kolkata")
        current_datetime_ist = datetime.now(ist_timezone)

        formatted_date = current_datetime_ist.strftime("%d %B %Y")
        formatted_time = current_datetime_ist.strftime("%I:%M %p").lower()

        next_id_clean_data = get_next_id("clean_data")
        query_clean_data = "INSERT INTO clean_data (ID, Date, Time) VALUES (%s, %s, %s)"
        values_clean_data = (next_id_clean_data, formatted_date, formatted_time)
        db_cursor.execute(query_clean_data, values_clean_data)
        db_connection.commit()

        next_id_raw_data = get_next_id("raw_data")
        query_raw_data = "INSERT INTO raw_data (ID, Date, Time) VALUES (%s, %s, %s)"
        values_raw_data = (next_id_raw_data, formatted_date, formatted_time)
        db_cursor.execute(query_raw_data, values_raw_data)
        db_connection.commit()

        st.success(f"Saved: {formatted_date} {formatted_time} (IST)")
    else:
        st.error("Wrong Password")


def get_next_id(table_name):
    query = f"SELECT MAX(ID) FROM {table_name}"
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    if result[0] is not None:
        return result[0] + 1
    else:
        return 1


def view_previous_entries(table_name, file_name):
    st.subheader(f"Previous Entries")
    query = f"SELECT * FROM {table_name} ORDER BY ID DESC"
    db_cursor.execute(query)
    rows = db_cursor.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=["ID", "Date", "Time"])
        csv_file = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download CSV", data=csv_file, file_name=file_name, mime="text/csv"
        )
        for row in rows:
            st.write(f"ID: {row[0]}")
            st.write(f"Date: {row[1]}")
            st.write(f"Time: {row[2]}")
            st.write("-" * 30)
    else:
        st.write("No entries found.")


def delete_latest_entry(password_entered):
    if password_entered == LOGIN_PASSWORD:
        query_select_clean_data = "SELECT MAX(ID) FROM clean_data"
        db_cursor.execute(query_select_clean_data)
        latest_id_clean_data = db_cursor.fetchone()[0]

        query_select_raw_data = "SELECT MAX(ID) FROM raw_data"
        db_cursor.execute(query_select_raw_data)
        latest_id_raw_data = db_cursor.fetchone()[0]

        if latest_id_clean_data is not None and latest_id_raw_data is not None:
            query_delete_clean_data = "DELETE FROM clean_data WHERE ID = %s"
            db_cursor.execute(query_delete_clean_data, (latest_id_clean_data,))
            db_connection.commit()

            query_delete_raw_data = "DELETE FROM raw_data WHERE ID = %s"
            db_cursor.execute(query_delete_raw_data, (latest_id_raw_data,))
            db_connection.commit()

            st.success("Latest entry deleted from both tables.")
        else:
            st.warning("No entries found to delete in table.")
    else:
        st.error("Wrong Password")


def refresh():
    st.rerun()


# Analysis Functions
def fetch_data(data_type):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE
        )
        cursor = conn.cursor()
        table_name = "raw_data" if data_type == "Raw Data" else "clean_data"
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()

        if not rows:
            st.error("No data fetched from the MySQL database.")
            return None

        columns = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(rows, columns=columns)

        cursor.close()
        conn.close()

        return df

    except mysql.connector.Error as e:
        st.error(f"MySQL Error: {e}")
        return None

    except Exception as e:
        st.error(f"Error fetching data from MySQL database: {e}")
        return None


def total_rows(df):
    if df is not None:
        num_rows = len(df)
        st.write(f"Total number of entries: {num_rows}")


def display_insights(df):
    if df is not None:
        display_monthly_counts(df)
        display_avg_monthly_counts(df)
        display_date_with_highest_count(df)
        display_frequency_with_user_input(df)
        display_days_with_frequency(df)
        display_hourly_frequency(df)


def display_monthly_counts(df):
    if df is not None:
        df["Month_Year"] = pd.to_datetime(df["Date"]).dt.to_period("M")
        monthly_counts = df["Month_Year"].value_counts().sort_index()

        st.write("Total number of entries for each month and year:")
        st.write(monthly_counts)

        plt.figure(figsize=(10, 6))
        monthly_counts.plot(kind="bar")
        plt.title("Total Number of Entries for Each Month and Year")
        plt.xlabel("Month and Year")
        plt.ylabel("Number of Entries")
        st.pyplot(plt)
        st.write("-" * 30)


def display_avg_monthly_counts(df):
    if df is not None:
        df["Month_Year"] = pd.to_datetime(df["Date"]).dt.to_period("M")
        monthly_counts = df["Month_Year"].value_counts().sort_index()
        monthly_avg = monthly_counts.groupby(monthly_counts.index.strftime("%B")).mean()
        month_order = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        monthly_avg.index = pd.CategoricalIndex(
            monthly_avg.index, categories=month_order, ordered=True
        )
        monthly_avg = monthly_avg.sort_index()
        avg_monthly_df = pd.DataFrame(
            {"Month": monthly_avg.index, "Average Count": monthly_avg.values}
        )

        st.write("Average count for each month:")
        st.table(avg_monthly_df)

        plt.figure(figsize=(10, 6))
        plt.bar(avg_monthly_df["Month"], avg_monthly_df["Average Count"])
        plt.title("Average Count for Each Month")
        plt.xlabel("Month")
        plt.ylabel("Average Count")
        plt.xticks(rotation=45, ha="right")
        st.pyplot(plt)

        st.write(
            f"Highest frequency month: {monthly_avg.idxmax()} ({monthly_avg.max():.2f})"
        )
        st.write("-" * 30)


def display_date_with_highest_count(df):
    if df is not None:
        df["Date"] = pd.to_datetime(df["Date"])
        date_counts = df["Date"].value_counts()
        max_count = date_counts.max()
        dates_with_max_count = date_counts[date_counts == max_count]

        st.write("Date(s) with the highest number of entries:")
        dates_with_max_count_df = pd.DataFrame(
            {"Date": dates_with_max_count.index, "Count": dates_with_max_count.values}
        )
        dates_with_max_count_df["Date"] = dates_with_max_count_df["Date"].dt.strftime(
            "%Y-%m-%d"
        )
        st.table(dates_with_max_count_df)
        st.write("-" * 30)


def display_frequency_with_user_input(df):
    if df is not None:
        date_counts = df["Date"].value_counts()
        unique_counts = sorted(date_counts.unique())
        unique_counts_str = [str(count) for count in unique_counts]

        st.write("Possible frequencies are:")
        st.write(", ".join(unique_counts_str))

        default_value = max(unique_counts) if unique_counts else 1
        user_input = st.number_input(
            "Enter the frequency you want to see:",
            min_value=min(unique_counts),
            max_value=max(unique_counts),
            value=default_value,
        )

        if user_input in unique_counts:
            dates_with_frequency = date_counts[date_counts == user_input]
            if not dates_with_frequency.empty:
                st.write(f"Dates with frequency {user_input}:")
                total_count = dates_with_frequency.sum()
                st.write("Total count: ", str(total_count / user_input))
                for date in dates_with_frequency.index:
                    st.write(date.strftime("%d %B %Y"))
            else:
                st.write(f"No dates found with frequency {user_input}")
        else:
            st.error(
                "Frequency not found in the dataset. Please enter a valid frequency."
            )
        st.write("-" * 30)


def display_days_with_frequency(df):
    df["Date"] = pd.to_datetime(df["Date"])
    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    day_of_week_counts = df["Date"].dt.day_name().value_counts().reindex(day_order)
    day_of_week_counts_df = pd.DataFrame(
        {"Days": day_of_week_counts.index, "Frequency": day_of_week_counts.values}
    )

    st.write("Days of the week and their frequencies:")
    st.table(day_of_week_counts_df)

    plt.figure(figsize=(10, 6))
    plt.bar(day_of_week_counts.index, day_of_week_counts.values)
    plt.title("Days of the Week and Their Frequencies")
    plt.xlabel("Day of the Week")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45)
    st.pyplot(plt)

    most_common_day = day_of_week_counts.idxmax()
    least_common_day = day_of_week_counts.idxmin()

    st.write(f"Most common day in the week: {most_common_day}")
    st.write(f"Least common day in the week: {least_common_day}")

    total_frequency = sum(day_of_week_counts)
    most_common_day_frequency = day_of_week_counts[most_common_day]
    chance_most_common_day = most_common_day_frequency / total_frequency * 100
    st.write(
        f"Likelihood of doing the task on {most_common_day}: {chance_most_common_day:.2f}%"
    )
    st.write("-" * 30)


def display_hourly_frequency(df):
    df["Time"] = pd.to_datetime(df["Time"], errors="coerce", format="%I:%M %p")
    df.dropna(subset=["Time"], inplace=True)
    hourly_frequency = {}

    for hour in range(0, 24):
        start_time = pd.to_datetime(f"{hour:02d}:00:00").time()
        end_time = pd.to_datetime(f"{hour:02d}:59:59").time()
        filtered_df = df[
            (df["Time"].dt.time >= start_time) & (df["Time"].dt.time <= end_time)
        ]
        frequency = filtered_df.shape[0]
        hourly_frequency[f"{hour:02d}:00 to {hour+1:02d}:00"] = frequency

    hourly_frequency_df = pd.DataFrame(
        hourly_frequency.items(), columns=["Hour Section", "Frequency"]
    )

    st.write("Hourly frequency:")
    st.table(hourly_frequency_df)

    plt.figure(figsize=(10, 6))
    plt.bar(hourly_frequency.keys(), hourly_frequency.values())
    plt.title("Hourly Frequency")
    plt.xlabel("Hour Section")
    plt.ylabel("Frequency")
    plt.xticks(rotation=45, ha="right")
    st.pyplot(plt)

    max_frequency = max(hourly_frequency.values())
    highest_frequency_hours = []

    for hour, frequency in hourly_frequency.items():
        if frequency == max_frequency:
            highest_frequency_hours.append(hour)

    st.write("Hour section(s) with the highest frequency:")
    for hour in highest_frequency_hours:
        st.write(f"{hour} : ({max_frequency})")

    total_frequency = sum(hourly_frequency.values())
    chance = max_frequency / total_frequency * 100
    st.write(f"Chance of doing the task during {hour}: {chance:.2f}%")
    st.write("-" * 30)


# Data Cleaner Functions
def download_clean(cleaned_file, file_name_with_extension):
    st.download_button(
        label="Download Cleaned File",
        data=cleaned_file,
        key="cleaned_file",
        file_name=file_name_with_extension,
    )


def replace(df):
    custom_value = st.text_input("Enter a value to replace nulls:", "NULL")
    df = df.fillna(custom_value)
    return df


def remove_duplicates(df):
    return df.drop_duplicates(keep="first")


def remove_missing_values(df):
    return df.dropna()


def convert_to_lowercase(df, selected_columns):
    for column in selected_columns:
        if column in df.columns:
            if df[column].dtype == "object":
                df[column] = df[column].str.lower()
            else:
                st.error(
                    f"Column '{column}' is not of string data type. Select a string column to convert to lowercase."
                )
                return df
    return df


def delete_columns(df, columns_to_delete):
    df = df.drop(columns=columns_to_delete, errors="ignore")
    return df


def sort_column(df, column_name, ascending):
    if column_name in df.columns:
        df[column_name] = df[column_name].astype(str)
        df = df.sort_values(by=column_name, ascending=ascending)
    return df


def capitalize_column_values(df, selected_columns):
    for selected_column in selected_columns:
        if selected_column in df.columns:
            if df[selected_column].dtype == "object":
                df[selected_column] = df[selected_column].apply(
                    lambda x: (
                        x.capitalize()
                        if isinstance(x, str) and x and x[0].isalpha()
                        else x
                    )
                )
            else:
                st.error(
                    f"Column '{selected_column}' is not of string data type. Select a string column to capitalize."
                )
    return df


def load_sample_csv():

    csv_file = """
    Name,Age,Score,Date
    John Doe,25,85.6,2023-01-05
    Alice Smith,30,92.3,2023-02-10
    Bob Johnson,,78.9,2023-03-15
    Emily Brown,28,,2023-04-20
    Michael Lee,,79.5,
    Sarah Wilson,35,,2023-06-25
    chris davis,40,88.2,2023-07-30
    Jessica Taylor,,90.1,2023-08-05
    David rodriguez,45,86.4,
    Emma Martinez,,84.7,2023-10-10
    ryan Anderson,50,87.9,2023-11-15
    Olivia Thomas,,91.2,2023-12-20
    Olivia Thomas,,91.2,2023-12-20
    Jessica Taylor,,90.1,2023-08-05
    """
    try:
        df = pd.read_csv(io.StringIO(csv_file))
        return df
    except Exception as e:
        st.error(f"Error: {e}")
        return None


def main():
    st.title("Streamlit Projects")
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose the app", ["Data Cleaner", "Timestamp", "Analysis"]
    )

    if app_mode == "Timestamp":
        st.header("Timestamp")
        if st.button("Refresh"):
            st.experimental_rerun()
        password_entered = login_page()
        if st.button("Save Date and Time"):
            save_current_datetime(password_entered)
        if st.button("Delete Latest Entry"):
            delete_latest_entry(password_entered)
        if st.button("Previous Entries (Cleaned)"):
            view_previous_entries("clean_data", "cleaned_data.csv")
        if st.button("Previous Entries (Raw)"):
            view_previous_entries("raw_data", "raw_data.csv")

        st.sidebar.markdown("### Project Description")
        st.sidebar.markdown(
            """
        This project provides a secure interface for managing timestamp entries in a MySQL database. 
You can perform the following operations:

- **Save Date and Time:** Save the current date and time (in IST) into the database.
- **Delete Latest Entry:** Remove the most recent timestamp entry from the database.
- **View Previous Entries:** Display and download previous timestamp entries, either cleaned or raw data.

All operations for saving and deleting timestamps are password-protected.
        """
        )

    elif app_mode == "Analysis":
        st.header("Analysis")
        data_type = st.radio("Select data type:", ("Cleaned Data", "Raw Data"))
        st.write("-" * 30)

        df = fetch_data(data_type)
        if df is not None:
            st.write("### All the data in table:")
            st.write(df)
            total_rows(df)
            csv_file = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download CSV",
                data=csv_file,
                file_name="data.csv",
                mime="text/csv",
            )
        st.write("-" * 30)

        display_insights(df)

        st.sidebar.markdown("### Project Description")
        st.sidebar.markdown(
            """
        This application analyzes timestamp data fetched from a MySQL database. 

The data collection process began on October 26, 2019, and is ongoing. This data records the number of times push-ups were done each day.

The cleaned data does not include data from October 2019, August 2023, and September 2023 due to miscalculations during that period. Raw data contains all available data.

Raw data and cleaned data are separated to ensure accuracy during analysis.

The application provides the following insights:
- **Monthly Counts:** Total number of entries for each month and year.
- **Average Monthly Counts:** Average count for each month.
- **Date with Highest Count:** Date(s) with the highest number of entries.
- **Frequency with User Input:** Display dates with a specific frequency as entered by the user.
- **Days with Frequency:** Frequency of entries for each day of the week.
- **Hourly Frequency:** Frequency of entries for each hour of the day.
        """
        )

    elif app_mode == "Data Cleaner":
        st.header("Data Cleaner")
        sheets_dataframes = {}
        uploaded_file = st.file_uploader(
            "Upload an Excel or CSV file", type=["xls", "xlsx", "csv"]
        )
        sample_df = load_sample_csv()
        if sample_df is not None:
            csv_file = io.BytesIO()
            sample_df.to_csv(csv_file, index=False)
            csv_file.seek(0)
            st.download_button(
                label="Download Sample CSV",
                data=csv_file,
                file_name="sample.csv",
                mime="text/csv",
            )

        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(("xls", "xlsx")):
                    xls = pd.ExcelFile(uploaded_file)
                    sheet_names = xls.sheet_names
                    for sheet_name in sheet_names:
                        sheets_dataframes[sheet_name] = pd.read_excel(
                            xls, sheet_name=sheet_name
                        )
                else:
                    df = pd.read_csv(uploaded_file)
                    sheets_dataframes["Sheet 1"] = df
            except Exception as e:
                st.error(f"Error: {e}")
            st.success("File uploaded successfully!")
            selected_sheet = st.selectbox(
                "Select a sheet to clean:", list(sheets_dataframes.keys())
            )
            clean_options = st.multiselect(
                "Select cleaning options:",
                [
                    "Replace",
                    "Remove Duplicate",
                    "Remove Missing Values",
                    "Convert to Lowercase",
                    "Delete Columns",
                    "Sort Column",
                    "Capitalize Columns",
                ],
            )
            if "Replace" in clean_options:
                sheets_dataframes[selected_sheet] = replace(
                    sheets_dataframes[selected_sheet]
                )
                st.write("Replaced null values with custom value.")
            if "Remove Duplicate" in clean_options:
                sheets_dataframes[selected_sheet] = remove_duplicates(
                    sheets_dataframes[selected_sheet]
                )
                st.write("Removed duplicate rows.")
            if "Remove Missing Values" in clean_options:
                sheets_dataframes[selected_sheet] = remove_missing_values(
                    sheets_dataframes[selected_sheet]
                )
                st.write("Removed rows with missing values.")
            if "Convert to Lowercase" in clean_options:
                selected_columns = st.multiselect(
                    "Select columns to convert to lowercase:",
                    sheets_dataframes[selected_sheet].columns,
                )
                sheets_dataframes[selected_sheet] = convert_to_lowercase(
                    sheets_dataframes[selected_sheet], selected_columns
                )
                st.write(
                    f"Converted selected columns to lowercase: {', '.join(selected_columns)}"
                )
            if "Delete Columns" in clean_options:
                columns_to_delete = st.multiselect(
                    "Select columns to delete:",
                    sheets_dataframes[selected_sheet].columns,
                )
                sheets_dataframes[selected_sheet] = delete_columns(
                    sheets_dataframes[selected_sheet], columns_to_delete
                )
                st.write(f"Deleted selected columns: {', '.join(columns_to_delete)}")
            if "Sort Column" in clean_options:
                column_to_sort = st.selectbox(
                    "Select a column to sort:",
                    sheets_dataframes[selected_sheet].columns,
                )
                sort_order = st.radio(
                    "Select sorting order:", ["Ascending", "Descending"]
                )
                ascending = sort_order == "Ascending"
                sheets_dataframes[selected_sheet] = sort_column(
                    sheets_dataframes[selected_sheet], column_to_sort, ascending
                )
                st.write(
                    f"Sorted column '{column_to_sort}' in {sort_order.lower()} order."
                )
            if "Capitalize Columns" in clean_options:
                selected_columns_to_capitalize = st.multiselect(
                    "Select columns to capitalize:",
                    sheets_dataframes[selected_sheet].columns,
                )
                sheets_dataframes[selected_sheet] = capitalize_column_values(
                    sheets_dataframes[selected_sheet], selected_columns_to_capitalize
                )
                st.write(
                    f"Capitalized selected columns: {', '.join(selected_columns_to_capitalize)}"
                )
            cleaned_file = io.BytesIO()
            if uploaded_file.name.endswith(("xls", "xlsx")):
                with pd.ExcelWriter(cleaned_file, engine="openpyxl") as writer:
                    for sheet_name, sheet_df in sheets_dataframes.items():
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                file_extension = "xlsx"
            else:
                sheets_dataframes[selected_sheet].to_csv(cleaned_file, index=False)
                file_extension = "csv"
            input_file_name = uploaded_file.name.rsplit(".", 1)[0]
            download_clean(cleaned_file, f"{input_file_name}_cleaned.{file_extension}")

            if uploaded_file.name.endswith(("xls", "xlsx")):
                cleaned_xls_file = io.BytesIO()
                with pd.ExcelWriter(cleaned_xls_file, engine="openpyxl") as writer:
                    for sheet_name, sheet_df in sheets_dataframes.items():
                        sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                csv_file = io.BytesIO()
                sheets_dataframes[selected_sheet].to_csv(csv_file, index=False)
                st.download_button(
                    label="Download Cleaned File (CSV)",
                    data=csv_file,
                    key="cleaned_file_csv",
                    file_name=f"{input_file_name}_cleaned.csv",
                )

            st.dataframe(sheets_dataframes[selected_sheet])

            st.sidebar.markdown("### Summary of Cleaning Operations")
            if "Replace" in clean_options:
                st.sidebar.write("- Replaced null values with custom value.")
            if "Remove Duplicate" in clean_options:
                st.sidebar.write("- Removed duplicate rows.")
            if "Remove Missing Values" in clean_options:
                st.sidebar.write("- Removed rows with missing values.")
            if "Convert to Lowercase" in clean_options:
                st.sidebar.write(
                    f"- Converted selected columns to lowercase: {', '.join(selected_columns)}"
                )
            if "Delete Columns" in clean_options:
                st.sidebar.write(
                    f"- Deleted selected columns: {', '.join(columns_to_delete)}"
                )
            if "Sort Column" in clean_options:
                st.sidebar.write(
                    f"- Sorted column '{column_to_sort}' in {sort_order.lower()} order."
                )
            if "Capitalize Columns" in clean_options:
                st.sidebar.write(
                    f"- Capitalized selected columns: {', '.join(selected_columns_to_capitalize)}"
                )

        st.sidebar.markdown("### Project Description")
        st.sidebar.markdown(
            """
        This project provides a user-friendly interface for cleaning and processing tabular data files (CSV, XLS, XLSX). 
        You can perform the following operations on your data:

        - **Replace Null Values:** Replace missing (null) values with a custom value.
        - **Remove Duplicate Rows:** Eliminate duplicate rows from your dataset.
        - **Remove Missing Values:** Remove rows containing missing values.
        - **Convert to Lowercase:** Convert text columns to lowercase.
        - **Delete Columns:** Select and delete specific columns from the dataset.
        - **Sort Column:** Sort a column in ascending or descending order based on lexicographical order.
        - **Capitalize Columns:** Capitalize the first letter of elements in selected columns.

        You can download the cleaned data in the same format as your input file or in CSV format.
        """
        )


if __name__ == "__main__":
    main()
