import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader import load_data, clean_data
from data_processor import calculate_kpis, save_precomputed_stats
import plotly.graph_objects as go

# Set page config
st.set_page_config(page_title="IPL Analysis Dashboard", layout="wide")

st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://upload.wikimedia.org/wikipedia/en/8/84/Indian_Premier_League_Official_Logo.svg' width='120'/>
        <h1 style='margin-top:10px;'>IPL Data Analysis Dashboard (2008-2024)</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Load and clean data
@st.cache_data(persist="disk")
def get_data():
    matches, deliveries = load_data()
    return clean_data(matches, deliveries)

try:
    matches, deliveries = get_data()
except FileNotFoundError:
    st.error("Dataset files not found in data/ directory. Please add matches.csv and deliveries.csv.")
    st.stop()

# Calculate KPIs
@st.cache_data(persist="disk")
def get_kpis(_matches, _deliveries):
    kpis = calculate_kpis(_matches, _deliveries)
    save_precomputed_stats(kpis)
    return kpis

kpis = get_kpis(matches, deliveries)

# Check for empty data
if matches.empty or deliveries.empty:
    st.error("No data available in the dataset. Please check matches.csv and deliveries.csv.")
    st.stop()

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7= st.tabs(["🏠 Overview", "📊 Team Analysis", "👤 Player Stats", "🏟️ Venue Insights", "📅 Season Analysis", "🏏 Team-Specific Analysis","🤝 Head-to-Head Analysis"])

