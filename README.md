# acro
An irc game where you create hilarious phrases based on acronyms with your friends!

**If you want to try the game, join us in #h4x @ irc.gamesurge.net**

A simple/fun irc game, where people make phrases (acronyms) with letters which the bot gives you. for example, the bot will start a round w/ an acronym, e.g. 'YEIS', and you'll come up with an acronym, e.g. *Your epidermis is showing*, and submit it privately to the game bot.

After 60 seconds, the bot will display each acronym submission anonymously, and every player can vote for other acronyms (you can't vote for your own). The creator of the acronym with the most votes wins the round! Each round win gains you 3 points, and games usually go up to 15 points, though this could be changed.

This code is a module for [Sopel](https://github.com/sopel-irc/sopel), an irc bot framework created w/ python.

Have fun and happy acro'ing!

##### Commands
| Command | Description | Example | Privileges Required |
| --- | --- | --- | --- |
| !acro | Start a new game of acro | !acro | user |
| !acroscores | Show the high scores for acro | !acroscores | user |
| !acrochangescore \<USER> \<#> | Change a users game wins | !acrochangescore rj1 5 | bot owner |
| !addacro \<ACRO> | Add a custom acro to the game | !addacro GITHUB | op |
| !delacro \<ACRO> | Delete a custom acro from the game | !delacro GITHUB | bot owner |
| !acrocustom \<#> | Change the odds that a custom acro will appear in the game | !acrocustom 10 | op |
| !acrolist | View a list of the custom acros available in the game | !acrolist | user |
| !acrolog \<USER> (parameter optional) | View a list of acros that \<USER> has submitted, without the \<USER> parameter it will show your acros | !acrolog rj1 | user |
| !acroletters \<LETTER> (parameter optional) | See the probability of letters appearing in the game | !acroletters A | user |
| !acroadjust \<LETTER> \<#> | Change the probability for a letter to appear in the game | !acroadjust A 13 | op |



