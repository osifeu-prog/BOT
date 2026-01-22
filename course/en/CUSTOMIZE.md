# 🛠 Customization – making the system yours

In this lesson you'll learn how to take the ready-made system and turn it into a custom product for yourself or a client.

--- PAGE ---

## Changing texts

Where do you change texts?

- `texts/*.py` – general texts (payments, explanations)
- `buttons/menus.py` – buttons and menus
- `course/he/*.md` – Hebrew course content
- `course/en/*.md` – English course content

Principle: texts are not hard-coded deep in logic – they live in dedicated files.

--- PAGE ---

## Changing prices

The nice part: no code changes needed.

In Railway:

1. Go to Variables.
2. Update:
   - `PRICE_SH`
   - `LESSON_DB_PRICE`
   - `PEEK_COST`
   - `REFERRAL_REWARD`
3. Save.

The code reads these values from `utils/config.py`.

--- PAGE ---

## Changing the landing page

In `landing/`:

- `index.html` – structure and copy
- `style.css` – colors, fonts, spacing

You can:

- Change the copy
- Add testimonials
- Add a video
- Switch language (RTL/LTR)

--- PAGE ---

## Changing menu logic

In `buttons/menus.py`:

- Add new buttons
- Change order
- Add new menus

In `callbacks/menu.py`:

- Handle new `menu_...` values
- Connect them to new functions

--- PAGE ---

## Adding a new lesson to the course

1. Create new files:
   - `course/he/NEW_LESSON.md`
   - `course/en/NEW_LESSON.md`
2. Add them to `LESSON_FILES` in `callbacks/course.py`.
3. Add a new button in `get_course_menu` with matching `callback_data`.

This way you extend the course without breaking the system.

--- PAGE ---

## Rebranding for a client

What needs to change for a new client?

- Texts (brand name, offer, pricing)
- Landing page (logo, colors)
- Possibly parts of the course (if they want a custom course)

The core code can stay almost identical.

--- PAGE ---

## Assignment

- Pick a "fictional client".
- Adapt the texts to fit them.
- Update the landing page.
- Write down what you'd change in the course for them.

This trains you to treat the system as a flexible product.
