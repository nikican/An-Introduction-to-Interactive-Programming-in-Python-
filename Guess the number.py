# "Guess the number" mini-project
# input will come from buttons and an input field
# all output for the game will be printed in the console

import simplegui
import random

# initialize global variables used in your code
secret_number = 0
stop = 100
remaining_guesses = 7


def start_game(stop):
    global secret_number, remaining_guesses
    if stop == 100:
        remaining_guesses = 7
    else:
        remaining_guesses = 10
    secret_number = random.randrange(0, stop)
    print "New game! Range is from 0 to " + str(stop)
    print "Number of remaining guesses is " + str(remaining_guesses) + "\n"
# define event handlers for control panel
    
def range100():
    # button that changes range to range [0,100) and restarts
    global stop, remaining_guesses
    stop = 100
    remaining_guesses = 7
    start_game(stop)
    
def range1000():
    # button that changes range to range [0,1000) and restarts
    global stop, remaining_guesses
    stop = 1000
    remaining_guesses = 10
    start_game(stop)
    
def get_input(guess):
    # main game logic goes here
    global remaining_guesses
    print "Guess was " + guess
    remaining_guesses = remaining_guesses - 1
    print "Number of remaining guesses is " + str(remaining_guesses)
    player_number = int(guess)
    if player_number < secret_number:
        print "Higher!\n"
        if remaining_guesses == 0:
            print "You lose. It was " + str(secret_number) + ".\n"
            start_game(stop)
    elif player_number > secret_number:
        print "Lower!\n"
        if remaining_guesses == 0:
            print "You lose. It was " + str(secret_number) + ".\n"
            start_game(stop)
    else:
        print "Correct!\n"
        start_game(stop)
    
    
# create frame
frame = simplegui.create_frame("Guess the number!", 200, 200)


# register event handlers for control elements
guess = frame.add_input("Enter your guess", get_input, 50)
frame.add_button("Range is [0, 100)", range100, 200)
frame.add_button("Range is [0, 1000)", range1000, 200)
# start frame

frame.start()
start_game(stop)
# always remember to check your completed program against the grading rubric
