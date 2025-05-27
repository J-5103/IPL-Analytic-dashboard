import streamlit as st
import hashlib
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from streamlit_option_menu import option_menu

st.set_page_config(page_title="IPL Analytics Dashboard", page_icon="🏏", layout="wide")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


USER_CREDENTIALS_FILE = "user_credentials.csv"


if not os.path.exists(USER_CREDENTIALS_FILE):
    df_credentials = pd.DataFrame(columns=["username", "password"])
    df_credentials.to_csv(USER_CREDENTIALS_FILE, index=False)


def load_credentials():
    return pd.read_csv(USER_CREDENTIALS_FILE)

def save_credentials(username, password):
    df_credentials = load_credentials()
    if username in df_credentials["username"].values:
        st.sidebar.error("Username already exists!")
        return
    df_new = pd.DataFrame([[username, hash_password(password)]], columns=["username", "password"])
    df_credentials = pd.concat([df_credentials, df_new], ignore_index=True)
    df_credentials.to_csv(USER_CREDENTIALS_FILE, index=False)

def authenticate(username, password):
    df_credentials = load_credentials()
    hashed_password = hash_password(password)
    return any((df_credentials["username"] == username) & (df_credentials["password"] == hashed_password))

query_params = st.query_params
if "auth" in query_params and query_params["auth"] == "true":
    st.session_state.authenticated = True

