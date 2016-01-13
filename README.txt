Swiss_Tournament Database version 1.00 10/29/2015
README

    Swiss_Tournament Database is a database for a Swiss Style tournament, where at the end of each round players play against a player that has about same number of wins as them in the next round. ----------------------------------------------------------------------------

SETUP NOTES

    Install Vagrant(http://vagrantup.com/) and VirtualBox (https://www.virtualbox.org/)
    First, fork the fullstack-nanodegree-vm repository (https://github.com/akamuri/Project_2_Swiss_Tournament)
    Launch the Vagrant VM :Use the command vagrant up (powers on the virtual machine) followed by vagrant ssh (logs into the virtual machine). Remember, once you have executed the vagrant ssh command, you will want to cd /vagrant to change directory to the synced folders in order to work on your project
    To build and access the database run psql followed by \i tournament.sql, this will create the tournament database and also create the tables.
    tournament_test.py can be used to test everthing it setup correctly.

GENERAL USAGE NOTES

    You can write you on python file to interact with the datbase.
    The following functions will be available to you:
    deleteMatches(): To delete all the matches.
    countPlayers(): To count all the players.
    registerPlayer(name): To add a player name to the Database.
    playerStandings(): Returns you a list of the currecnt player standings.
    reportMatch(winner, loser):To update the winner and loser of a match.
    swissPairings(): This returns you a list of the pairings of player for the next match.
