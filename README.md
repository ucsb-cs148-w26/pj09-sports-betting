# Sports Betting

## Description

Our app is designed to provide live win probability modeling and player performance projections for daily NBA Matchups. The system ingests live NBA game data and runs predictive models to broadcast live odds updates to all users in real time. Anyone from sports bettors to casual fans are able to perform pre-game analysis and monitor probabilities throughout each game. This design is meant to provide a clear and interactive view of probabilities and statistics in one clean dashboard.

Access the website at https://pj09-sports-betting.vercel.app/

## Audience

Our ideal users are casual NBA fans and sports bettors who want a real-time view of matchup odds and player performance projections.

## Tech Stack

This project employs frontend with Next.js due to its ease of use and compatibility with common backend services, routing, and Vercel for deployment. For our backend, we decided to use FastAPI because of its built-in support for WebSockets, which would allow real-time retrieval of game state updates to update live probabilities.

#### Frontend

- Next.js (React, TypeScript)
- Tailwind CSS

#### Backend

- FastAPI (Python)

#### Data & Modeling

- Pandas + NumPy
- scikit-learn

#### Database

- PostgreSQL
- Redis

### User Roles

#### NBA Fans and Sports Bettors

The first user role that we are targeting are NBA fans who are actively watching games in real time and want to have another layer of information that they are able to access during the games. This information would consist of live probabilities as well as player performance and projections. More specifically, these users would mainly be focused on viewing live NBA games and matchups, player performance projects for each game, and real-time win probabilities for the games as well.

The next user role would be sports bettors. They would have a similar role to your average NBA fan but would be more inclined to focusing on the player projects and the real-time win projections of the games. This would help them make a better informed decision for their bets. This platform helps users accomplish their goals by ingesting live NBA game data, running predictive models to broadcast live odds updates to all users in real time all in on dashboard. This allows users to stay up to date and informed throughout the game for all their needs.

## Group Members

| Name           | GitHub ID       |
| -------------- | --------------- |
| Logan Melgoza  | @logan-melgoza  |
| Raymond Xie    | @POWERTRICEPS   |
| Ali Shahid     | @Mala-Patke     |
| Kevin Yang     | @lem0000ns      |
| Timothy Nguyen | @timmywin       |
| Alvin Chan     | @alvinlovescode |
| Junhyung Yoon  | @Neamal         |
| Jay Yeung      | @JayYeung5      |