with tab1:
    st.header("Overview")
    col1, col2, col3 = st.columns(3)
    
    # Total Matches
    col1.metric("Total Matches", kpis['total_matches'])
    
    # Most Wins
    with col2:
        if not kpis['most_wins'].empty:
            team = kpis['most_wins'].index[0]
            wins = int(kpis['most_wins'].values[0])
            st.write("**Most Wins**")
            st.markdown(
                f"""
                <div style='text-align: left;'>
                    <div>{team}</div>
                    <div>Wins: {wins}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.write("**Most Wins**")
            st.markdown(
                """
                <div style='text-align: left;'>
                    <div>None</div>
                    <div>Wins: 0</div>
                </div>
                """,
                unsafe_allow_html=True
            )
    
    # Most Losses
    with col3:
        if not kpis['most_losses'].empty:
            team = kpis['most_losses'].index[0]
            losses = int(kpis['most_losses'].values[0])
            st.write("**Most Losses**")
            st.markdown(
                f"""
                <div style='text-align: left;'>
                    <div>{team}</div>
                    <div>Losses: {losses}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.write("**Most Losses**")
            st.markdown(
                """
                <div style='text-align: left;'>
                    <div>None</div>
                    <div>Losses: 0</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.subheader("IPL Winners per Season")
    st.markdown(
    """
    <div style='text-align: center;'>
        <img src='https://raw.githubusercontent.com/kindo-tk/images/main/wp3991237-removebg-preview.png' width='200' height='180'/>
    </div>
    """,
    unsafe_allow_html=True
    )
    if not kpis['season_winners'].empty:
        # Create a DataFrame with a constant y-value for all bars
        season_winners_df = kpis['season_winners'].copy()
        season_winners_df['bar_height'] = 1  # Constant height for all bars
        
        # Sort the DataFrame by season in ascending order
        season_winners_df = season_winners_df.sort_values('season', ascending=True)
        
        # Create a list of seasons in sorted order for the x-axis
        sorted_seasons = season_winners_df['season'].astype(str).tolist()
        
        fig = px.bar(
            season_winners_df,
            x='season',
            y='bar_height',
            color='winner',
            text='winner',
            title="IPL Winners per Season",
            labels={'season': 'Season', 'bar_height': ''},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig.update_traces(textposition='auto', textfont=dict(size=12))
        fig.update_layout(
            xaxis={
                'tickangle': 45,
                'showticklabels': True,
                'type': 'category',
                'categoryorder': 'array', 
                'categoryarray': sorted_seasons 
            },
            xaxis_tickfont_size=12,
            yaxis={'showticklabels': False, 'title': ''},
            showlegend=True,
            legend_title_text="Winning Team",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for IPL Winners per Season.")
    
    st.subheader("Most IPL Titles by Team")
    if not kpis['most_titles'].empty:
        fig = px.bar(
            x=kpis['most_titles'].values,
            y=kpis['most_titles'].index,
            orientation='h',  # Horizontal bar chart
            labels={'x': 'Titles', 'y': 'Team'},
            title="Teams with Most IPL Titles",
            color_discrete_sequence=['#bcbd22']
        )
        fig.update_layout(
            xaxis_tickfont_size=12,
            yaxis={'tickfont_size': 12},
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(kpis['most_titles'].reset_index().rename(columns={'index': 'Team', 'winner': 'Titles'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for IPL Titles.")


    st.subheader("Cumulative Runs by Top Batters")
    if not kpis['cumulative_runs'].empty:
        
        cumulative_runs_df = kpis['cumulative_runs'].reset_index().sort_values('season')
        fig = px.line(cumulative_runs_df, x='season', y=kpis['cumulative_runs'].columns, 
                     title="Cumulative Runs by Top Batters", color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(xaxis_title="Season", yaxis_title="Cumulative Runs", legend_title="Batter",
                         xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No data available for Cumulative Runs.")
    
    st.download_button("Download Overview Stats", kpis['team_matches'].to_csv(), "overview_stats.csv")

with tab2:
    st.header("Team Analysis")
    
    st.subheader("Matches per Team")
    if not kpis['team_matches'].empty:
        fig = px.bar(x=kpis['team_matches'].index, y=kpis['team_matches'].values, 
                    labels={'x': 'Team', 'y': 'Matches'}, title="Matches per Team",
                    color_discrete_sequence=['#1f77b4'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['team_matches'].reset_index().rename(columns={'index': 'Team', 0: 'Matches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Matches per Team.")
    
    st.subheader("Toss Wins per Team")
    if not kpis['toss_wins'].empty:
        fig = px.bar(x=kpis['toss_wins'].index, y=kpis['toss_wins'].values, 
                    labels={'x': 'Team', 'y': 'Toss Wins'}, title="Toss Wins per Team",
                    color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['toss_wins'].reset_index().rename(columns={'index': 'Team', 'toss_winner': 'Toss Wins'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Toss Wins per Team.")
    
    st.subheader("Highest Team Totals")
    top_totals = kpis['highest_team_totals']
    st.dataframe(top_totals.rename(columns={
        'batting_team': 'Team',
        'opponent': 'Against',
        'total_runs': 'Runs'
    }))

    fig = px.bar(
        top_totals,
        x='batting_team',
        y='total_runs',
        color='opponent',
        text='total_runs',
        title="Top 10 Highest Team Totals (with Opponents)",
        labels={'batting_team': 'Team', 'total_runs': 'Runs', 'opponent': 'Against'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Team with Most Winning Percentage
    st.subheader("Team Winning Percentages")
    if not kpis['team_matches'].empty and not kpis['most_wins'].empty:
        # Calculate winning percentage
        win_percentage = (kpis['most_wins'] / kpis['team_matches'] * 100).fillna(0).sort_values(ascending=False)
        fig = px.bar(x=win_percentage.index, y=win_percentage.values, 
                     labels={'x': 'Team', 'y': 'Winning Percentage (%)'}, title="Team Winning Percentages",
                     color_discrete_sequence=['#2ca02c'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(win_percentage.reset_index().rename(columns={'index': 'Team', 'winner': 'Winning Percentage (%)'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Winning Percentages.")
    
    # Teams Playing Most Finals
    st.subheader("Teams Playing Most Finals")
    if 'id' in matches.columns and 'season' in matches.columns:
        finals = matches.groupby('season')['id'].idxmax()
        final_matches = matches.loc[finals, ['team1', 'team2']]
        final_appearances = pd.concat([final_matches['team1'], final_matches['team2']]).value_counts()
        if not final_appearances.empty:
            fig = px.bar(x=final_appearances.index, y=final_appearances.values, 
                         labels={'x': 'Team', 'y': 'Number of Finals'}, title="Teams Playing Most Finals",
                         color_discrete_sequence=['#d62728'])
            fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                             xaxis_tickfont_size=12, dragmode='pan')
            fig.update_xaxes(fixedrange=False)
            st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
            st.dataframe(final_appearances.reset_index().rename(columns={'index': 'Team', 0: 'Number of Finals'}), 
                        use_container_width=True, hide_index=True)
        else:
            st.warning("No data available for Teams Playing Finals.")
    else:
        st.warning("Required columns for finals calculation are missing.")
    
    st.download_button("Download Team Stats", kpis['team_matches'].to_csv(), "team_stats.csv")

with tab3:
    st.header("Player Statistics")
    
    st.subheader("Orange Cap (Most Runs per Season)")
    if not kpis['orange_cap'].empty:
        orange_cap_sorted = kpis['orange_cap'].sort_values('season')
        fig = px.bar(
            orange_cap_sorted,
            x='season',
            y='batsman_runs',
            color='batter',
            text='batter',
            title="Orange Cap Winners",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition='auto', textfont=dict(size=12))
        fig.update_layout(
            xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category', 
                  'categoryorder': 'array', 'categoryarray': sorted(kpis['orange_cap']['season'].unique())},
            xaxis_tickfont_size=12,
            xaxis_title="Season",
            yaxis_title="Runs",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(orange_cap_sorted.rename(columns={'batter': 'Batter', 'batsman_runs': 'Runs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No Orange Cap data available.")
    
    st.subheader("Purple Cap (Most Wickets per Season)")
    if not kpis['purple_cap'].empty:
        purple_cap_sorted = kpis['purple_cap'].sort_values('season')
        fig = px.bar(
            purple_cap_sorted,
            x='season',
            y='player_dismissed',
            color='bowler',
            text='bowler',
            title="Purple Cap Winners",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='auto', textfont=dict(size=12))
        fig.update_layout(
            xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category', 
                  'categoryorder': 'array', 'categoryarray': sorted(kpis['purple_cap']['season'].unique())},
            xaxis_tickfont_size=12,
            xaxis_title="Season",
            yaxis_title="Wickets",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(purple_cap_sorted.rename(columns={'bowler': 'Bowler', 'player_dismissed': 'Wickets'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No Purple Cap data available.")
    
    st.subheader("Players with Most Orange Caps")
    if not kpis['orange_cap'].empty:
        orange_cap_counts = kpis['orange_cap']['batter'].value_counts()
        max_orange_caps = orange_cap_counts.max()
        top_orange_cap_winners = orange_cap_counts[orange_cap_counts == max_orange_caps]
        fig = px.bar(x=orange_cap_counts.index, y=orange_cap_counts.values, 
                     labels={'x': 'Batter', 'y': 'Number of Orange Caps'}, title="Players with Most Orange Caps",
                     color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(orange_cap_counts.reset_index().rename(columns={'index': 'Batter', 'batter': 'Number of Orange Caps'}), 
                    use_container_width=True, hide_index=True)
        st.write(f"Player(s) with the most Orange Caps ({max_orange_caps}): {', '.join(top_orange_cap_winners.index)}")
    else:
        st.warning("No data available for Orange Cap counts.")
    
    st.subheader("Players with Most Purple Caps")
    if not kpis['purple_cap'].empty:
        purple_cap_counts = kpis['purple_cap']['bowler'].value_counts()
        max_purple_caps = purple_cap_counts.max()
        top_purple_cap_winners = purple_cap_counts[purple_cap_counts == max_purple_caps]
        fig = px.bar(x=purple_cap_counts.index, y=purple_cap_counts.values, 
                     labels={'x': 'Bowler', 'y': 'Number of Purple Caps'}, title="Players with Most Purple Caps",
                     color_discrete_sequence=['#9467bd'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(purple_cap_counts.reset_index().rename(columns={'index': 'Bowler', 'bowler': 'Number of Purple Caps'}), 
                    use_container_width=True, hide_index=True)
        st.write(f"Player(s) with the most Purple Caps ({max_purple_caps}): {', '.join(top_purple_cap_winners.index)}")
    else:
        st.warning("No data available for Purple Cap counts.")
    
    st.subheader("Most Runs Overall")
    if not kpis['most_runs_total'].empty:
        fig = px.bar(x=kpis['most_runs_total'].index, y=kpis['most_runs_total'].values, 
                    labels={'x': 'Batter', 'y': 'Runs'}, title="Most Runs Overall",
                    color_discrete_sequence=['#2ca02c'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_runs_total'].reset_index().rename(columns={'index': 'Batter', 'batsman_runs': 'Runs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Runs Overall.")
    
    st.subheader("Most Wickets Overall")
    if not kpis['most_wickets_total'].empty:
        fig = px.bar(x=kpis['most_wickets_total'].index, y=kpis['most_wickets_total'].values, 
                    labels={'x': 'Bowler', 'y': 'Wickets'}, title="Most Wickets Overall",
                    color_discrete_sequence=['#d62728'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_wickets_total'].reset_index().rename(columns={'index': 'Bowler', 'player_dismissed': 'Wickets'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Wickets Overall.")
    
    st.subheader("Most Sixes Overall")
    if not kpis['most_sixes'].empty:
        fig = px.bar(x=kpis['most_sixes'].index, y=kpis['most_sixes'].values, 
                    labels={'x': 'Batter', 'y': 'Sixes'}, title="Most Sixes Overall",
                    color_discrete_sequence=['#9467bd'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_sixes'].reset_index().rename(columns={'index': 'Batter', 'batsman_runs': 'Sixes'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Sixes Overall.")
    
    st.subheader("Most Sixes Per Season")
    if not kpis['most_sixes_per_season'].empty:
        fig = px.bar(
            kpis['most_sixes_per_season'],
            x='season',
            y='batsman_runs',
            color='batter',
            text='batter',
            title="Most Sixes Per Season",
            color_discrete_sequence=px.colors.qualitative.Pastel1
        )
        fig.update_traces(textposition='auto', textfont=dict(size=12))
        fig.update_layout(
            xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'},
            xaxis_tickfont_size=12,
            xaxis_title="Season",
            yaxis_title="Sixes",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(kpis['most_sixes_per_season'].rename(columns={'batter': 'Batter', 'batsman_runs': 'Sixes'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Sixes Per Season.")
    
    st.subheader("Most Fours Overall")
    if not kpis['most_fours'].empty:
        fig = px.bar(x=kpis['most_fours'].index, y=kpis['most_fours'].values, 
                    labels={'x': 'Batter', 'y': 'Fours'}, title="Most Fours Overall",
                    color_discrete_sequence=['#ffbb78'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_fours'].reset_index().rename(columns={'index': 'Batter', 'batsman_runs': 'Fours'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Fours Overall.")
    
    st.subheader("Most Fours Per Season")
    if not kpis['most_fours_per_season'].empty:
        fig = px.bar(
            kpis['most_fours_per_season'],
            x='season',
            y='batsman_runs',
            color='batter',
            text='batter',
            title="Most Fours Per Season",
            color_discrete_sequence=px.colors.qualitative.Pastel2
        )
        fig.update_traces(textposition='auto', textfont=dict(size=12))
        fig.update_layout(
            xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'},
            xaxis_tickfont_size=12,
            xaxis_title="Season",
            yaxis_title="Fours",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(kpis['most_fours_per_season'].rename(columns={'batter': 'Batter', 'batsman_runs': 'Fours'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Fours Per Season.")
    
    st.subheader("Most Catches")
    if not kpis['most_catches'].empty:
        fig = px.bar(x=kpis['most_catches'].index, y=kpis['most_catches'].values, 
                    labels={'x': 'Fielder', 'y': 'Catches'}, title="Most Catches",
                    color_discrete_sequence=['#17becf'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_catches'].reset_index().rename(columns={'index': 'Fielder', 'player_dismissed': 'Catches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Catches.")
    
    st.subheader("Most Stumps")
    if not kpis['most_stumps'].empty:
        fig = px.bar(x=kpis['most_stumps'].index, y=kpis['most_stumps'].values, 
                    labels={'x': 'Fielder', 'y': 'Stumps'}, title="Most Stumps",
                    color_discrete_sequence=['#bcbd22'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_stumps'].reset_index().rename(columns={'index': 'Fielder', 'player_dismissed': 'Stumps'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Stumps.")
    
    st.subheader("Most Run-outs")
    if not kpis['most_run_outs'].empty:
        fig = px.bar(x=kpis['most_run_outs'].index, y=kpis['most_run_outs'].values, 
                    labels={'x': 'Fielder', 'y': 'Run-outs'}, title="Most Run-outs",
                    color_discrete_sequence=['#7f7f7f'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_run_outs'].reset_index().rename(columns={'index': 'Fielder', 'player_dismissed': 'Run-outs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Run-outs.")
    
    st.subheader("Most Matches Played")
    if not kpis['most_matches_played'].empty:
        fig = px.bar(x=kpis['most_matches_played'].index, y=kpis['most_matches_played'].values, 
                    labels={'x': 'Player', 'y': 'Matches'}, title="Most Matches Played",
                    color_discrete_sequence=['#e377c2'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_matches_played'].reset_index().rename(columns={'index': 'Player', 'match_id': 'Matches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Matches Played.")
    
    st.subheader("Most Player of the Match Awards")
    if not kpis['most_pom_awards'].empty:
        fig = px.bar(x=kpis['most_pom_awards'].index, y=kpis['most_pom_awards'].values, 
                    labels={'x': 'Player', 'y': 'Awards'}, title="Most Player of the Match Awards",
                    color_discrete_sequence=['#f7b6d2'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(kpis['most_pom_awards'].reset_index().rename(columns={'index': 'Player', 'player_of_match': 'Awards'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Most Player of the Match Awards.")
    
    st.download_button("Download Player Stats", kpis['orange_cap'].to_csv(), "player_stats.csv")

with tab4:
    st.header("Venue Insights")
    
    st.subheader("Matches per Stadium (Top 10 Venues)")
    if not kpis['stadium_matches'].empty:
        top_10_stadiums = kpis['stadium_matches'].head(10)
        fig = px.bar(x=top_10_stadiums.index, y=top_10_stadiums.values, 
                    labels={'x': 'Venue', 'y': 'Matches'}, title="Matches per Stadium (Top 10)",
                    color_discrete_sequence=['#8c564b'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(top_10_stadiums.reset_index().rename(columns={'index': 'Venue', 'venue': 'Matches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning("No data available for Matches per Stadium.")
    
    st.download_button("Download Venue Stats", kpis['stadium_matches'].to_csv(), "venue_stats.csv")

with tab5:
    st.header("Season Analysis")
    
    seasons = sorted(matches['season'].unique())
    selected_season = st.selectbox("Select Season", seasons)
    
    st.subheader(f"Top 5 Run Scorers in {selected_season}")
    season_runs = deliveries[deliveries['season'] == selected_season].groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(5)
    if not season_runs.empty:
        fig = px.bar(x=season_runs.index, y=season_runs.values, 
                    labels={'x': 'Batter', 'y': 'Runs'}, title=f"Top 5 Run Scorers in {selected_season}",
                    color_discrete_sequence=['#1f77b4'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_runs.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Runs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No run scoring data available for {selected_season}.")
    
    st.subheader(f"Top 5 Wicket Takers in {selected_season}")
    season_wickets = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['dismissal_kind'].isin(['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']))
    ].groupby('bowler')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not season_wickets.empty:
        fig = px.bar(x=season_wickets.index, y=season_wickets.values, 
                    labels={'x': 'Bowler', 'y': 'Wickets'}, title=f"Top 5 Wicket Takers in {selected_season}",
                    color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_wickets.reset_index().rename(columns={'bowler': 'Bowler', 'player_dismissed': 'Wickets'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No wicket-taking data available for {selected_season}.")
    
    st.subheader(f"Top 5 Catch Takers in {selected_season}")
    season_catches = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['dismissal_kind'] == 'caught')
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not season_catches.empty:
        fig = px.bar(x=season_catches.index, y=season_catches.values, 
                    labels={'x': 'Fielder', 'y': 'Catches'}, title=f"Top 5 Catch Takers in {selected_season}",
                    color_discrete_sequence=['#2ca02c'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_catches.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Catches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No catch data available for {selected_season}.")
    
    st.subheader(f"Top 5 Stumpings in {selected_season}")
    season_stumps = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['dismissal_kind'] == 'stumped')
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not season_stumps.empty:
        fig = px.bar(x=season_stumps.index, y=season_stumps.values, 
                    labels={'x': 'Fielder', 'y': 'Stumps'}, title=f"Top 5 Stumpings in {selected_season}",
                    color_discrete_sequence=['#d62728'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_stumps.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Stumps'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No stumping data available for {selected_season}.")
    
    st.subheader(f"Top 5 Run-outs in {selected_season}")
    season_run_outs = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['dismissal_kind'] == 'run out')
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not season_run_outs.empty:
        fig = px.bar(x=season_run_outs.index, y=season_run_outs.values, 
                    labels={'x': 'Fielder', 'y': 'Run-outs'}, title=f"Top 5 Run-outs in {selected_season}",
                    color_discrete_sequence=['#9467bd'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_run_outs.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Run-outs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No run-out data available for {selected_season}.")
    
    st.subheader(f"Top 5 Six Hitters in {selected_season}")
    season_sixes = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['batsman_runs'] == 6)
    ].groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(5)
    if not season_sixes.empty:
        fig = px.bar(x=season_sixes.index, y=season_sixes.values, 
                    labels={'x': 'Batter', 'y': 'Sixes'}, title=f"Top 5 Six Hitters in {selected_season}",
                    color_discrete_sequence=['#ffbb78'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_sixes.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Sixes'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No sixes data available for {selected_season}.")
    
    st.subheader(f"Top 5 Four Hitters in {selected_season}")
    season_fours = deliveries[
        (deliveries['season'] == selected_season) & 
        (deliveries['batsman_runs'] == 4)
    ].groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(5)
    if not season_fours.empty:
        fig = px.bar(x=season_fours.index, y=season_fours.values, 
                    labels={'x': 'Batter', 'y': 'Fours'}, title=f"Top 5 Four Hitters in {selected_season}",
                    color_discrete_sequence=['#17becf'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(season_fours.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Fours'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No fours data available for {selected_season}.")
    
    st.download_button(f"Download Season {selected_season} Stats", season_runs.to_csv(), f"season_{selected_season}_stats.csv")

with tab6:
    st.header("Team-Specific Analysis")
    
    teams = sorted(set(matches['team1'].unique()) | set(matches['team2'].unique()))
    selected_team = st.selectbox("Select Team", teams)
    
    team_deliveries = deliveries[
        (deliveries['batting_team'] == selected_team) | 
        (deliveries['bowling_team'] == selected_team)
    ]
    
    st.subheader(f"Top 5 Run Scorers for {selected_team}")
    team_runs = team_deliveries[team_deliveries['batting_team'] == selected_team].groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(5)
    if not team_runs.empty:
        fig = px.bar(x=team_runs.index, y=team_runs.values, 
                    labels={'x': 'Batter', 'y': 'Runs'}, title=f"Top 5 Run Scorers for {selected_team}",
                    color_discrete_sequence=['#1f77b4'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_runs.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Runs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No run scoring data available for {selected_team}.")
    
    st.subheader(f"Top 5 Wicket Takers for {selected_team}")
    team_wickets = team_deliveries[
        (team_deliveries['bowling_team'] == selected_team) & 
        (team_deliveries['dismissal_kind'].isin(['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket']))
    ].groupby('bowler')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not team_wickets.empty:
        fig = px.bar(x=team_wickets.index, y=team_wickets.values, 
                    labels={'x': 'Bowler', 'y': 'Wickets'}, title=f"Top 5 Wicket Takers for {selected_team}",
                    color_discrete_sequence=['#ff7f0e'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_wickets.reset_index().rename(columns={'bowler': 'Bowler', 'player_dismissed': 'Wickets'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No wicket-taking data available for {selected_team}.")
    
    st.subheader(f"Top 5 Catch Takers for {selected_team}")
    team_catches = team_deliveries[
        (team_deliveries['dismissal_kind'] == 'caught') & 
        (team_deliveries['batting_team'] != selected_team)
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not team_catches.empty:
        fig = px.bar(x=team_catches.index, y=team_catches.values, 
                    labels={'x': 'Fielder', 'y': 'Catches'}, title=f"Top 5 Catch Takers for {selected_team}",
                    color_discrete_sequence=['#2ca02c'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_catches.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Catches'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No catch data available for {selected_team}.")
    
    st.subheader(f"Top 5 Stumpings for {selected_team}")
    team_stumps = team_deliveries[
        (team_deliveries['dismissal_kind'] == 'stumped') & 
        (team_deliveries['batting_team'] != selected_team)
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not team_stumps.empty:
        fig = px.bar(x=team_stumps.index, y=team_stumps.values, 
                    labels={'x': 'Fielder', 'y': 'Stumps'}, title=f"Top 5 Stumpings for {selected_team}",
                    color_discrete_sequence=['#d62728'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_stumps.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Stumps'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No stumping data available for {selected_team}.")
    
    st.subheader(f"Top 5 Run-outs for {selected_team}")
    team_run_outs = team_deliveries[
        (team_deliveries['dismissal_kind'] == 'run out') & 
        (team_deliveries['batting_team'] != selected_team)
    ].groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(5)
    if not team_run_outs.empty:
        fig = px.bar(x=team_run_outs.index, y=team_run_outs.values, 
                    labels={'x': 'Fielder', 'y': 'Run-outs'}, title=f"Top 5 Run-outs for {selected_team}",
                    color_discrete_sequence=['#9467bd'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_run_outs.reset_index().rename(columns={'fielder': 'Fielder', 'player_dismissed': 'Run-outs'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No run-out data available for {selected_team}.")
    
    st.subheader(f"Top 5 Six Hitters for {selected_team}")
    team_sixes = team_deliveries[
        (team_deliveries['batting_team'] == selected_team) & 
        (team_deliveries['batsman_runs'] == 6)
    ].groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(5)
    if not team_sixes.empty:
        fig = px.bar(x=team_sixes.index, y=team_sixes.values, 
                    labels={'x': 'Batter', 'y': 'Sixes'}, title=f"Top 5 Six Hitters for {selected_team}",
                    color_discrete_sequence=['#ffbb78'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_sixes.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Sixes'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No sixes data available for {selected_team}.")
    
    st.subheader(f"Top 5 Four Hitters for {selected_team}")
    team_fours = team_deliveries[
        (team_deliveries['batting_team'] == selected_team) & 
        (team_deliveries['batsman_runs'] == 4)
    ].groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(5)
    if not team_fours.empty:
        fig = px.bar(x=team_fours.index, y=team_fours.values, 
                    labels={'x': 'Batter', 'y': 'Fours'}, title=f"Top 5 Four Hitters for {selected_team}",
                    color_discrete_sequence=['#17becf'])
        fig.update_layout(xaxis={'tickangle': 45, 'showticklabels': True, 'type': 'category'}, 
                         xaxis_tickfont_size=12, dragmode='pan')
        fig.update_xaxes(fixedrange=False)
        st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True})
        st.dataframe(team_fours.reset_index().rename(columns={'batter': 'Batter', 'batsman_runs': 'Fours'}), 
                    use_container_width=True, hide_index=True)
    else:
        st.warning(f"No fours data available for {selected_team}.")
    
    st.download_button(f"Download {selected_team} Stats", team_runs.to_csv(), f"{selected_team}_stats.csv")
with tab7:
    st.header("Head-to-Head Analysis")
    teams = sorted(set(matches['team1'].unique()) | set(matches['team2'].unique()))
    team1 = st.selectbox("Select Team 1", teams, key="team1_select")
    team2 = st.selectbox("Select Team 2", teams, key="team2_select")
    
    if team1 != team2:
        h2h_matches = matches[
            ((matches['team1'] == team1) & (matches['team2'] == team2)) |
            ((matches['team1'] == team2) & (matches['team2'] == team1))
        ]
        h2h_wins = h2h_matches['winner'].value_counts()
        st.write(f"Total Matches: {len(h2h_matches)}")
        
        if not h2h_wins.empty:
            fig = px.pie(
                names=h2h_wins.index,
                values=h2h_wins.values,
                title=f"{team1} vs {team2} - Win Distribution"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No matches found between these teams.")
    else:
        st.warning("Please select two different teams.")
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; font-size: 0.9em; padding-top: 20px;'>
        <strong>IPL Data Analysis Dashboard (2008–2024)</strong><br>
        Created by <a href='https://kindo-tk.github.io/tk.github.io/' target='_blank'>Tufan Kundu</a> ·
        <a href='https://github.com/kindo-tk' target='_blank'>GitHub</a> ·
        <a href='https://www.linkedin.com/in/tufan-kundu-577945221/' target='_blank'>LinkedIn</a>
    </div>
    """,
    unsafe_allow_html=True
)
