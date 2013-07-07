# Rock-paper-scissors-lizard-Spock

# The key idea of this program is to equate the strings
# "rock", "paper", "scissors", "lizard", "Spock" to numbers
# as follows:
#
# 0 - rock
# 1 - Spock
# 2 - paper
# 3 - lizard
# 4 - scissors
import random

# helper functions

def number_to_name(number):
    if number == 0:
        return "rock"
    elif number == 1:
        return "Spock"
    elif number == 2:
        return "paper"
    elif number == 3:
        return "lizard"
    elif number == 4:
        return "scissors"
    elif number<0 or number >5:
        return "Incorrect value"
        
    
def name_to_number(name):
     if name=="rock":
        return 0
     elif name=="Spock":
        return 1
     elif name=="paper":
        return 2
     elif name == "lizard":
        return 3
     elif name == "scissors":
        return 4
     elif name!="rock" or name!="Spock" or name!="paper" or name != "lizard" or name!= "scissors":
        return "Incorrect value"


def rpsls(name): 
    player_number = name_to_number(name);
    comp_number = random.randrange(0,5)
    mod = (comp_number-player_number) % 5
    
    print
    print "Player chooses " + name
    print "Computer chooses " + number_to_name(comp_number)
    if mod == 0:
        print "Draw!"
    elif mod == 1 or mod == 2:
        print "Computer wins!"
    else:
        print "Player wins!"

   
# test code
rpsls("rock")
rpsls("Spock")
rpsls("paper")
rpsls("lizard")
rpsls("scissors")
