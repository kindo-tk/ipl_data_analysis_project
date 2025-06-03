import pandas as pd
import os

def calculate_kpis(matches, deliveries):
    """Calculate KPIs for IPL analysis with error handling."""
    kpis = {}
    
    try:
        # Total matches
        try:
            kpis['total_matches'] = matches.shape[0]
        except Exception as e:
            print(f"Warning: Error calculating total matches: {str(e)}")
            kpis['total_matches'] = 0
        
        # Matches per team
        try:
            kpis['team_matches'] = pd.concat([matches['team1'], matches['team2']]).value_counts()
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for team matches calculation.")
            kpis['team_matches'] = pd.Series()
        
        # Most wins
        try:
            team_wins = matches[matches['winner'] != 'No Result']['winner'].value_counts()
            kpis['most_wins'] = team_wins if not team_wins.empty else pd.Series()  # Removed .head(1)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for most wins calculation.")
            kpis['most_wins'] = pd.Series()
        
        # Most losses
        try:
            kpis['most_losses'] = (kpis['team_matches'] - team_wins).fillna(kpis['team_matches']).sort_values(ascending=False).head(1)
        except NameError as e:
            print(f"Warning: Error calculating most losses: {str(e)}.")
            kpis['most_losses'] = pd.Series()
        
        # Toss wins
        try:
            kpis['toss_wins'] = matches['toss_winner'].value_counts()
            kpis['most_toss_wins'] = kpis['toss_wins'].head(1) if not kpis['toss_wins'].empty else pd.Series()
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for toss wins calculation.")
            kpis['toss_wins'] = pd.Series()
            kpis['most_toss_wins'] = pd.Series()
        
        # Orange Cap
        try:
            runs_per_season = deliveries.groupby(['season', 'batter'])['batsman_runs'].sum().reset_index()
            kpis['orange_cap'] = runs_per_season.loc[runs_per_season.groupby('season')['batsman_runs'].idxmax()]
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for orange cap calculation.")
            kpis['orange_cap'] = pd.DataFrame()
        
        # Purple Cap
        try:
            wickets = deliveries[deliveries['dismissal_kind'].isin(['caught', 'bowled', 'lbw', 'stumped', 'caught and bowled', 'hit wicket'])]
            wickets_per_season = wickets.groupby(['season', 'bowler'])['player_dismissed'].count().reset_index()
            kpis['purple_cap'] = wickets_per_season.loc[wickets_per_season.groupby('season')['player_dismissed'].idxmax()]
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for purple cap calculation.")
            kpis['purple_cap'] = pd.DataFrame()
        
        # Most runs overall
        try:
            kpis['most_runs_total'] = deliveries.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for most runs calculation.")
            kpis['most_runs_total'] = pd.Series()
        
        # Most wickets overall
        try:
            kpis['most_wickets_total'] = wickets.groupby('bowler')['player_dismissed'].count().sort_values(ascending=False).head(10)
        except NameError as e:
            print(f"Warning: Error calculating most wickets: {str(e)}.")
            kpis['most_wickets_total'] = pd.Series()
        
        # Most sixes
        try:
            sixes = deliveries[deliveries['batsman_runs'] == 6]
            kpis['most_sixes'] = sixes.groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(10)
            sixes_per_season = sixes.groupby(['season', 'batter'])['batsman_runs'].count().reset_index()
            kpis['most_sixes_per_season'] = sixes_per_season.loc[sixes_per_season.groupby('season')['batsman_runs'].idxmax()]
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for sixes calculation.")
            kpis['most_sixes'] = pd.Series()
            kpis['most_sixes_per_season'] = pd.DataFrame()
        
        # Most fours
        try:
            fours = deliveries[deliveries['batsman_runs'] == 4]
            kpis['most_fours'] = fours.groupby('batter')['batsman_runs'].count().sort_values(ascending=False).head(10)
            fours_per_season = fours.groupby(['season', 'batter'])['batsman_runs'].count().reset_index()
            kpis['most_fours_per_season'] = fours_per_season.loc[fours_per_season.groupby('season')['batsman_runs'].idxmax()]
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for fours calculation.")
            kpis['most_fours'] = pd.Series()
            kpis['most_fours_per_season'] = pd.DataFrame()
        
        # Most catches
        try:
            catches = deliveries[deliveries['dismissal_kind'] == 'caught']
            kpis['most_catches'] = catches.groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for catches calculation.")
            kpis['most_catches'] = pd.Series()
        
        # Most stumps
        try:
            stumps = deliveries[deliveries['dismissal_kind'] == 'stumped']
            kpis['most_stumps'] = stumps.groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for stumps calculation.")
            kpis['most_stumps'] = pd.Series()
        
        # Most run-outs
        try:
            run_outs = deliveries[deliveries['dismissal_kind'] == 'run out']
            kpis['most_run_outs'] = run_outs.groupby('fielder')['player_dismissed'].count().sort_values(ascending=False).head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for run-outs calculation.")
            kpis['most_run_outs'] = pd.Series()
        
        # Most matches played
        try:
            player_matches = deliveries.groupby(['batter', 'match_id']).size().reset_index().groupby('batter')['match_id'].count()
            kpis['most_matches_played'] = player_matches.sort_values(ascending=False).head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for matches played calculation.")
            kpis['most_matches_played'] = pd.Series()

        # Highest team totals with opponent
        try:
            match_teams = matches[['id', 'team1', 'team2']]
            team_totals = deliveries.groupby(['match_id', 'batting_team'])['total_runs'].sum().reset_index()
            team_totals = team_totals.merge(match_teams, left_on='match_id', right_on='id', how='left')

            def get_opponent(row):
                return row['team2'] if row['batting_team'] == row['team1'] else row['team1']

            team_totals['opponent'] = team_totals.apply(get_opponent, axis=1)
            team_totals = team_totals[['match_id', 'batting_team', 'opponent', 'total_runs']]
            kpis['highest_team_totals'] = team_totals.sort_values('total_runs', ascending=False).head(10)

        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for team totals calculation.")
            kpis['highest_team_totals'] = pd.DataFrame()
        
        # Most player of the match awards
        try:
            kpis['most_pom_awards'] = matches[matches['player_of_match'] != 'None']['player_of_match'].value_counts().head(10)
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for player of the match awards calculation.")
            kpis['most_pom_awards'] = pd.Series()
        
        # Stadium matches
        try:
            kpis['stadium_matches'] = matches['venue'].value_counts()
        except KeyError as e:
            print(f"Warning: Missing column {str(e)} for stadium matches calculation.")
            kpis['stadium_matches'] = pd.Series()
        
        # Cumulative runs
        try:
            runs_per_season = deliveries.groupby(['season', 'batter'])['batsman_runs'].sum().reset_index()
            top_batters = runs_per_season.groupby('batter')['batsman_runs'].sum().sort_values(ascending=False).head(5).index
            # Pivot, sort seasons, fill NaNs with 0, then compute cumulative sum
            cumulative_runs = runs_per_season[runs_per_season['batter'].isin(top_batters)].pivot(index='season', columns='batter', values='batsman_runs')
            cumulative_runs = cumulative_runs.sort_index().fillna(0).cumsum()
            kpis['cumulative_runs'] = cumulative_runs
        except (KeyError, ValueError) as e:
            print(f"Warning: Error calculating cumulative runs: {str(e)}.")
            kpis['cumulative_runs'] = pd.DataFrame()
        
        return kpis
    
    except Exception as e:
        raise Exception(f"Unexpected error in calculate_kpis: {str(e)}")

def save_precomputed_stats(kpis):
    """Save precomputed stats to JSON with error handling."""
    try:
        os.makedirs('../data/precomputed_stats', exist_ok=True)
        for key, data in kpis.items():
            if isinstance(data, (pd.DataFrame, pd.Series)) and not data.empty:
                try:
                    data.to_json(f'../data/precomputed_stats/{key}.json')
                except Exception as e:
                    print(f"Warning: Failed to save {key}.json: {str(e)}")
    except OSError as e:
        print(f"Warning: Failed to create directory for precomputed stats: {str(e)}")
    except Exception as e:
        print(f"Warning: Unexpected error while saving precomputed stats: {str(e)}")