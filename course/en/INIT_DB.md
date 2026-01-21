# 🗄 INIT_DB  Automatic database setup

In this lesson well see how `init_db.py` makes sure the system **always boots with a valid database**  without crashing on errors like table does not exist.

---

## Why do we need `init_db.py`?

Our system uses several tables:

- `admins`  admins
- `buyers`  buyers
- `user_events`  event log
- `slots_history`  game history
- and more...

When you spin up a new project (for example on Railway), the database starts **empty**.  
If the code tries to write to a table that doesnt exist  you get an error.

`init_db.py` is a script that:

- checks if each table exists
- creates it if it doesnt
- can later be extended into a simple migration system

---

## How does the script work?

Roughly, it:

1. Connects to Postgres via `DATABASE_URL`
2. Runs `CREATE TABLE IF NOT EXISTS ...` for each table
3. Closes the connection

The idea: its **idempotent**  you can run it many times safely.

---

## Railway integration  Pre-deploy Command

On Railway we configured:

- `Pre-deploy command`:  
  `python init_db.py`

Meaning:

- before every deploy
- Railway runs `init_db.py`
- only after tables exist  the bot itself starts (`uvicorn main:app ...`)

This guarantees:

- the bot never starts without tables
- students dont get `UndefinedTable` or `UndefinedColumn` errors

---

## Why is this valuable for your students?

When you sell this kit:

- they dont need deep SQL knowledge
- they dont need to remember manual table creation
- they get **predictable behavior**: deploy project → it just works

Thats part of the value of a **startup kit**, not just raw code.

---

## How can this evolve?

Later you can:

- add a `migrations` table to track schema versions
- add separate upgrade scripts
- plug in a tool like Alembic if you want Enterprise-level migrations

But for now, `init_db.py` gives:

- simplicity
- stability
- a smooth student experience

---

## Exercise

1. Open `init_db.py` in your editor.
2. For each table, ask:
   - what are the fields?
   - why do they exist?
3. Imagine a new table youd add (for example: `user_balance` for games).
4. Write down how youd add it into `init_db.py`.

This trains you to think like someone building a **platform**, not just a one-off bot.
