import os
import re
import time

import requests
import uiautomation as auto
from dotenv import load_dotenv

# Load secrets from a local .env file (kept out of git via .gitignore).
load_dotenv()

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ID = os.environ.get("TELEGRAM_CHAT_ID")
cert_path = r"C:\\Users\\70023796\\Desktop\\Project\\Main_Link\\RepoGit\\Additional\\_.telegram.org.crt"

if not BOT_TOKEN or not ID:
    raise SystemExit(
        "Missing TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID. "
        "Add them to a .env file next to this script."
    )

# How often (seconds) to poll the Teams taskbar badge.
POLL_INTERVAL = 2
# The new Teams app id, used to find its taskbar button.
TEAMS_APP_ID_HINT = "msteams"
# Matches the badge count exposed in the taskbar button HelpText, e.g. "1 items".
_BADGE_RE = re.compile(r"(\d+)\s+items", re.IGNORECASE)
# Buttons that only appear on an incoming-call card.
CALL_BUTTON_NAMES = ("decline call", "accept with audio", "accept with video")

def send_noti_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: 
        response = requests.post(url, data={'chat_id': ID, 'text': text}, timeout=10)
        print(f"Response status code: {response.status_code}")
        # print(f"Response content: {response.content.decode('utf-8')}")
        if response.status_code == 200:
            print("Notification sent successfully.")
        else:
            print(f"Failed to send notification. Status code: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def _find_teams_taskbar_button():
    """Return the Teams app button on the taskbar, or None if not found."""
    for win in auto.GetRootControl().GetChildren():
        if "Shell_TrayWnd" not in (win.ClassName or ""):
            continue
        for ctrl, _ in auto.WalkControl(win, maxDepth=12):
            if ctrl.ControlTypeName != "ButtonControl":
                continue
            app_id = (ctrl.AutomationId or "").lower()
            name = (ctrl.Name or "").lower()
            # The real app button carries the MSTeams app id; skip the
            # microphone / mute button which also mentions "teams".
            if TEAMS_APP_ID_HINT in app_id and "microphone" not in name:
                return ctrl
    return None


def get_unread_count():
    """Read the Teams taskbar badge count. Returns an int (0 when no badge)."""
    button = _find_teams_taskbar_button()
    if button is None:
        return None  # Teams not running / taskbar button not found.
    try:
        help_text = button.GetPropertyValue(30013) or ""  # UIA HelpText
    except Exception:
        help_text = ""
    match = _BADGE_RE.search(str(help_text))
    return int(match.group(1)) if match else 0


def _extract_caller(candidates):
    """From texts like 'Guest Ramachandra, Nagapriya is calling you', return the
    caller name ('Guest Ramachandra, Nagapriya'). Ignores the bare phrase."""
    best = ""
    for text in candidates:
        idx = text.lower().find("is calling you")
        prefix = text[:idx].strip() if idx > 0 else ""
        if len(prefix) > len(best):
            best = prefix
    return best or None


def get_incoming_call():
    """Detect an incoming Teams call card.

    Returns a tuple (is_call, caller_name). ``caller_name`` may be None if the
    card is showing but the caller name hasn't rendered yet.
    """
    for win in auto.GetRootControl().GetChildren():
        if (win.ClassName or "") != "TeamsWebView" or (win.Name or "") != "Microsoft Teams":
            continue
        is_call = False
        candidates = []
        for ctrl, _ in auto.WalkControl(win, maxDepth=30):
            name = (ctrl.Name or "").strip()
            if ctrl.ControlTypeName == "ButtonControl" and name.lower() in CALL_BUTTON_NAMES:
                is_call = True
            if "is calling you" in name.lower():
                candidates.append(name)
        if is_call:
            return True, _extract_caller(candidates)
    return False, None


def watch_teams():
    print("Watching Microsoft Teams badge + incoming calls... (Ctrl+C to stop)")
    last_count = 0
    call_active = False
    call_pending_polls = 0
    warned_missing = False

    while True:
        # --- Incoming call detection ---
        is_call, caller = get_incoming_call()
        if is_call:
            if not call_active:
                if caller:
                    print(f"Incoming Teams call from {caller}")
                    send_noti_message(f"Incoming Microsoft Teams call from {caller}")
                    call_active = True
                    call_pending_polls = 0
                else:
                    # Card is up but the name hasn't rendered; wait a few polls.
                    call_pending_polls += 1
                    if call_pending_polls >= 3:
                        print("Incoming Teams call (caller unknown)")
                        send_noti_message("Incoming Microsoft Teams call - Unknown caller")
                        call_active = True
                        call_pending_polls = 0
        else:
            call_active = False
            call_pending_polls = 0

        # --- Unread badge detection ---
        count = get_unread_count()
        if count is None:
            if not warned_missing:
                print("Teams taskbar button not found. Is Teams running and pinned?")
                warned_missing = True
            last_count = 0
            time.sleep(POLL_INTERVAL)
            continue
        warned_missing = False

        if count > last_count:
            print(f"Teams badge increased: {last_count} -> {count}")
            send_noti_message(
                f"New Microsoft Teams activity - {count} unread notification(s)."
            )
        last_count = count

        time.sleep(POLL_INTERVAL)


def main():
    try:
        watch_teams()
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == "__main__":
    main()