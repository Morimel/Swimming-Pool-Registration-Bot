from playwright.sync_api import sync_playwright, expect
from datetime import date
import os, re, sys, time, random
from dotenv import load_dotenv

load_dotenv()

URL        = os.environ["FORM_URL"]           
EMAIL      = os.environ["EMAIL"]
NAME       = os.environ["FULL_NAME"]
SID        = os.environ["STUDENT_ID"]
PHONE      = os.environ["PHONE"]
GROUP_NAME = os.environ["GROUP_NAME"]

# --- human-like delays / typing ---
def hsleep(a=0.25, b=0.8):
    time.sleep(random.uniform(a, b))

def human_type(locator, text, min_d=0.03, max_d=0.12):
    locator.click()
    locator.fill("")
    for ch in text:
        locator.type(ch, delay=int(random.uniform(min_d*1000, max_d*1000)))

def click_next(page):
    for text in ("Далее", "Next"):
        btn = page.get_by_role("button", name=text)
        if btn.count():
            btn.click()
            return
    page.locator('div[role="button"]', has_text="Next").first.click()

def choose_radio(page, label: str):
    selector = f'div[role="radio"][aria-label="{label}"]'
    rb = page.locator(selector).first
    rb.scroll_into_view_if_needed()
    try:
        rb.check(timeout=1500)
    except Exception:
        pass
    if (rb.get_attribute("aria-checked") or "false") != "true":
        rb.click(force=True)
        page.wait_for_timeout(120)
    if (rb.get_attribute("aria-checked") or "false") != "true":
        rb.focus()
        rb.press(" ")
        expect(rb).to_have_attribute("aria-checked", "true", timeout=2500)

def check_slot(page, label: str):
    cb = page.locator(f'div[role="checkbox"][aria-label="{label}"]').first
    cb.scroll_into_view_if_needed()
    cb.click()
    try:
        expect(cb).to_have_attribute("aria-checked", "true", timeout=2500)
    except Exception:
        cb.focus()
        cb.press(" ")
        expect(cb).to_have_attribute("aria-checked", "true", timeout=2500)

HEADLESS = os.getenv("HEADLESS", "0") == "1"   # windowed by default locally; set HEADLESS=1 for cron
DRY_RUN  = os.getenv("DRY_RUN", "0") == "1"    # fill the form but don't click Submit
SUBMIT_TIMEOUT = int(os.getenv("SUBMIT_TIMEOUT", "300"))  # seconds for CAPTCHA + confirmation

