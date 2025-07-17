# Optimized Route Planner for Profile Visits

This project is a FastAPI-based backend tool that helps plan the most efficient route to visit a series of user profiles based on filtering criteria such as ethnicity, political alignment, or voting score. It leverages geolocation data, clustering, and real road optimization via the OpenRouteService API to return a highly usable, visually intuitive route map as well as providing useful insights regarding the profiles.

---

## Purpose

The purpose of this project is to:
- Filter and locate user profiles from a database according to user-defined criteria
- Plan an optimized real-road route starting from a given coordinate
- Visualize the path clearly with direction arrows and color-coded markers
- Handle large datasets efficiently by clustering the points when API limits are reached

---

## Features

### Database

- The original database used for this project is structured like so :

| Column Name            | Type            | Properties                            |
| ---------------------- | --------------- | ------------------------------------- |
| `UNIQUEID`             | string          | Primary Key, Unique                   |
| `NAME`                 | string          | Required                              |
| `FIRSTNAME`            | string          | Required                              |
| `AGE`                  | integer         | Nullable, Derived from BIRTHDATE      |
| `SECTION`              | string          | Nullable, Categorical                 |
| `NE`                   | integer         | Nullable                              |
| `CIRCONSCRIPT`         | string          | Electoral district, Nullable          |
| `PREFERRED_LANGUAGE`   | string          | ISO language code or full name        |
| `LANGUAGE`             | string          | Language spoken, Nullable             |
| `ORIGIN`               | string          | Ethnicity/National origin             |
| `PERSONNALITY`         | string          | Nullable, Could be MBTI or labels     |
| `BIRTHDATE`            | date            | Required if AGE not stored directly   |
| `GENRE`                | string          | Gender, expected values: M/F/X        |
| `HOME_PHONE`           | string          | Nullable, Optional                    |
| `SECOND_PHONE`         | string          | Nullable, Optional                    |
| `THIRD_PHONE`          | string          | Nullable, Optional                    |
| `MAIN_MAIL`            | string          | Email, Unique                         |
| `SECOND_MAIL`          | string          | Email, Nullable                       |
| `CIVIC`                | string          | Civic number/address ID               |
| `APP`                  | string          | Apartment info, Nullable              |
| `STREET`               | string          | Street name                           |
| `STREET_TYPE`          | string          | e.g., Avenue, Rue, Blvd               |
| `CITY`                 | string          | Required                              |
| `CP`                   | string          | Postal Code                           |
| `ADRESS`               | string          | Full address (may be redundant)       |
| `ANTICIPATED_VOTE`     | string          | Nullable, Expected vote               |
| `2017_RESULTS`         | string          | Nullable, Voting history              |
| `POLITICAL_PROFILE`    | string          | Nullable, Label or score range        |
| `POLITICAL_LEANING`    | string          | e.g., Left, Right, Center             |
| `INTERACTION_SEQUENCE` | string          | Nullable, List of interaction codes   |
| `VOTE_PROBABILITY`     | float (0.0–1.0) | Nullable, Model output                |
| `SUGGESTED_ARGUMENTS`  | string/json     | Nullable, Reasoning or talking points |
| `STRATEGIC_PROFILE`    | string          | Nullable, e.g., "swing voter", etc.   |
| `EXPLANATIONS`         | string/json     | Nullable, Additional reasoning        |

- And was reduced to a simpler one focusing on the most important aspects for the project :

| Column Name           | Type    | Properties                                                  |
| --------------------- | ------- | ----------------------------------------------------------- |
| `id`                  | integer | Primary Key, Auto-incremented                               |
| `uniqueid`            | string  | Unique, Not Null                                            |
| `name`                | string  | Nullable                                                    |
| `nbhood`              | string  | Not Null, Default = `"Loyola"`                              |
| `score_vote`          | integer | Nullable, Expected range: 1 to 5                            |
| `preferred_language`  | string  | Nullable                                                    |
| `native_language`     | string  | Nullable                                                    |
| `origin`              | string  | Nullable, Ethnic/cultural background                        |
| `political_lean`      | string  | Nullable, e.g., "Left", "Right", "Center"                   |
| `personality`         | string  | Nullable, could represent MBTI type or trait label          |
| `political_scale`     | text    | Nullable, may be serialized values or descriptive           |
| `ideal_process`       | string  | Nullable, preferred decision-making or political method     |
| `strategic_profile`   | string  | Nullable, e.g., "Undecided", "Mobilizable", "Committed"     |
| `suggested_arguments` | text    | Nullable, Argumentation points or notes                     |
| `picture_url`         | string  | Nullable, URL to the person's photo                         |
| `latitude`            | float   | Nullable, used for geolocation, computed from the adress    |
| `longitude`           | float   | Nullable, used for geolocation, computed from the adress    |
| `distance`            | float   | Nullable, calculated at runtime (e.g., from starting point) |

- The project contains tools to filter and export subsets of profiles, used notably to target certain profiles if the user decides to.

- Functions used to cleanup the original data and store it into an SQLite database, using `sqlalchemy`.

### Route Optimization
- Uses OpenRouteService's `/optimization` and `/directions` endpoints
- Starts from a user-defined location
- Handles up to 500 points with automatic batching and clustering if necessary

### Intelligent Batching
- Automatically clusters points when over 60 locations are passed
- Prevents API request overload while preserving geographic locality

### Interactive Mapping
- Uses [Folium](https://python-visualization.github.io/folium/) to generate route maps
- Arrows on the route using animated `AntPath`
- Start point highlighted in green
- Other markers colored in a green-to-blue gradient to visualize visit order

### API Endpoint
- POST `/profiles/optimize`
  - Body parameters:
    ```json
    {
      "start_lat": 48.8566,
      "start_lon": 2.3522,
      "ethnicity": "Hispanic",
      "political_alignment": "left",
      "min_score_vote": 0.7
    }
    ```

---

## Technologies Used

- **Python 3.13**
- **FastAPI** — Web API framework
- **SQLAlchemy** — ORM for profile database
- **Folium** — Interactive maps
- **Scikit-learn** — KMeans clustering for optimization batching
- **OpenRouteService** — Routing and optimization API

---

## 📦 Setup & Usage

0. **(Recommended) Setup a venv environment.**
    ```bash
    python -m venv .venv
    call .venv/Scripts/activate
    ```

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the FastAPI app**

    ```bash
    uvicorn backend.main:app --reload
    ```

3. **Register on the app**

When prompted, select option 2 (create admin account).
Enter your username and password.

4. **Use the endpoint**

Authenticate by calling ```/auth/login``` with the username and password defined.

Send a POST request to ```/profiles/optimize``` with the filtering criteria

It returns a GeoJSON of the optimized route

A map is saved locally as ```route_map.html``` or ```clustered_map.html``` depending on the number of points.

To visualize the route, open the file in a browser.

**NB :** You can run the ```cli_tester.py``` file located in ```backend``` for easier use.

4. **Dependencies**

Requires an API key from [OpenRouteService](https://openrouteservice.org/).

## Future Improvements
* Interactive frontend with live map previews

* User authentication and saved preferences

* Exportable map/report PDF

* Better marker clustering for extremely dense zones