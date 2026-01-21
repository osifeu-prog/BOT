# 🎰 SLOTS game code – full explanation

In this lesson we'll break down the SLOTS game and understand how it works, and how you can change it.

--- PAGE ---

## Basic idea

The game:

- Picks 3 symbols (emojis)
- If all are identical – the user "wins"
- Otherwise – "loses"
- Stores the result in the DB
- Shows a message accordingly

It's simple, but demonstrates:

- Logic
- Probability
- DB usage
- User experience

--- PAGE ---

## handlers/slots.py

You'll find:

- `SYMBOLS` – list of symbols
- `play_slots` – runs a single game
- `show_leaderboard` – shows a leaderboard

`play_slots`:

1. Decides if the user wins or not (based on `WIN_CHANCE_PERCENT`).
2. Builds a list of symbols.
3. Stores the result in `slots_history`.
4. Sends a message to the user.

--- PAGE ---

## Controlling win chance

In `utils/config.py`:

- `WIN_CHANCE_PERCENT` – win probability.

Examples:

- 20 – about 20% of games are wins.
- 50 – about half.
- 5 – very rare.

This lets you control the game experience.

--- PAGE ---

## Leaderboard

In `db/slots.py`:

- `add_slots_result` – inserts a result.
- `get_leaderboard` – returns users ordered by number of games.

In `handlers/slots.py`:

- `show_leaderboard` – builds a nice text from the data.

This lets you show users who's "most active".

--- PAGE ---

## Making the game richer

Ideas:

- Add "points" per win
- Track a "balance" per user
- Let users "buy" more plays
- Add different prize types

The current code is a base – you can extend it into any game you want.

--- PAGE ---

## Assignment

- Change the symbol list.
- Change the win chance.
- Add custom text when a user wins 3 times in a row (you can add logic in the DB).

This trains you to take existing code and make it your own.
