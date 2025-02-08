
import streamlit as st
import requests
import pandas as pd
import sqlite3
from datetime import datetime
import json

# Load configuration from config file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

# Constants
DEXSCREENER_API_URL = config["dex_api_url"]
DATABASE_NAME = config["database_name"]
TELEGRAM_BOT_TOKEN = config["telegram_bot_token"]
BONKBOT_API_URL = "https://api.bonkbot.com/trade"
BONKBOT_API_KEY = config["bonkbot_api_key"]

# Initialize Streamlit app
st.title("🚀 Crypto Trading Bot Dashboard")

# Sidebar for settings
st.sidebar.header("Settings")
update_interval = st.sidebar.slider("Update Interval (seconds)", 60, 600, 300)
min_liquidity = st.sidebar.number_input("Minimum Liquidity", value=10000)
max_liquidity = st.sidebar.number_input("Maximum Liquidity", value=1000000)
min_market_cap = st.sidebar.number_input("Minimum Market Cap", value=50000)
max_market_cap = st.sidebar.number_input("Maximum Market Cap", value=10000000)

# Blacklist management
st.sidebar.header("Blacklist Management")
coin_blacklist = st.sidebar.text_area("Coin Blacklist (one per line)", value="\n".join(config["blacklist"]["coins"]))
dev_blacklist = st.sidebar.text_area("Dev Blacklist (one per line)", value="\n".join(config["blacklist"]["devs"]))

# Save blacklists to config
if st.sidebar.button("Update Blacklists"):
    config["blacklist"]["coins"] = coin_blacklist.split("\n")
    config["blacklist"]["devs"] = dev_blacklist.split("\n")
    with open("config.json", "w") as config_file:
        json.dump(config, config_file)
    st.sidebar.success("Blacklists updated!")

