"""
acro.py - make acronyms w/ your friends on irc!
Copyright 2020, rj1 <rj1@hotmail.com>
Licensed under the GPL2 license.
https://sopel.chat
"""

import sopel.module as module
import sopel.tools as tools
from sopel.formatting import color, bold, colors
import random
import time
import operator
import json

SCORE_FILE = "/home/sopel/.sopel/scores.acro"
LETTER_FILE = "/home/sopel/.sopel/letters.acro"
CUSTOM_ACRO_FILE = "/home/sopel/.sopel/custom.acro"
TEMP_CHANNEL = "#acrogame" # visit us - #acrogame @ EFNet
INSULTS = ['idiot', 'dummy', 'jerk', 'retard'] # what to call people when they don't vote

class AcroGame:
    def __init__(self, trigger):
        self.owner = trigger.nick
        self.channel = trigger.sender
        self.scores = {}
        self.currentAcro = []
        self.currentAcroString = ''
        self.submittedAcros = {}
        self.letters = []
        self.roundPlayers = []
        self.active = True
        self.gameMode = ''
        self.countAcros = 1
        self.voteCount = 0
        self.voterLog = []
        self.badRounds = 0
        self.scoreNeeded = 15

    def generateAcro(self, bot, trigger):
        self.currentAcro = []
        self.countAcros = 1
        self.submittedAcros = {}
        self.voteCount = 0

        if random.randint(0,9) == 0:
            customAcros = []
            try:
                with open(CUSTOM_ACRO_FILE, 'r') as f:
                    filecontents = f.readlines()
                    for line in filecontents:
                        current_line = line[:-1]
                        customAcros.append(current_line)
            except IOError:
                    customAcros = ['ACRO', 'GAME']
            customAcro = random.choice(customAcros).lower()
            for letter in customAcro:
                self.currentAcro.append(letter)
        else:
            with open(LETTER_FILE) as fp:
                for cnt, line in enumerate(fp):
                    letter = line.split()
                    amount = int(letter[1].strip())
                    char = letter[0].strip()
                    for _ in range(amount):
                        self.letters.append(char)

            if(random.randint(0,5)) == 0: 
                max_length = 6
            else:
                max_length = 4

            for _ in range(random.randint(3,max_length)):
                randomLetter = random.choice(self.letters)
                self.letters.remove(randomLetter)
                self.currentAcro.append(randomLetter)

        self.currentAcroString = bold(color(''.join(self.currentAcro).upper(), colors.ORANGE))
        return bot.say(f"Acro for this round: {self.currentAcroString}")

    def submitAcro(self, bot, trigger):
        if self.gameMode is not 'SUBMITTING':
            return

        submittedAcro = trigger.group(0)
        words = submittedAcro.split()

        if(len(words) != len(self.currentAcro)):
            return bot.notice(f"There's a problem with the acro you submitted, remember, the current acro is: {self.currentAcroString}")

        for word, letter in zip(words, self.currentAcro):
            if word[0].lower() != letter:
                return bot.notice(f"There's a problem with the acro you submitted, remember, the current acro is: {self.currentAcroString}")

        for username, info in self.submittedAcros.items():
            if username == trigger.sender:
                self.submittedAcros[str(trigger.sender)].update({'acro': submittedAcro})
                return bot.notice(f"Your acro for this round has been updated! {bold(submittedAcro)}")

        self.submittedAcros[str(trigger.sender)] = {}
        self.submittedAcros[str(trigger.sender)].update({'acroID': self.countAcros, 'username': str(trigger.sender), 'acro': submittedAcro})
        self.submittedAcros[str(trigger.sender)]['votes'] = []
        bot.say(f"Acro #{self.countAcros} has been submitted!", TEMP_CHANNEL)
        self.countAcros += 1
        return bot.notice(f"Your acro for this round has been recorded! {bold(submittedAcro)}")

    def displayAcros(self, bot):
        if len(self.submittedAcros) < 3:
            self.badRounds += 1
            if self.badRounds > 2:
                bot.say("We need at least 3 players to play acro. Stopping the game now.")
                self.active = False
                return False
            else:
                bot.say("We need at least 3 players to play acro. Restarting the round...")
                return False
        self.badRounds = 0
        self.voterLog = []

        bot.say(f"Ok, Acro submission time is over. Its time to VOTE:")
        for username, info in self.submittedAcros.items():
            acroID = bold(color(str(info['acroID']), colors.RED))
            acro = color(' ' + info['acro'] + ' ', colors.ORANGE, colors.BLACK)
            bot.say(f"[{acroID}] {acro}")

        time.sleep(2)

        vote_instructions = bold(color(f"/msg {bot.nick} #", colors.GREEN))
        bot.say(f"Ok, you have 30 seconds to vote for your favorite acro! Type {vote_instructions} to vote now!")

        self.gameMode = 'VOTING'
        voteEndTime = time.time() + 30
        while(self.gameMode == 'VOTING'):
            if self.voteCount == len(self.submittedAcros) or time.time() > voteEndTime:
                self.gameMode = 'NONE'
                bot.say("Voting is over!")

    def voteAcro(self, bot, trigger):
        if self.gameMode != 'VOTING':
            return
        if str(trigger.sender) not in self.submittedAcros:
            bot.notice(f"You didn't submit an acro, you can't vote!", trigger.sender)
            return
        if str(trigger.sender) in self.voterLog:
            return bot.notice(f"You already voted. Chill out!", trigger.sender)

        votedFor = int(trigger.group(0))
        for username, info in self.submittedAcros.items():
            acroID = info['acroID']
            if votedFor == acroID:
                if username == trigger.sender:
                    return bot.notice(f"You can't vote for your own acro!")
                self.submittedAcros[username]['votes'].append(str(trigger.sender))
        self.voteCount += 1
        self.voterLog.append(str(trigger.sender))
        bot.say(f"Vote #{self.voteCount} has been submitted!", TEMP_CHANNEL)
        return bot.notice(f"You have voted for acro #{votedFor}", trigger.sender)

    def addPoints(self, username, amount):
        if username not in self.scores:
            self.scores[username] = amount
        else:
            self.scores[username] += amount

    def displayVotes(self, bot):
        if self.gameMode != 'SCORING':
            return

        if self.voteCount < 1:
            bot.say(f"No votes were submitted. Stopping the game now.")
            self.active = False
            return False

        voterList = []
        highestVotes = 0
        candidates = {}
        for username, info in self.submittedAcros.items():
            acro = info['acro']
            voterList.extend(info['votes'])
            voteCount = len(info['votes'])
            if voteCount >= highestVotes:
                highestVotes = voteCount
                candidates[username] = voteCount
            voters = ' '.join(info['votes'])
            if voteCount > 0:
                bot.say(f"{color(username,colors.RED)}'s acro: {color(' ' + acro + ' ', colors.ORANGE, colors.BLACK)} got {str(voteCount)} votes from: {voters}")
            else:
                bot.say(f"{color(username,colors.RED)}'s acro: {color(' ' + acro + ' ', colors.ORANGE, colors.BLACK)} got no votes :(")

        winningScore = max(candidates.values())

        winners = []
        assholes = []
        for key in candidates:
            if candidates[key] == winningScore:
                if key in voterList:
                    winners.append(key)
                else:
                    assholes.append(key)
        
        if len(assholes) > 0 and winningScore > 0:
            for asshole in assholes:
                bot.say(bold(color(f"{asshole} should have won, but they didn't vote. Please refrain from being a {random.choice(INSULTS)} in the future, thanks.", colors.RED)))
        if len(winners) == 0:
            winString = bold(color("Nobody won any points this round. If you don't vote you don't win! VOTE!!!", colors.RED))
        elif len(winners) == 1:
            winner = winners[0]
            winString = f"{bold(winner)} had the most votes and wins 3 points this round!"
            self.addPoints(winner, 3)
            if len(self.submittedAcros[winner]['votes']) > 1:
                firstVoter = self.submittedAcros[winner]['votes'][0]
                self.addPoints(firstVoter, 1)
                bot.say(f"{bold(firstVoter)} was the first to vote for a winning acro and receives 1 bonus point!")
        else:
            for winner in winners:
                self.addPoints(winner, 3)
                winnerString = ' + '.join(winners)
                winString = bold(f"{winnerString} tied for the most votes and each win 3 points this round!")

        bot.say(winString)

        sortedScores = dict(sorted(self.scores.items(), key=operator.itemgetter(1),reverse=True))
        scoreString = bold("Scores: ")
        for user, points in sortedScores.items():
            scoreString += f"{bold(color(user, colors.BLUE))}: {color(str(points), colors.GREEN)}  "
        bot.say(scoreString.rstrip())

        winners = []
        for winner in self.scores:
            if self.scores[winner] >= self.scoreNeeded:
                winners.append(winner)

        if len(winners) != 0:
            if len(winners) > 1:
                for winner in winners:
                    self.addWin(winner)
                bot.say(bold(f"{', '.join(winners)} all have {self.scoreNeeded} or more points and tie for the win!"))
            elif len(winners) == 1:
                winner = winners.pop()
                self.addWin(winner)
                bot.say(bold(f"{winner} has won the game! ALL GLORY GOES TO YOU!!!"))

            self.active = False
            return False

    def addWin(self, winner):
        try:
            with open(SCORE_FILE, 'r') as f:
                highScores = json.load(f)
        except IOError:
                highScores = {}

        if winner not in highScores:
            highScores[winner] = 1
        else:
            highScores[winner] += 1

        with open(SCORE_FILE, 'w') as f:
            json.dump(highScores, f)

        return highScores[winner]

