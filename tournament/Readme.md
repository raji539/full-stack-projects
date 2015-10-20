System Requirements:
-Have python version 2.7 installed.
-Vagrant
-VirtualBox


How to Run:
-Launch the Vagrant VM
-Connect to psql and create the required table with the command \i tournament.sql
-exit psql and execute the the test in python with the command python tournamant_test.py


Files Includes With This Project:
-tournament.py
-tournament_test.py
-tournament.sql


Enhancements added:
-Support for multiple tournaments.
-Bye support for odd number of players.

Enhancements docket:
- Prevent rematches between players
- Support ties in matches.
- When two players have the same number of wins, rank them according to OMW