#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
# supports odd no of players added with addition of "Bye" player
# supports different tournaments, so that mathces do not have to be deleted
# between tournaments
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM matches;")
    db.commit()
    db.close()


def deletePlayers():
    """Remove all the player records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM players;")
    db.commit()
    db.close()


def deleteTournaments():
    """Remove all the tournament records from the database."""
    db = connect()
    c = db.cursor()
    c.execute("DELETE FROM tournaments;")
    db.commit()
    db.close()


def countPlayers(tournament=''):
    """Returns the number of players currently registered.
    If tournament name is passed returns the number of players
    registered for the tournament."""
    db = connect()
    c = db.cursor()
    tournament_id = ''
    if tournament and tournament.strip():
            tournament_id = getTournamentId(tournament, c)
            c.execute("SELECT COUNT(PlayerId) from players WHERE TournamentId IN  (%s)",  # noqa
                     (tournamentId))
    else:
        c.execute("SELECT COUNT(PlayerId) from players")
    count = c.fetchall()[0][0]
    return count


def registerPlayer(name, tournament=""):
    """Adds a player to the database. If a tournament name is passed,
    player data is stored with torunament information.

    The database assigns a unique serial id number for the player, 
    and the tournament if the tournament has not been entered earlier.
    (This is handled by the SQL database schema.)

    Args:
      name: the player's full name (need not be unique).
    """
    db = connect()
    c = db.cursor()
    tournament_id = ''
    if tournament and tournament.strip():
        tournament_id = getTournamentId(tournament, c)
        if not tournament_id:
            c.execute("INSERT INTO tournaments (TournamentName) VALUES (%s)",
                      (tournament,))
            tournament_id = getTournamentId(tournament, c)

    if tournament_id:
        c.execute("INSERT INTO players (PlayerName, TournamentId) VALUES (%s,%s )",  # noqa
                  (name, tournament_id))
    else:
        c.execute("INSERT INTO players (PlayerName) VALUES (%s)", (name,))
    db.commit()
    db.close()


def getTournamentId(tournament, conn):
    """ Returns the tournament id of a tournament."""
    conn.execute("SELECT TournamentId FROM tournaments WHERE TournamentName IN  (%s)",  # noqa
                 (tournament,))
    tournament_id = conn.fetchone()
    return tournamentId


def playerStandings(tournament=""):
    """Returns a list of the players and their win records, sorted by wins.
    If tournamnet name is passed will return records for that tournament only.

    The first entry in the list should be the player in first place,
    or a player tied for first place if there is currently a tie.

    If odd number of players are registered in tournament, a bye player
    is added. (Assumption made is that standings will only be requested
    after all player registerations are over)

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
        TournamentId: the id of the tournament name passed (optional based
        on if tournament name is passed or not)
    """

    db = connect()
    c = db.cursor()
    tournament_id = ''
    if tournament and tournament.strip():
            tournament_id = getTournamentId(tournament, c)
    count = countPlayers(tournament)
    if count % 2 != 0:
        if tournament_id:
            c.execute("INSERT INTO players (PlayerName, TournamentId) VALUES ('BYE',%s )",  # noqa
                      (tournamentId))
        else:
            c.execute("INSERT INTO players (PlayerName) VALUES ('BYE')")
    if tournament_id:
        c.execute("SELECT PlayerId, PlayerName, Wins, TotalMatches, TournamentId from player_standings WHERE TournamentId IN  (%s) ORDER BY Wins Desc, TotalMatches DESC, PlayerId", (tournamentId))  # noqa
    else:
        c.execute("SELECT PlayerId, PlayerName, Wins, TotalMatches from player_standings ORDER BY Wins Desc, TotalMatches DESC, PlayerId")  # noqa
    standings = c.fetchall()
    db.commit()
    db.close()
    return standings


def reportMatch(winner, loser, tournament=""):
    """Records the outcome of a single match between two players.
    Also allows reporting of match with player set as Bye player
    and ensures Bye player is not reported as winner.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    db = connect()
    c = db.cursor()
    c.execute("SELECT PlayerName FROM players where PlayerId IN (%s)",
              (winner,))
    name = c.fetchone()
    if tournament and tournament.strip():
        tournament_id = getTournamentId(tournament, c)
        if name is 'BYE':
            c.execute("INSERT INTO matches (WinnerId, OpponentId, TournamentId) VALUES (%s, %s, %s)",  # noqa 
                     (loser, winner, tournament_id))
        else:
            c.execute("INSERT INTO matches (WinnerId, OpponentId, TournamentId) VALUES (%s, %s %s)",  # noqa
                     (winner, loser, tournament_id))
    else:
        if name is 'BYE':
            c.execute("INSERT INTO matches (WinnerId, OpponentId) VALUES (%s, %s)",  # noqa
                      (loser, winner))
        else:
            c.execute("INSERT INTO matches (WinnerId, OpponentId) VALUES (%s, %s)",  # noqa
                      (winner, loser))
    db.commit()
    db.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    player_standings = playerStandings()
    swiss_pairs = []
    while len(player_standings) > 1:
        winner = player_standings.pop(0)
        opponent = player_standings.pop(0)
        swiss_pair = (winner[0], winner[1], opponent[0], opponent[1])
        swiss_pairs.append(swiss_pair)
    return swiss_pairs


def reportTournaments():
    db = connect()
    c = db.cursor()
    c.execute("SELECT * FROM tournaments")
    tournament_list = c.fetchall()
    return tournament_list
