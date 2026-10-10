# 🏊 Swimming Pool Registration Bot

Automatically fills in the **INTI International University Facility Reservation** Google Form to book the 🏊 **Swimming Pool** for today.

It uses [Playwright](https://playwright.dev/python/) 🎭 to open a real Chromium browser, types like a human ⌨️, and walks through all 4 pages of the form for you.

---

## ✨ What it does

| Page | Filled in automatically |
|---|---|
| 1️⃣ | 📧 Email, 📅 today's date, ⏰ time slots **5 PM → 10 PM**, 🏊 facility = Swimming Pool |
| 2️⃣ | 👤 Full name, 🪪 Student / Staff ID, 📞 contact number |
| 3️⃣ | 👥 Group member names & IDs, ✅ "Agree" |
| 4️⃣ | ✅ Agrees to the notice, rules and COVID-19 protocol, then 🚀 **Submit** |

After submitting, it waits for Google's **"Your response has been recorded"** page and tells you whether the booking worked.

---

## 📁 Project structure

```
Swimming-Pool-Registration-Bot/
├── form_book.py     🤖 the bot itself
├── run_form.sh      ▶️  launcher (logs everything to form.log)
├── save_state.py    🔐 saves your Google login to state.json
├── .env             🔒 your personal data (not committed)
├── state.json       🍪 Google cookies (not committed)
├── form.log         📜 history of every run
└── form-bot/venv/   🐍 Python virtual environment
```

---

## 🛠️ Setup (one time)

```bash
cd ~/Desktop/Swimming-Pool-Registration-Bot

# 🐍 create the virtual environment
python3 -m venv form-bot/venv

# 📦 install dependencies
./form-bot/venv/bin/pip install playwright python-dotenv

# 🌐 download the browser
./form-bot/venv/bin/python -m playwright install chromium
```

### 🔒 Create `.env`

```env
FORM_URL=https://docs.google.com/forms/d/e/.../viewform
EMAIL=you@student.newinti.edu.my
FULL_NAME=Your Full Name
STUDENT_ID=I12345678
PHONE=0123456789
GROUP_NAME=Friend Name I23456789, Another Friend I34567890
```

### 🔐 (Optional) Save your Google login

Only needed if the form ever asks you to sign in:

```bash
./form-bot/venv/bin/python save_state.py
```

Log in when the window opens, then press **Enter** in the terminal as instructed.

---

## ▶️ How to run

| 🎯 Goal | 💻 Command |
|---|---|
| 🚀 **Book for real** (browser visible, recommended) | `HEADLESS=0 ./run_form.sh` |
| 🧪 **Test only**, fill everything but don't submit | `DRY_RUN=1 ./run_form.sh` |
| 👀 Test while watching the browser | `HEADLESS=0 DRY_RUN=1 ./run_form.sh` |
| 🙈 Run without a window | `./run_form.sh` |

### ⚙️ Options

| Variable | Default | Meaning |
|---|---|---|
| `HEADLESS` | `1` | `0` = show the browser window 🪟 |
| `DRY_RUN` | `0` | `1` = don't click Submit 🧪 |
| `SUBMIT_TIMEOUT` | `300` | ⏳ seconds to wait for CAPTCHA + confirmation |

---

## 🧩 About the CAPTCHA

Google sometimes shows a "select all images with…" 🖼️ challenge after **Submit**.

- 🙋 **You solve it yourself.** The bot doesn't solve CAPTCHAs.
- ⏳ The bot waits up to **5 minutes** for you (change with `SUBMIT_TIMEOUT=600`).
- 🪟 That's why you should book with `HEADLESS=0`. In window-less mode the bot stops and asks you to rerun with the window visible.
- 🛑 The browser stays open until you press **Enter**, so you can double-check the result.

---

## ✅ Did it work?

Look at the terminal (or `tail -5 form.log`):

| Message | Meaning | Proof |
|---|---|---|
| `✅ Submitted booking for DD.MM.YYYY` | 🎉 Booking recorded! | 🖼️ `submitted.png` |
| `DRY_RUN: form filled, submit skipped` | 🧪 Test run OK, nothing submitted | 🖼️ `dry_run.png` |
| `⚠️ CAPTCHA appeared…` | 🧩 Rerun with `HEADLESS=0` | 🖼️ `captcha_detected.png` |
| `❌ NOT submitted…` | 💥 Something broke | 🖼️ `error.png` |

You'll also get a 📧 copy of your response by email from Google Forms.

---

## 🩹 Troubleshooting

- 🔑 **Asked to sign in?** Run `save_state.py` again. Google cookies expire after a while.
- 🔄 **Form changed?** If a field label or time slot was renamed, update the matching text in `form_book.py`. `error.png` shows where it got stuck.
- 📅 **Need a different date or slots?** Edit the date and `time_slot` list in `form_book.py`.
- ⏰ **Scheduling with cron?** macOS blocks background jobs from reading `~/Desktop` 🚫. Either grant `cron` **Full Disk Access** (System Settings → Privacy & Security) or move the project to e.g. `~/bots/`.

---

## ⚠️ Disclaimer

For personal use only 🙏. Please respect the university's booking rules and don't use it to block slots for other students.
