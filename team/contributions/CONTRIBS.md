# Contributions - Alvin

# Leadership/Design Document Coordinator
Although our team has slowed down on the scrum documentations, I led a good number of them when we were actively doing them. I also lead the first sprint planning meeting we held. I have been responsible for
creating a lot of the documentation in our Github. As the design document coordinator, I made sure anybody working on the document included information that was relevant and useful.

# Code Contributions

I mainly worked on the frontend portion for the project throughout this quarter:
- Cache Frontend Standings for quicker loading. PR: [189](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/189)
- Implemented Dark Mode theme. PRs: [169](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/169), [189](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/188)
- Implement filtering for props. PR: [137](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/137) 
- Made game cards clickable for a seperate stat page. PR: [124](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/124)
- Pulled standings from backend to display on the home page. PR: [99](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/99)
- Implemented basic game card format. PR: [77](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/77)

# Contributions - Jay

## Leadership/Planning

Over this quarter, I have led scrum meetings and retro meetings. I have also created many issues regarding the frontend and ideas for the user stories on the Kanban board. I have also been responsible for some of the documentation and ensuring we meet deadlines.

## Coding Contributions

Throughout the quarter, I focused mainly on frontend:

- Render list of game cards. PRs: [62](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/62) 
- Create Props Card Component. PRs: [33](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/33) [112](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/112) 
- Refactor Player Prop Component. PRs: [130](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/130)
- Create frontend directory. PR: [47](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/47)
- Design the frontend layout. PR: [87](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/87)
- Create mock data for player props. PR: [38](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/38)
- Build Game Stats Component to render team stats. PRs: [103](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/103)
- Logo Changes + Colorscheme Design Changes. PRs: [179](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/179) [162](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/162)


## User Flows

Many of the frontend changes were around the frontend layout, such as the 3-column design, player prop card component, and creating the team stats page after you click into each live NBA game. My work also involved refactoring many designs and small improvements such as the logo or the colorscheme.

# Contributions - Junhyung

## Leadership/Planning

During the course of this project I led scrums as well as retros and made sure that everyone was on the route to success. I created several issues and was able to manage the deployment of Render which was our main backend deployment method. I also led outside meetings on zoom and was able to make sure that the team was working without any issues.

## Coding Contributions

### Database and Efficiency

- Architected the initial SQL and Postgres schemas and successfully implemented a working Python-to-Postgres connection.
- Managed the complexity of database connections across both local development and production environments on Render.
- Improved application speed by decreasing overall data payloads and implementing conditional checks to streamline data delivery at much quicker speeds.

### Real-time data

I developed websocket integration as well as logic behind the integration of the player props

- Implemented WebSocket subscriptions to provide users with live game detail updates without needing to refresh.
- Developed logic to pull starting lineups and integrate them into the player props page through the ESPN API.
- Created a historical database of the previous games

### DevOps

- Setup the render deployment and render postgres database deployment

# Contributions - Kevin

Throughout the quarter I mostly worked on backend development including defining routes, instantiating polling loop for constant websocket connection flow, and training ML models for win probability prediction and stat prediction models. I integrated external API's with internal pipelines to feed necessary data into frontend, including team stats + leaders, team records, and live player prop projections. I led a scrum and participated actively in retro meetings as well.

## Coding Contributions

- Migrating from NBA API to ESPN API for improved reliability (NBA would sometimes block NAT IP address after scraping large amounts of data): https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/94

- Defining routes to get player PRA props from SportsGameOdds API: https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/171, https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/200

- Fixing endpoint for last 10 games record: https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/165

- Training models: https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/184, https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/136, https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/119

# Contributions - Logan

## Leadership/Planning

Over the course of the quarter I have held lead sprint planning and been the product ownwer. I have also been responsible creating a substantial portion of the invididual user stories, issues, and managing the kanban board. During my time as product owner and planning sprints I made sure that our work was focused on worked toward developing core features and delivering on user needs.

## Coding Contributions

Throughout the quart I worked on mutliple issues and features. Most issues were backend related with a frontend changes. They include:

