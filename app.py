import streamlit as st
import pandas as pd
import random
from datetime import datetime, timedelta
from itertools import combinations
from fpdf import FPDF
from datetime import datetime
from zoneinfo import ZoneInfo

def safe_text(text):
    return str(text).encode("latin-1", errors="ignore").decode("latin-1")

st.subheader("DSYM Karol Bagh")
st.subheader("Presents")
st.title("Augustine Championship 4.0")
st.subheader("St. Augustine Forane Church, Karol Bagh")
st.image("PicsArt_09-05-09.29.37.png", width=100)

# Select number of teams
num_teams = st.selectbox("Select the number of teams", [12, 16])

# Upload Excel
uploaded_file = st.file_uploader("Upload an Excel file with team names and church names", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    if 'Team' not in df.columns or 'Church' not in df.columns:
        st.error("Excel file must contain 'Team' and 'Church' columns")
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
            group_keys = ['A', 'B', 'C', 'D']
            group_size = num_teams // num_groups
        
            # Step 1: Group teams by church
            from collections import defaultdict
            church_to_teams = defaultdict(list)
            for team, church in zip(team_list, church_list):
                church_to_teams[church].append(team)
        
            # Step 2: Initialize empty groups
            groups = {key: [] for key in group_keys}
            church_in_group = {key: [] for key in group_keys}
        
            # Step 3: Place fixed team first
            fixed_team_index = team_list.index(fixed_team)
            fixed_church = church_list[fixed_team_index]
        
            groups[selected_group].append(fixed_team)
            church_in_group[selected_group].append(fixed_church)
        
            # Remove the fixed team from its church group
            church_to_teams[fixed_church].remove(fixed_team)
        
            # Step 4: Assign other teams
            unassigned = []  # fallback for later
            for church, teams in church_to_teams.items():
                random.shuffle(teams)
                used_groups = set()
        
                for team in teams:
                    # Try to find a group with space that hasn't been used by this church
                    possible_groups = [
                        g for g in group_keys
                        if len(groups[g]) < group_size and church not in church_in_group[g] and g not in used_groups
                    ]
                    if possible_groups:
                        chosen_group = random.choice(possible_groups)
                        groups[chosen_group].append(team)
                        church_in_group[chosen_group].append(church)
                        used_groups.add(chosen_group)
                    else:
                        # Save unassigned to assign later
                        unassigned.append((team, church))
        
            # Step 5: Assign leftover teams (from churches with more than 4 teams, etc.)
            for team, church in unassigned:
                placed = False
                for group in group_keys:
                    if len(groups[group]) < group_size and church not in church_in_group[group]:
                        groups[group].append(team)
                        church_in_group[group].append(church)
                        placed = True
                        break
                if not placed:
                    for group in group_keys:
                        if len(groups[group]) < group_size:
                            groups[group].append(team)
                            church_in_group[group].append(church)
                            placed = True
                            break
        
            # Display final groups
            st.markdown("### Groups")
            group_display = {f"Group {group}": teams for group, teams in groups.items()}
            st.dataframe(pd.DataFrame(dict([(k, pd.Series(v)) for k,v in group_display.items()])))


            # Function to generate match combinations for a group
            def group_matches(group_teams, group_label):
                return [
                    (f"{group_label}{i+1} ({group_teams[i]})", f"{group_label}{j+1} ({group_teams[j]})")
                    for i, j in combinations(range(len(group_teams)), 2)
                ]

            # Interleave matches from A/B
            ab_schedule = []
            ab_a = group_matches(groups['A'], 'A')
            ab_b = group_matches(groups['B'], 'B')
            while ab_a or ab_b:
                if ab_a:
                    ab_schedule.append(ab_a.pop(0))
                if ab_b:
                    ab_schedule.append(ab_b.pop(0))

            # Interleave matches from C/D
            cd_schedule = []
            cd_c = group_matches(groups['C'], 'C')
            cd_d = group_matches(groups['D'], 'D')
            while cd_c or cd_d:
                if cd_c:
                    cd_schedule.append(cd_c.pop(0))
                if cd_d:
                    cd_schedule.append(cd_d.pop(0))

            full_schedule = ab_schedule + cd_schedule

            # Display group fixtures in a table
            st.markdown("### Group Fixtures")
            start_time = datetime.strptime("09:00", "%H:%M")
            fixture_table = []
            for match in full_schedule:
                match_time = start_time.strftime("%H:%M")
                fixture_table.append({"Time": match_time, "Match": f"{match[0]} vs {match[1]}"})
                start_time += timedelta(minutes=20)

            fixture_df = pd.DataFrame(fixture_table)
            st.dataframe(fixture_df)

            # Knockout Fixtures
            st.markdown("### Knockout Fixtures")
            knockout_fixtures = [
                {"Stage": "QF1", "Match": "Winner A vs Runner B"},
                {"Stage": "QF2", "Match": "Winner B vs Runner A"},
                {"Stage": "QF3", "Match": "Winner C vs Runner D"},
                {"Stage": "QF4", "Match": "Winner D vs Runner C"},
                {"Stage": "SF1", "Match": "Winner QF1 vs Winner QF3"},
                {"Stage": "SF2", "Match": "Winner QF2 vs Winner QF4"},
                {"Stage": "Loser's Final", "Match": "Loser SF1 vs Loser SF2"},
                {"Stage": "Final", "Match": "Winner SF1 vs Winner SF2"},
            ]

            knockout_df = pd.DataFrame(knockout_fixtures)
            st.dataframe(knockout_df)

            # PDF Download Option
            st.markdown("### Download Fixture as PDF")
            class PDF(FPDF):
                def header(self):
                    self.set_font("Arial", 'B', 12)
                    self.cell(0, 10, safe_text("Augustine Championship 4.0 Fixtures"), ln=True, align="C")

                def chapter_title(self, title):
                    self.set_font("Arial", 'B', 12)
                    self.cell(0, 10, safe_text(title), ln=True)

                def chapter_body(self, body):
                    self.set_font("Arial", '', 12)
                    for line in body:
                        self.cell(0, 10, safe_text(line), ln=True)


            pdf = PDF()
            pdf.add_page()
            image_width = 30
            x_pos = pdf.w - image_width - 10  # 10mm margin from the right
            
            # Add the image at top-right
            pdf.image("PicsArt_09-05-09.29.37.png", x=x_pos, y=10, w=image_width)
             
            pdf.chapter_title("Group Allocation")
            for group_name, team_list in groups.items():
                pdf.set_font("Arial", 'B', 11)
                pdf.cell(0, 10, f"Group {group_name}:", ln=True)
                pdf.set_font("Arial", '', 11)
                for team in team_list:
                    pdf.cell(0, 10, f" - {safe_text(team)}", ln=True)
                pdf.ln(5)
            pdf.chapter_title("Group Fixtures")
            for row in fixture_table:
                pdf.chapter_body([f"{row['Time']} - {row['Match']}"])

            pdf.chapter_title("Knockout Fixtures")
            for row in knockout_fixtures:
                pdf.chapter_body([f"{row['Stage']}: {row['Match']}"])
            pdf.set_font("Arial", 'I', 12)
            pdf.cell(0, 10, "St. Augustine Church Parish Priest Signature", ln=True)
            pdf.cell(0, 10, "_____________________________", ln=True)
            pdf.set_font("Arial", '', 10)
            now = datetime.now(ZoneInfo("Asia/Kolkata"))
            formatted_date = now.strftime("%d-%m-%Y %H:%M")
           
            pdf.cell(0, 10, f"Date: {formatted_date}")
            
            pdf_output = "/tmp/fixtures.pdf"
            pdf.output(pdf_output)

            with open(pdf_output, "rb") as f:
                st.download_button(
                    label="Download PDF",
                    data=f,
                    file_name="augustine_fixtures.pdf",
                    mime="application/pdf"
                )