# Connect to SQLite database
def init_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id TEXT PRIMARY KEY,
            name TEXT,
            symbol TEXT,
            price_usd REAL,
            market_cap REAL,
            liquidity REAL,
            volume_24h REAL,
            is_cex_listed INTEGER,
            is_tier1 INTEGER,
            is_rugged INTEGER,
            is_pumped INTEGER,
            dev_address TEXT,
            is_fake_volume INTEGER,
            is_bundled_supply INTEGER,
            rugcheck_status TEXT,
            timestamp DATETIME
        )
    ''')
    conn.commit()
    return conn

# Fetch token data from DexScreener
def fetch_token_data(token_address):
    url = f"{DEXSCREENER_API_URL}{token_address}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to fetch data for token: {token_address}")
        return None

# Execute trade via BonkBot
def execute_trade(token_address, action):
    headers = {"Authorization": f"Bearer {BONKBOT_API_KEY}"}
    payload = {
        "token_address": token_address,
        "action": action  # "buy" or "sell"
    }
    response = requests.post(BONKBOT_API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return True
    else:
        st.error(f"Failed to execute {action} for token {token_address}.")
        return False

# Send Telegram notification
def send_telegram_notification(message):
    chat_id = config["telegram_chat_id"]
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        st.error("Failed to send Telegram notification.")

# Main app
def main():
    conn = init_db()

    # Token monitoring
    st.header("📊 Token Monitoring")
    token_addresses = st.text_area("Enter Token Addresses (one per line)", value="\n".join(["TOKEN_ADDRESS_1", "TOKEN_ADDRESS_2"]))
    token_addresses = token_addresses.split("\n")

    if st.button("Fetch Token Data"):
        for address in token_addresses:
            token_data = fetch_token_data(address)
            if token_data:
                st.write(f"**Token:** {token_data['pair']['baseToken']['name']} ({token_data['pair']['baseToken']['symbol']})")
                st.write(f"**Price (USD):** ${token_data['pair']['priceUsd']}")
                st.write(f"**Market Cap:** ${token_data['pair']['marketCap']}")
                st.write(f"**Liquidity:** ${token_data['pair']['liquidity']['usd']}")
                st.write("---")

    # Trade execution
    st.header("💹 Execute Trades")
    trade_token_address = st.text_input("Enter Token Address for Trade")
    trade_action = st.selectbox("Select Action", ["buy", "sell"])

    if st.button("Execute Trade"):
        if execute_trade(trade_token_address, trade_action):
            st.success(f"Successfully executed {trade_action} for token {trade_token_address}.")
            send_telegram_notification(f"✅ {trade_action.capitalize()} {trade_token_address} at {datetime.now()}.")

    # View notifications
    st.header("🔔 Notifications")
    if st.button("View Latest Notifications"):
        # Fetch notifications from Telegram (pseudo-code)
        st.write("Latest Notifications:")
        st.write("- Bought TOKEN_ADDRESS_1 at $0.50")
        st.write("- Sold TOKEN_ADDRESS_2 at $1.00")

    # View database
    st.header("📂 Database")
    if st.button("View Database"):
        df = pd.read_sql_query("SELECT * FROM tokens", conn)
        st.dataframe(df)

# Run the app
if __name__ == "__main__":
    main()










import datetime
import random

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Show app title and description.
st.set_page_config(page_title="Support tickets", page_icon="🎫")
st.title("🎫 Support tickets")
st.write(
    """
    This app shows how you can build an internal tool in Streamlit. Here, we are 
    implementing a support ticket workflow. The user can create a ticket, edit 
    existing tickets, and view some statistics.
    """
)

# Create a random Pandas dataframe with existing tickets.
if "df" not in st.session_state:

    # Set seed for reproducibility.
    np.random.seed(42)

    # Make up some fake issue descriptions.
    issue_descriptions = [
        "Network connectivity issues in the office",
        "Software application crashing on startup",
        "Printer not responding to print commands",
        "Email server downtime",
        "Data backup failure",
        "Login authentication problems",
        "Website performance degradation",
        "Security vulnerability identified",
        "Hardware malfunction in the server room",
        "Employee unable to access shared files",
        "Database connection failure",
        "Mobile application not syncing data",
        "VoIP phone system issues",
        "VPN connection problems for remote employees",
        "System updates causing compatibility issues",
        "File server running out of storage space",
        "Intrusion detection system alerts",
        "Inventory management system errors",
        "Customer data not loading in CRM",
        "Collaboration tool not sending notifications",
    ]

    # Generate the dataframe with 100 rows/tickets.
    data = {
        "ID": [f"TICKET-{i}" for i in range(1100, 1000, -1)],
        "Issue": np.random.choice(issue_descriptions, size=100),
        "Status": np.random.choice(["Open", "In Progress", "Closed"], size=100),
        "Priority": np.random.choice(["High", "Medium", "Low"], size=100),
        "Date Submitted": [
            datetime.date(2023, 6, 1) + datetime.timedelta(days=random.randint(0, 182))
            for _ in range(100)
        ],
    }
    df = pd.DataFrame(data)

    # Save the dataframe in session state (a dictionary-like object that persists across
    # page runs). This ensures our data is persisted when the app updates.
    st.session_state.df = df


# Show a section to add a new ticket.
st.header("Add a ticket")

# We're adding tickets via an `st.form` and some input widgets. If widgets are used
# in a form, the app will only rerun once the submit button is pressed.
with st.form("add_ticket_form"):
    issue = st.text_area("Describe the issue")
    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
    submitted = st.form_submit_button("Submit")

if submitted:
    # Make a dataframe for the new ticket and append it to the dataframe in session
    # state.
    recent_ticket_number = int(max(st.session_state.df.ID).split("-")[1])
    today = datetime.datetime.now().strftime("%m-%d-%Y")
    df_new = pd.DataFrame(
        [
            {
                "ID": f"TICKET-{recent_ticket_number+1}",
                "Issue": issue,
                "Status": "Open",
                "Priority": priority,
                "Date Submitted": today,
            }
        ]
    )

    # Show a little success message.
    st.write("Ticket submitted! Here are the ticket details:")
    st.dataframe(df_new, use_container_width=True, hide_index=True)
    st.session_state.df = pd.concat([df_new, st.session_state.df], axis=0)

# Show section to view and edit existing tickets in a table.
st.header("Existing tickets")
st.write(f"Number of tickets: `{len(st.session_state.df)}`")

st.info(
    "You can edit the tickets by double clicking on a cell. Note how the plots below "
    "update automatically! You can also sort the table by clicking on the column headers.",
    icon="✍️",
)

# Show the tickets dataframe with `st.data_editor`. This lets the user edit the table
# cells. The edited data is returned as a new dataframe.
edited_df = st.data_editor(
    st.session_state.df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Status": st.column_config.SelectboxColumn(
            "Status",
            help="Ticket status",
            options=["Open", "In Progress", "Closed"],
            required=True,
        ),
        "Priority": st.column_config.SelectboxColumn(
            "Priority",
            help="Priority",
            options=["High", "Medium", "Low"],
            required=True,
        ),
    },
    # Disable editing the ID and Date Submitted columns.
    disabled=["ID", "Date Submitted"],
)

# Show some metrics and charts about the ticket.
st.header("Statistics")

# Show metrics side by side using `st.columns` and `st.metric`.
col1, col2, col3 = st.columns(3)
num_open_tickets = len(st.session_state.df[st.session_state.df.Status == "Open"])
col1.metric(label="Number of open tickets", value=num_open_tickets, delta=10)
col2.metric(label="First response time (hours)", value=5.2, delta=-1.5)
col3.metric(label="Average resolution time (hours)", value=16, delta=2)

# Show two Altair charts using `st.altair_chart`.
st.write("")
st.write("##### Ticket status per month")
status_plot = (
    alt.Chart(edited_df)
    .mark_bar()
    .encode(
        x="month(Date Submitted):O",
        y="count():Q",
        xOffset="Status:N",
        color="Status:N",
    )
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(status_plot, use_container_width=True, theme="streamlit")

st.write("##### Current ticket priorities")
priority_plot = (
    alt.Chart(edited_df)
    .mark_arc()
    .encode(theta="count():Q", color="Priority:N")
    .properties(height=300)
    .configure_legend(
        orient="bottom", titleFontSize=14, labelFontSize=14, titlePadding=5
    )
)
st.altair_chart(priority_plot, use_container_width=True, theme="streamlit")