with sync_playwright() as p:
    browser = p.chromium.launch(headless=HEADLESS, slow_mo=220)
    storage = "state.json" if (os.path.exists("state.json") and os.path.getsize("state.json") > 0) else None
    ctx = browser.new_context(
        storage_state=storage,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1320, "height": 900},
        locale="en-US",
        timezone_id="Asia/Kuala_Lumpur",
    )
    page = ctx.new_page()

    try:
        page.goto(URL, wait_until="domcontentloaded")
        page.wait_for_load_state("networkidle")
        hsleep(0.6, 1.3)

        # ---------- Page 1 ----------
        # EMAIL
        email = page.locator('input[type="email"]').first
        if email.count():
            human_type(email, EMAIL)
        else:
            page.get_by_role("textbox", name=re.compile("email|электрон|почт", re.I)).first.fill(EMAIL)
        hsleep()

        # DATE
        date_input = None
        for lbl in ("Booking date", "Дата", "Booking Date"):
            cont = page.get_by_label(lbl, exact=False)
            if cont.count():
                cand = cont.locator("input").first
                if cand.count():
                    date_input = cand
                    break
        if not date_input:
            for sel in ('input[type="date"]', 'input[aria-label*="Booking"]', 'input[aria-label*="Дата"]'):
                q = page.locator(sel).first
                if q.count():
                    date_input = q
                    break

        if date_input:
            today_dot = date.today().strftime("%d.%m.%Y")
            today_iso = date.today().strftime("%Y-%m-%d")
            date_input.click()
            date_input.press("Home"); date_input.press("ControlOrMeta+a")
            human_type(date_input, today_dot)
            date_input.blur()
            if page.locator("text=/Invalid date/i").is_visible(timeout=500):
                try:
                    date_input.fill(today_iso); date_input.blur()
                except:
                    pass
                if page.locator("text=/Invalid date/i").is_visible(timeout=500):
                    date_input.evaluate(
                        "(el, v) => { el.value=v; el.dispatchEvent(new Event('input',{bubbles:true})); el.dispatchEvent(new Event('change',{bubbles:true})); }",
                        today_dot
                    )
        hsleep()

        # TIME slots
        for time_slot in (
            "5.00 PM to 6.00 PM",
            "6.00 PM to 7.00 PM",
            "7.00 PM to 8.00 PM",
            "8.00 PM to 9.00 PM",
            "9.00 PM to 10.00 PM",
        ):
            check_slot(page, time_slot); hsleep(0.15, 0.35)

        # FACILITIES -> Swimming Pool
        combo = page.locator('div[role="listbox"]').last
        combo.scroll_into_view_if_needed()
        try:
            combo.click(timeout=3000)
        except:
            combo.focus(); combo.press(" "); combo.press("ArrowDown")
        opt = page.get_by_role("option", name=re.compile("Swimming Pool", re.I)).first
        opt.scroll_into_view_if_needed(); opt.click()
        hsleep(0.4, 0.9)

        click_next(page); hsleep(0.6, 1.3)

        # ---------- Page 2 ----------
        page.get_by_label("Full Name", exact=False).fill(NAME); hsleep(0.2, 0.5)
        page.get_by_label("Student / Staff ID", exact=False).fill(SID); hsleep(0.2, 0.5)
        page.get_by_label("Contact Number", exact=False).fill(PHONE); hsleep(0.3, 0.6)
        click_next(page); hsleep(0.6, 1.3)

        # ---------- Page 3 ----------
        fld = (
            page.get_by_role("textbox", name=re.compile("Student Name & ID", re.I))
            .filter(has_not=page.locator('[aria-disabled="true"]'))
            .nth(0)
        )
        fld.scroll_into_view_if_needed(); fld.click(); fld.fill(GROUP_NAME); hsleep(0.2, 0.6)
        choose_radio(page, "Agree"); hsleep(0.3, 0.7)
        click_next(page); hsleep(0.8, 1.5)

        # ---------- Page 4 ----------
        page.get_by_text(re.compile(r"IMPORTANT NOTICE", re.I)).first.wait_for(timeout=10000)
        radios = page.get_by_role("radio", name=re.compile(r"\bagree\b", re.I))
        for i in range(radios.count()):
            rb = radios.nth(i)
            rb.scroll_into_view_if_needed()
            try:
                rb.click(timeout=2000)
            except:
                rb.focus(); rb.press(" ")
            expect(rb).to_have_attribute("aria-checked", "true", timeout=2500)
            hsleep(0.25, 0.6)

        # anti-trigger: if a CAPTCHA shows up before submitting, don't submit
        if page.locator('iframe[title*="captcha" i], div:has-text("I\'m not a robot")').first.is_visible(timeout=500):
            page.screenshot(path="captcha_detected.png")
            print("⚠️ CAPTCHA detected, aborting submit.")
            raise SystemExit(2)

        if DRY_RUN:
            page.screenshot(path="dry_run.png", full_page=True)
            print("DRY_RUN: form filled, submit skipped (see dry_run.png)")
            raise SystemExit(0)

        # Submit
        submit = page.get_by_role("button", name=re.compile(r"(submit|отправить)", re.I)).first
        submit.scroll_into_view_if_needed(); hsleep(0.3, 0.7); submit.click()

        # wait for confirmation; if Google shows a CAPTCHA, a human solves it in the browser window
        challenge = page.locator('iframe[title*="challenge" i]')
        confirmed = page.get_by_text(re.compile(r"response has been recorded|ответ записан", re.I))
        deadline = time.time() + SUBMIT_TIMEOUT
        captcha_announced = False
        while time.time() < deadline:
            if "formResponse" in page.url or confirmed.first.is_visible():
                break
            if challenge.first.is_visible() and not captcha_announced:
                captcha_announced = True
                if HEADLESS:
                    page.screenshot(path="captcha_detected.png")
                    print("⚠️ CAPTCHA appeared. Re-run with HEADLESS=0 ./run_form.sh and solve it in the window.")
                    raise SystemExit(2)
                print(f"🧩 CAPTCHA appeared — solve it in the browser window (waiting up to {SUBMIT_TIMEOUT}s)...", flush=True)
            page.wait_for_timeout(1000)
        else:
            raise TimeoutError(f"no confirmation page within {SUBMIT_TIMEOUT}s after Submit")

        page.screenshot(path="submitted.png")
        print(f"✅ Submitted booking for {date.today():%d.%m.%Y} (see submitted.png)")
    except SystemExit:
        raise
    except Exception as e:
        page.screenshot(path="error.png", full_page=True)
        print(f"❌ NOT submitted. Failed at {page.url}: {e!r} (see error.png)")
        raise SystemExit(1)
    finally:
        if not HEADLESS and sys.stdin.isatty():
            input("Press Enter to close the browser... ")
        browser.close()
