# Streamlit Projects

## Overview
This repository contains Streamlit applications for data cleaning, timestamp management and data analysis.

## Applications

### Data Cleaner
The Data Cleaner application provides a user-friendly interface for cleaning and processing tabular data files (CSV, XLS, XLSX). Operations include:
- **Replace Null Values:** Replace missing (null) values with a custom value.
- **Remove Duplicate Rows:** Eliminate duplicate rows from your dataset.
- **Remove Missing Values:** Remove rows containing missing values.
- **Convert to Lowercase:** Convert text columns to lowercase.
- **Delete Columns:** Select and delete specific columns from the dataset.
- **Sort Column:** Sort a column in ascending or descending order based on lexicographical order.
- **Capitalize Columns:** Capitalize the first letter of elements in selected columns.

### Timestamp Management
The Timestamp Management application allows users to interact with a MySQL database to manage timestamp entries securely. Key functionalities include:
- **Save Date and Time:** Save the current date and time (in IST) into the database.
- **Delete Latest Entry:** Remove the most recent timestamp entry from the database.
- **View Previous Entries:** Display and download previous timestamp entries, either cleaned or raw data.

### Analysis
The Analysis application analyzes timestamp data fetched from a MySQL database. Insights provided include:
- **Monthly Counts:** Total number of entries for each month and year.
- **Average Monthly Counts:** Average count for each month.
- **Date with Highest Count:** Date(s) with the highest number of entries.
- **Frequency with User Input:** Display dates with a specific frequency as entered by the user.
- **Days with Frequency:** Frequency of entries for each day of the week.
- **Hourly Frequency:** Frequency of entries for each hour of the day.

## Technologies Used
- **Streamlit:** For building interactive web applications.
- **Python Libraries:** pandas, matplotlib, mysql-connector-python, pytz, dotenv.

## Setup Instructions

1. Clone this repository to your local machine.
````bash
git clone https://github.com/SiddhantDembi/streamlit-projects.git
````

2. Install the required Python libraries listed in `requirements.txt`.
````bash
python -r requirements.txt
````

3. Set up your MySQL database and create necessary tables as described in the code for timestamp.
   
4. Create a `.env` file and add your database credentials and other configurations.
````bash
DB_HOST = " "
DB_USER = " "
DB_PASSWORD = " "
DB_DATABASE = " "
LOGIN_PASSWORD = " "
````
5. Run the Streamlit app.
````bash
streamlit run app.py
````

## Demo
1. Data Cleaner
![image](https://github.com/SiddhantDembi/streamlit-projects/assets/106478699/b8fd3435-3e02-4c2f-a69a-c0a65fcc165d)

2. Timestamp
![image](https://github.com/SiddhantDembi/streamlit-projects/assets/106478699/c5a2c54d-052b-43db-9cb3-88961e193c05)

3. Analysis
![image](https://github.com/SiddhantDembi/streamlit-projects/assets/106478699/1e6a61b2-0812-499f-a775-39e1f6aa7363)