- Implement API endpoints and routes. PRs: [71](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/71) [84](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/84/changes) [154](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/154)
- Add backend documentation. PRs: [117](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/117) [143](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/143)
- Creating training Dataset scripts. PR: [117](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/117)
- Redesigned Web Socket to support multiple subjects. PR: [143](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/143)
- Adding e2e test to the frontend. PR: [164](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/164)
- Designed a data pipeline for live playerprop predicition. PR:[208](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/208)
- UI Hardening [223](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/223)
- Small bug fixes. PRs: [48](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/48) [100](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/100) [115](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/100) [149](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/149)

## User Flows

Many of the backend changes I made are meant to support major user flows. The backend endpoints that I created were the fountation for both the live games and standings on the main games dashboard. Redesigning the websocket also allows users to get live game updates on the games dashboard, individual games page, and pplayer props page. Lastly, my work in creating data piplines and scripts allowed us to train and use our ML models for actual user features such as the live game probabilites and player props. This included an entire end to end pipeline that took live game, projected their players PRA, and rendered them on the frontend.

# Contributions - Raymond

Throughout the quarter my primary focus was backend development for the application. I worked on building and improving the backend infrastructure that powers the live game dashboard and player props features. This included developing API endpoints, implementing real-time data streaming using WebSockets, designing database structures, and integrating external sports data sources. A lot of work was also done on pair programming issues with other members. 
## Coding Contributions

Throughout the quart I worked on mutliple issues and features. Most issues were backend related with some frontend changes. They include:
- Refactor Starting Lineup Endpoint to Support ESPN PR: [170](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/127)
- Implement per-game WebSocket broadcaster for detailed game stats PR: [142](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/161)
- Integrate real win probability into live game updates PR: [110](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/168)
- Add backend endpoint to return stats for a specific game PR: [102](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/122)
- Create script to clean data for pydantic schema PR: [79](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/85)
- Refactor /api/games backend route  PR: [114](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/127)
- Create basic database schema  PR: [63](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/76)
- Setup FastAPI app  PR: [56](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/67)
- Add player images to props  PR: [82](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/199)
- Create player props endpoint + web sockets PR: [194](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/198)
- Added help/info page PR: [212 and 214](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/212)
- Added advance props search PR: [205](https://github.com/ucsb-cs148-w26/pj09-sports-betting/pull/205)

# Contributions - Tim

I contributed primarily to frontend development and real-time data integration for the sports probability application. My work focused on implementing live game updates, probability visualization, and UI components for displaying game and player data. Throughout the quarter I lead a retro and some scrum meetings as scribe. 

## Feature Development
- Implemented **real-time NBA game updates using WebSockets** in the frontend, enabling the client to receive live game data from the backend.  
  PRs: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/60

- Created a **win probability graph for live games** to visualize probability changes throughout the game.  
  PRs: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/68

- Optimized **game statistics loading on the game page** to improve performance and reduce load time.  
  PRs: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/159

- Implemented **GameCard UI components and wired live game data into the interface** so updates appear in real time.

- Implemented **player props UI components and rendered them on the props page**.  
  PRs: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/113

- Fixed **game fetching in the production environment**, updating frontend API endpoints to correctly retrieve deployed backend data.  
  PRs: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/116

# Contributions - Ali
## Leadership 
The majority of my leadership roles were in running scrum meetings. I lead a few standups to ensure everyone was on pace and everyone was able to work together. I also took the lead on unit testing for one of the labs. 

## Code contributions
Through this project, I worked a lot on the app's frontend. I designed and drew up page mockups for other team members to use and reference, and I worked a lot on major UI changes through the app's lifecycle. I also worked briefly on the backend API, helping debug routes and expanding functionality

Issues include:
- Page Creation/Formatting: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/59 https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/104 https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/192
- Assorted Frontend Feature Addition: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/178 https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/156 https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/132
- UI updates + Image Integrations: https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/176 https://github.com/ucsb-cs148-w26/pj09-sports-betting/issues/90
