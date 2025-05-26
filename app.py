import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta

st.subheader("DSYM Karol Bagh")
st.subheader("Presents")
st.title("Augustine Championship 4.0")
st.subheader("St. Augustine Forane Church, Karol Bagh")

# Select number of teams
num_teams = st.selectbox("Select the number of teams", [12, 16])

# Upload CSV
uploaded_file = st.file_uploader("Upload a CSV with team names and church names", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, delimiter=';')
    if 'Team' not in df.columns or 'Church' not in df.columns:
        st.error("CSV must contain 'Team' and 'Church' columns")
    else:
        team_list = df['Team'].tolist()
        church_list = df['Church'].tolist()

        # Display all teams
        st.markdown("### Team to be fixed")
        fixed_team = st.selectbox("Select a team to fix", team_list)
        selected_group = st.selectbox("Select group that the fixed team will be in", ['A', 'B', 'C', 'D'])

        # Generate groups
        st.markdown("### Generate Groups")
        if st.button("Generate Groups"):
            num_groups = 4
            group_size = num_teams // num_groups

            groups = {'A': [], 'B': [], 'C': [], 'D': []}
            church_in_group = {'A': [], 'B': [], 'C': [], 'D': []}

            fixed_team_index = team_list.index(fixed_team)
            fixed_church = church_list[fixed_team_index]

            groups[selected_group].append(fixed_team)
            church_in_group[selected_group].append(fixed_church)

            remaining_teams = [(team_list[i], church_list[i]) for i in range(num_teams) if team_list[i] != fixed_team]
            random.shuffle(remaining_teams)

            for team, church in remaining_teams:
                for group in groups:
                    if len(groups[group]) < group_size and church not in church_in_group[group]:
                        groups[group].append(team)
                        church_in_group[group].append(church)
                        break

            st.markdown("### Groups")
            for group in groups:
                st.write(f"Group {group}: {groups[group]}")

            # Generate fixtures
            def generate_group_fixtures(group_name, teams, start_time):
                schedule = []
                time = start_time
                for i in range(len(teams)):
                    for j in range(i + 1, len(teams)):
                        schedule.append((time.strftime("%H:%M"), f"{group_name}{i+1} ({teams[i]}) vs {group_name}{j+1} ({teams[j]})"))
                        time += timedelta(minutes=20)
                return schedule, time

            st.markdown("### Group Fixtures")
            start_time = datetime.strptime("09:00", "%H:%M")
            all_schedules = []
            for group in ['A', 'B', 'C', 'D']:
                schedule, start_time = generate_group_fixtures(group, groups[group], start_time)
                all_schedules.extend(schedule)

            for match_time, match in all_schedules:
                st.write(f"{match_time} - {match}")

            # Knockouts
            st.markdown("### Knockout Fixtures")
            qf = [
                ("QF1", "Winner A", "Runner B"),
                ("QF2", "Winner B", "Runner A"),
                ("QF3", "Winner C", "Runner D"),
                ("QF4", "Winner D", "Runner C"),
            ]
            sf = [
                ("SF1", "Winner QF1", "Winner QF3"),
                ("SF2", "Winner QF2", "Winner QF4"),
            ]
            final_matches = [
                ("LF", "Loser SF1", "Loser SF2"),
                ("Final", "Winner SF1", "Winner SF2")
            ]

            st.markdown("#### Quarter Finals")
            for match in qf:
                st.write(f"{match[0]}: {match[1]} vs {match[2]}")

            st.markdown("#### Semi Finals")
            for match in sf:
                st.write(f"{match[0]}: {match[1]} vs {match[2]}")

            st.markdown("#### Loser's Final and Final")
            for match in final_matches:
                st.write(f"{match[0]}: {match[1]} vs {match[2]}")
