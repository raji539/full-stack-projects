-- Table definitions for the tournament project.

-- drop the Tournament database if it exists.
DROP DATABASE IF EXISTS tournament;

-- Create new Tournament database
CREATE DATABASE tournament;
-- Connect to the newly created DB
\c tournament;

CREATE TABLE tournaments (
	TournamentId   serial PRIMARY KEY,
	TournamentName   text NOT NULL		  
);

CREATE TABLE players (
	PlayerId   serial PRIMARY KEY,
	PlayerName   text NOT NULL,
	TournamentId integer REFERENCES tournaments (TournamentId)		  
);

CREATE TABLE matches (
	MatchId   serial PRIMARY KEY,
	WinnerId   integer REFERENCES players (PlayerId) ON DELETE CASCADE,
	OpponentId   integer REFERENCES players (PlayerId) ON DELETE CASCADE,
	TournamentId integer REFERENCES tournaments (TournamentId)
);

CREATE VIEW player_standings AS
    SELECT players.PlayerId, 
           players.PlayerName, 
	   players.TournamentId,
           count(matches.WinnerId) AS Wins, 
              (SELECT COUNT(*) 
               FROM matches 
               WHERE players.PlayerId = matches.WinnerId
               OR players.PlayerId = matches.OpponentId) 
           AS TotalMatches 
    FROM players 
    LEFT JOIN matches ON players.PlayerId = matches.WinnerId 
    GROUP BY players.PlayerId,
	     players.TournamentId;