def side_bar():
    with st.sidebar:
        sidebar_select = option_menu(
            "IPL Analytics", ["Log-in", "Sign-Up"],
            default_index=0, menu_icon="award", icons=["unlock", "lock"],
            orientation="vertical", key="sidebar_menu_key"
        )


    if sidebar_select == "Log-in":
        st.success("If you do not have an account, please sign up first.")
        with st.form("LoginForm"):
            st.title("Log In")
            username = st.text_input("Enter Your Username")
            password = st.text_input("Enter Your Password", type="password")
            submit = st.form_submit_button("Submit")

            if submit:
                if authenticate(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.query_params["auth"] = "true"
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid username or password. Please try again.")

    elif sidebar_select == "Sign-Up":
        with st.form("SignUpForm"):
            st.title("Sign Up")
            new_username = st.text_input("Enter Your Username")
            new_password = st.text_input("Enter Your Password", type="password")
            submit2 = st.form_submit_button("Submit")

            if submit2:
                if new_username.strip() == "" or new_password.strip() == "":
                    st.error("Username and Password cannot be empty.")
                elif new_username in load_credentials()["username"].values:
                    st.error("Username already taken. Choose another one.")
                else:
                    save_credentials(new_username, new_password)
                    st.success("Account created! Please log in.")


def main_dashboard():
    with st.sidebar:
        selected = option_menu(
            "IPL Analytics",
            ["Home", "Overall Team Performance", "Player Insights", "Venue Analytics", "Head-to-Head Analysis", "Season Overview", "Logout"],
            icons=["house", "bar-chart", "person-circle", "geo-alt", "people", "calendar-event", "box-arrow-right"],
            default_index=0, menu_icon="award", orientation="vertical", key="main_menu_key"
        )

        @st.cache_data
        def load_data():
            import pandas as pd
            return pd.read_csv("ipl_dashboard_dataset.csv")

    if selected == "Home":
        st.toast("Welcome To IPL Analytics", icon="🎊")
        st.title("🏏 Welcome to IPL Analytics Dashboard")
        st.write(f"Hello! Glad to have you here. 🎉")

        st.image("indian-premier-league-ipl-2024-slide1.png", width=900)

        st.markdown(
            """
            ### 📊 About This Dashboard  
            This **IPL Analytics Dashboard** provides in-depth insights into the **Indian Premier League (IPL)**, helping users explore various aspects of the tournament.  
            - 🏆 **Overall Team Performance** – Analyze team statistics over different seasons.  
            - 🎯 **Player Insights** – Get individual player performance metrics and trends.  
            - 🏟 **Venue Analytics** – Discover how different stadiums influence match results.  
            - 🤝 **Head-to-Head Analysis** – Compare teams' performances against each other.  
            - 📅 **Season Overview** – Summary of each IPL season with key highlights.  

            🚀 Use the **sidebar menu** to navigate different sections and gain valuable insights!  
            """
        )

        st.success("Explore the dashboard to uncover interesting IPL trends and statistics!")
    elif selected == "Overall Team Performance":
        st.title("📊 Overall Team Performance")
        df = load_data()

        teams = sorted(set(df["Team1"]).union(set(df["Team2"])))
        selected_team = st.selectbox("Select a Team", teams)

        total_matches = df[(df["Team1"] == selected_team) | (df["Team2"] == selected_team)].shape[0]
        total_wins = df[df["Winner"] == selected_team].shape[0]
        total_losses = total_matches - total_wins

        st.subheader(f"📌 Performance of {selected_team}")
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Matches", total_matches)
        col2.metric("Wins", total_wins)
        col3.metric("Losses", total_losses)

        st.subheader(f"📈 Yearly Wins for {selected_team}")
        yearly_wins = df[df["Winner"] == selected_team].groupby("Season")["Winner"].count().reset_index()
        yearly_wins.columns = ["Season", "Wins"]

        import plotly.express as px
        fig = px.bar(
            yearly_wins,
            x="Season",
            y="Wins",
            color="Wins",
            color_continuous_scale="viridis",
            title=f"Yearly Wins for {selected_team}",
            labels={"Wins": "Number of Wins", "Season": "Season"},
            height=400
        )
        fig.update_layout(xaxis_title="Season", yaxis_title="Wins")
        st.plotly_chart(fig)


    elif selected == "Player Insights":

        st.title("🏅 Player Insights")

        df = load_data()

        players = sorted(df["Player_of_Match"].unique())

        selected_player = st.selectbox("Select a Player", players)

        total_awards = df[df["Player_of_Match"] == selected_player].shape[0]

        st.subheader(f"🏆 {selected_player} has won 'Player of the Match' {total_awards} times.")

        player_matches = df[df["Player_of_Match"] == selected_player]

        player_team_wins = player_matches[

            player_matches["Winner"].isin(player_matches["Team1"]) |

            player_matches["Winner"].isin(player_matches["Team2"])

            ].shape[0]

        player_team_losses = total_awards - player_team_wins

        st.subheader(f"📊 Matches Won When {selected_player} Was 'Player of the Match'")

        import plotly.graph_objects as go

        fig = go.Figure(data=[go.Pie(

            labels=["Won", "Lost"],

            values=[player_team_wins, player_team_losses],

            marker=dict(colors=["green", "red"]),

            hole=0,  # for donut use: hole=0.4

            textinfo='label+percent',

            insidetextorientation='radial'

        )])

        fig.update_layout(title=f"Win/Loss Distribution for {selected_player}", height=400)

        st.plotly_chart(fig)


    elif selected == "Venue Analytics":

        st.title("📍 Venue Analytics")

        df = load_data()

        venues = sorted(df["Venue"].unique())

        selected_venue = st.selectbox("Select a Venue", venues)

        total_matches = df[df["Venue"] == selected_venue].shape[0]

        st.subheader(f"🏟️ {selected_venue} has hosted {total_matches} matches.")

        st.subheader(f"📊 Runs Scored at {selected_venue} Over the Seasons")

        venue_df = df[df["Venue"] == selected_venue]

        import plotly.express as px

        import pandas as pd

        # Prepare data for plotly (melt to long format)

        melted_df = pd.melt(

            venue_df,

            id_vars=["Season"],

            value_vars=["Runs_Team1", "Runs_Team2"],

            var_name="Team",

            value_name="Runs"

        )

        fig = px.scatter(

            melted_df,

            x="Season",

            y="Runs",

            color="Team",

            symbol="Team",

            title=f"Runs Scored at {selected_venue} Over the Seasons",

            labels={"Season": "Season", "Runs": "Runs Scored"},

            height=400

        )

        st.plotly_chart(fig)

    elif selected == "Head-to-Head Analysis":

        st.title("⚔️ Head-to-Head Analysis")

        df = load_data()

        teams = sorted(df["Team1"].unique())

        team1 = st.selectbox("Select Team 1", teams)

        team2 = st.selectbox("Select Team 2", [t for t in teams if t != team1])

        h2h_matches = df[

            ((df["Team1"] == team1) & (df["Team2"] == team2)) | ((df["Team1"] == team2) & (df["Team2"] == team1))

            ]

        total_wins_team1 = (df["Winner"] == team1).sum()

        total_wins_team2 = (df["Winner"] == team2).sum()

        h2h_wins_team1 = (h2h_matches["Winner"] == team1).sum()

        h2h_wins_team2 = (h2h_matches["Winner"] == team2).sum()

        total_h2h_matches = len(h2h_matches)

        st.subheader(f"🏆 Overall Wins for {team1} & {team2}")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(label=f"{team1} Total Wins", value=total_wins_team1)

        with col2:
            st.metric(label=f"{team2} Total Wins", value=total_wins_team2)

        st.subheader(f"🏏 Head-to-Head Record Between {team1} & {team2}")

        st.write(f"Total Matches Played: **{total_h2h_matches}**")

        st.write(f"✅ {team1} Wins in Head-to-Head: **{h2h_wins_team1}**")

        st.write(f"✅ {team2} Wins in Head-to-Head: **{h2h_wins_team2}**")

        st.subheader(f"📊 Wins Comparison")

        import plotly.graph_objects as go

        categories = ["Total Wins", "H2H Wins"]

        fig = go.Figure(data=[

            go.Bar(name=team1, x=categories, y=[total_wins_team1, h2h_wins_team1], marker_color='blue'),

            go.Bar(name=team2, x=categories, y=[total_wins_team2, h2h_wins_team2], marker_color='red')

        ])

        fig.update_layout(

            barmode='group',

            title=f"Comparison Between {team1} & {team2}",

            xaxis_title="Category",

            yaxis_title="Number of Wins",

            height=400

        )

        st.plotly_chart(fig)
    elif selected == "Season Overview":
        st.title("📆 Season Overview")

        df = load_data()

        if "Season" not in df.columns or "Winner" not in df.columns or "Match_ID" not in df.columns:
            st.error("Dataset missing required columns!")

        available_seasons = sorted(df["Season"].unique(), reverse=True)
        selected_season = st.selectbox("Select a Season", available_seasons)

        season_df = df[df["Season"] == selected_season]

        top_team = season_df["Winner"].value_counts().idxmax()
        top_team_wins = season_df["Winner"].value_counts().max()

        st.subheader(f"🏆 Most Wins in {selected_season}")
        st.success(f"🥇 **{top_team}** won **{top_team_wins}** matches in {selected_season}.")

        st.subheader("📊 Team Wins in Selected Season")

        import plotly.express as px

        wins_per_team = season_df["Winner"].value_counts().reset_index()
        wins_per_team.columns = ["Team", "Wins"]

        fig = px.bar(
            wins_per_team,
            x="Team",
            y="Wins",
            color="Wins",
            color_continuous_scale="Blues",
            title=f"Wins by Teams in {selected_season}",
            labels={"Wins": "Number of Wins", "Team": "Team"},
            height=400
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig)

        # if "Innings_Runs" in df.columns:
        #     total_runs_per_match = season_df.groupby("Match_ID")["Innings_Runs"].sum().reset_index()
        # else:
        #     st.error("Column 'Innings_Runs' not found in dataset!")
        #     return
        #
        # st.subheader("📈 Total Runs Scored in the Season")
        #
        # fig, ax = plt.subplots()
        # ax.plot(total_runs_per_match["Match_ID"], total_runs_per_match["Innings_Runs"], marker="o", linestyle="-",
        #         color="green")
        #
        # ax.set_xlabel("Match ID")
        # ax.set_ylabel("Total Runs")
        # ax.set_title(f"Total Runs Scored in {selected_season}")
        # ax.grid(True)
        #
        # st.pyplot(fig)

    elif selected=="Logout":
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.query_params["auth"] = "false"
        st.rerun()


if "authenticated" in st.session_state and st.session_state.authenticated:
    main_dashboard()
else:
    side_bar()
