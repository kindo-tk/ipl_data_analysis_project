import pandas as pd
import os

def load_data():
    """Load matches and deliveries datasets."""
    matches_path = 'data/matches.csv'
    deliveries_path = 'data/deliveries.csv'

    if not os.path.exists(matches_path) or not os.path.exists(deliveries_path):
        raise FileNotFoundError("Dataset files not found in data/ directory")

    matches = pd.read_csv(matches_path)
    deliveries = pd.read_csv(deliveries_path)
    return matches, deliveries


def clean_data(matches, deliveries):
    """Clean and preprocess datasets with enhanced team name standardization."""
    # Clean matches
    matches = matches.copy()

    # Fix 2020/21 season to 2020
    def clean_season(season_str):
        season_str = str(season_str)
        if season_str in ['2020/21', '2020-21']:
            return 2020
        if '/' in season_str or '-' in season_str:
            year = season_str.split('/')[-1] if '/' in season_str else season_str.split('-')[-1]
            year = year.strip()
            if len(year) == 2:
                year = '20' + year
            return int(year)
        return int(season_str)

    matches['season'] = matches['season'].apply(clean_season)
    matches['city'] = matches['city'].fillna('Unknown')
    matches['winner'] = matches['winner'].fillna('No Result')
    matches['result_margin'] = matches['result_margin'].fillna(0)
    matches['player_of_match'] = matches['player_of_match'].fillna('None')
    matches['method'] = matches['method'].fillna('Normal')
    matches['home_team'] = matches['team1']  # Simplified assumption
    matches['toss_winner'] = matches['toss_winner'].fillna('None')

    # Clean deliveries
    deliveries = deliveries.copy()
    deliveries['dismissal_kind'] = deliveries['dismissal_kind'].fillna('None')
    deliveries['player_dismissed'] = deliveries['player_dismissed'].fillna('None')
    deliveries['fielder'] = deliveries['fielder'].fillna('None')
    deliveries['extras_type'] = deliveries['extras_type'].fillna('None')
    deliveries['batting_team'] = deliveries['batting_team'].fillna('Unknown')
    deliveries['bowling_team'] = deliveries['bowling_team'].fillna('Unknown')
    deliveries['fielder'] = deliveries['fielder'].replace('None', pd.NA)
    # Merge season from matches
    deliveries = deliveries.merge(matches[['id', 'season']], left_on='match_id', right_on='id', how='left')
    unmatched = deliveries['season'].isna().sum()
    if unmatched > 0:
        print(f"Warning: {unmatched} deliveries could not be matched with a season. These will be excluded.")
        deliveries = deliveries.dropna(subset=['season'])
    deliveries['season'] = deliveries['season'].astype(int)
    deliveries = deliveries.drop(columns=['id'])

    # Standardize team names
    team_mapping = {
        'delhi daredevils': 'Delhi Capitals',
        'deccan chargers': 'Sunrisers Hyderabad',
        'kings xi punjab': 'Punjab Kings',
        'royal challengers bengaluru': 'Royal Challengers Bangalore',
        'royal challengers bangalore': 'Royal Challengers Bangalore',
        'rising pune supergiant': 'Rising Pune Supergiants',
        'rising pune supergaints': 'Rising Pune Supergiants',
        'rising pune supergiants': 'Rising Pune Supergiants',
        'gujarat lions': 'Gujarat Titans',
        'pune warriors': 'Rising Pune Supergiants',
        'delhi capitals ': 'Delhi Capitals',
        'sunrisers hyderabad ': 'Sunrisers Hyderabad',
        'punjab kings ': 'Punjab Kings',
        'royal challengers bangalore ': 'Royal Challengers Bangalore',
        'rising pune supergiants ': 'Rising Pune Supergiants',
        'kolkata knight riders ': 'Kolkata Knight Riders',
        'mumbai indians ': 'Mumbai Indians',
        'chennai super kings ': 'Chennai Super Kings',
        'rajasthan royals ': 'Rajasthan Royals',
        'gujarat titans ': 'Gujarat Titans',
        'lucknow super giants ': 'Lucknow Super Giants',
        'delhi capitals': 'Delhi Capitals',
        'sunrisers hyderabad': 'Sunrisers Hyderabad',
        'punjab kings': 'Punjab Kings',
        'kolkata knight riders': 'Kolkata Knight Riders',
        'mumbai indians': 'Mumbai Indians',
        'chennai super kings': 'Chennai Super Kings',
        'rajasthan royals': 'Rajasthan Royals',
        'gujarat titans': 'Gujarat Titans',
        'lucknow super giants': 'Lucknow Super Giants',
    }

    def normalize_team_name(name):
        if isinstance(name, str):
            return name.strip().lower()
        return name

    for col in ['team1', 'team2', 'winner', 'toss_winner', 'home_team']:
        if col in matches.columns:
            matches[col] = matches[col].apply(normalize_team_name)
            matches[col] = matches[col].map(team_mapping).fillna(matches[col])
            matches[col] = matches[col].apply(normalize_team_name)
            matches[col] = matches[col].map(team_mapping).fillna(matches[col])
            matches[col] = matches[col].str.title()
    return matches, deliveries