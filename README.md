# EZ-Blackjack-Solver
A simple program for determining optimal blackjack strategy in real time. The vast majority of this code is AI-generated based on my input prompts and testing/corrections.

The goal of this project is to replace the need to use blackjack hand charts for determining optimal strategy by essentially baking them into a program. There is no advanced logic or card-counting going on - it simply takes inputs for both player and dealer cards and returns the optimal strategy. If necessary, strategy updates in real time as additional cards are dealt. The program is intended for single-hand play, but supports up to four total simultaneous hands as the result of splits.

# Why is this useful?

At the time of this program's creation, we are in an online casino boom. Many casinos offer promotional deals that grant players bonus funds upon deposit with the caveat that those bonus funds must be "played through". This has generated a niche group of players who are not interested in gambling but are instead interested in exploiting the casino bonus offers by playing high return-to-player games. Blackjack is one such game.

This program is designed to allow any player to utilize optimal basic blackjack strategy (no counting) with zero experience, study, or chart usage. Following the strategy recommended by this program will allow a player to approach 99% expected ROI over a large enough sample size.