class AcroBot:
    def __init__(self):
        self.games = {}

    def start(self, bot, trigger):
        if trigger.sender in self.games:
            bot.say(f"We're already playing acro!")
            return
        if trigger.sender != TEMP_CHANNEL:
            bot.say(f"I don't like hosting acro games here")
            return

        bot.notice(f"New acro game started by {trigger.nick}! Have fun and good luck!", trigger.sender)
        time.sleep(1)
        self.games[trigger.sender] = AcroGame(trigger)
        game = self.games[trigger.sender]

        instructions = bold(color(f"/msg {bot.nick} <answer>", colors.GREEN))

        # game loop
        while(game.active is True):
            game.gameMode = 'SUBMITTING'
            bot.say(f"Points needed to win this game: {game.scoreNeeded}")
            bot.say(f"Submit an acro by messaging me. {instructions} is how you do it!")
            time.sleep(2)
            bot.say(f"You have 60 seconds to come up with your best acro! GO!")
            game.generateAcro(bot, trigger)
            time.sleep(45)
            bot.say(bold(color(f"HURRY THE FUCK UP! 15 SECONDS LEFT!", colors.RED)))
            time.sleep(15)
            game.gameMode = 'PREVOTE'
            if game.displayAcros(bot) == False:
                continue
            game.gameMode = 'SCORING'
            if game.displayVotes(bot) == False:
                continue
            time.sleep(8)

        del self.games[trigger.sender]

    def submitAcro(self, bot, trigger):
        if not self.games:
            return
        game = self.games[TEMP_CHANNEL] # TODO: write logic to find which channel the user is playing in
        game.submitAcro(bot, trigger)

    def voteAcro(self, bot, trigger):
        if not self.games:
            return

        game = self.games[TEMP_CHANNEL] # TODO: write logic to find which channel the user is playing in
        game.voteAcro(bot, trigger)

    def highScore(self, bot, trigger):
        try:
            with open(SCORE_FILE, 'r') as f:
                highScores = json.load(f)
        except IOError:
                highScores = {}

        sortedScores = dict(sorted(highScores.items(), key=operator.itemgetter(1),reverse=True))
        scoreString = bold("GAME WINS: ")
        for user, points in sortedScores.items():
            scoreString += f"{bold(color(user, colors.BLUE))}: {color(str(points), colors.GREEN)}  "
        bot.say(scoreString.rstrip())

    def addAcro(self, bot, trigger):
        if(len(trigger.group(2))) > 6:
            return bot.say("You can't add custom acros this long")
        if(trigger.group(2).isalpha()) == False:
            return bot.say("The custom acro you're trying to add SUCKS. Try again.")

        customAcros = []
        try:
            with open(CUSTOM_ACRO_FILE, 'r') as f:
                filecontents = f.readlines()
                for line in filecontents:
                    current_acro = line[:-1]
                    customAcros.append(current_acro)
        except IOError:
                customAcros = []

        newAcro = trigger.group(2).upper()
        if(newAcro in customAcros):
            return bot.say("This custom already is already in the game!")
        customAcros.append(newAcro)

        with open(CUSTOM_ACRO_FILE, 'w') as f:
            for listitem in customAcros:
                f.write('%s\n' % listitem)

        return bot.say(f"Your custom acro {bold(color(newAcro, colors.ORANGE))} has been added to the game!")

        

acro = AcroBot()

@module.commands('acro')
@module.example(".acro")
@module.priority('high')
@module.require_chanmsg
def acrostart(bot, trigger):
    """
    Start a game of acro in the current channel
    """
    acro.start(bot, trigger)

@module.rule("[A-Za-z,;:.-`~'!?'\"\\s]+")
@module.priority('high')
@module.require_privmsg
def submitacro(bot, trigger):
    """
    Player submitted an acro
    """
    acro.submitAcro(bot, trigger)

@module.rule("[0-9]")
@module.priority('high')
@module.require_privmsg
def voteacro(bot, trigger):
    """
    Player voted for an acro
    """
    acro.voteAcro(bot, trigger)

@module.commands('acroscores')
@module.example(".acroscores")
@module.priority('high')
@module.require_chanmsg
def acroScore(bot, trigger):
    """
    Show acro scores in channel
    """
    acro.highScore(bot, trigger)

@module.commands('addacro')
@module.example(".addacro")
@module.priority('low')
@module.require_privilege(module.OP, 'You need to be an op to add custom acros.')
@module.require_chanmsg
def addacro(bot, trigger):
    """
    Add a custom acro
    """
    acro.addAcro(bot, trigger)

