# IPL Data Analysis Dashboard
![Python](https://img.shields.io/badge/Python-3.10-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38.0-red)

A professional, interactive dashboard for analyzing Indian Premier League (IPL) data from 2008 to 2024 using Python, Pandas, and Streamlit.

---

## Overview

The goal of this project is to explore IPL data across multiple seasons and extract insights through interactive visualizations. Key statistics like highest scores, best players, and venue patterns are computed and presented using Streamlit and Plotly.

---

## Features

- **Overview**: Total matches, most wins, losses, and cumulative runs by top batters.
- **Team Analysis**: Matches per team, toss wins, highest totals, winning percentages.
- **Player Stats**: Orange/purple cap winners, most runs/wickets, sixes/fours, catches, stumpings, run-outs, and Player of the Match awards.
- **Venue Insights**: Matches per stadium.
- **Season Analysis**: Top performers (runs, wickets, catches, etc.)
- **Team-Specific Analysis**: Detailed metrics for a selected team, including top performers and win/loss trends.
- **Head-to-Head Analysis**: win distribution between two teams.

---

## Dataset

- **Source**: [Kaggle – IPL Complete Dataset (2008–2020)](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)
- **Files Used**:
  - `matches.csv` – match-level details like team, toss, result, season
  - `deliveries.csv` – ball-by-ball level statistics including batsman, bowler, and dismissal info

---


## Demo

<a href="https://ipldataanalysisproject.streamlit.app/">Click here</a>

---

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/kindo-tk/ipl_data_analysis_project.git
   ```
2. **Navigate to the project directory:**

    ```sh
    cd ipl_data_analysis_project
    ```

3. **Create a virtual environment(using conda):**

    ```sh
    conda create -n ipl python=3.10
    ```

4. **Activate the virtual environment:**

   ```sh
   conda activate ipl
   ```

5. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

6. **Run the Streamlit application:**

    ```sh
    streamlit run streamlit_app.py
    ```
---

## Technologies Used

- Python 3.10
- Pandas, NumPy
- Streamlit
- Plotly
> See [`requirements.txt`](requirements.txt) for the full list of dependencies.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contact 
For any inquiries or feedback, please contact:

- <a href="https://www.linkedin.com/in/tufan-kundu-577945221/">Tufan Kundu (LinkedIn)</a>
- Email: tufan.kundu11@gmail.com

---
## Contributing

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch for your changes (`git checkout -b feature/your-feature-name`).
3. Make your changes and commit them (`git commit -m "Add your message here"`).
4. Push to your branch (`git push origin feature/your-feature-name`).
5. Submit a pull request.

---

## Acknowledgments

- **Dataset**: Sourced from Kaggle ([IPL Complete Dataset](https://www.kaggle.com/datasets/patrickb1912/ipl-complete-dataset-20082020)).
- **Tools**: Built with [Streamlit](https://streamlit.io/) for the dashboard and [Plotly](https://plotly.com/) for interactive visualizations.

