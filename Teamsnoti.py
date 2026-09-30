import logging
import os
import re
import time

import requests
import uiautomation as auto
from dotenv import load_dotenv


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_PATH = os.path.join(SCRIPT_DIR, "Teamsnoti_error.log")

# Load secrets from a local .env file.
load_dotenv(os.path.join(SCRIPT_DIR, ".env"))

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Currently unused. Keep this only if your network requires a custom
# certificate for Telegram.
cert_path = (
    r"C:\Users\70023796\Desktop\Project\Main_Link\RepoGit"
    r"\Additional\_.telegram.org.crt"
)

if not BOT_TOKEN or not CHAT_ID:
    raise SystemExit(
        "Missing TELEGRAM_BOT_TOKEN and/or TELEGRAM_CHAT_ID. "
        "Add them to a .env file next to this script."
    )

# How often, in seconds, to poll Teams.
POLL_INTERVAL = 2

# The new Teams app ID, used to identify its taskbar button.
TEAMS_APP_ID_HINT = "msteams"

# Matches badge text such as "1 items".
_BADGE_RE = re.compile(r"(\d+)\s+items", re.IGNORECASE)

# Buttons that appear on an incoming-call card.
CALL_BUTTON_NAMES = (
    "decline call",
    "accept with audio",
    "accept with video",
)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Telegram notifications
# ---------------------------------------------------------------------------

def send_noti_message(text):
    """Send a Telegram notification without stopping the watcher on failure."""

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    try:
        response = requests.post(
            url,
            data={
                "chat_id": CHAT_ID,
                "text": text,
            },
            timeout=10,
        )

        print(f"Response status code: {response.status_code}")

        if response.status_code == 200:
            print("Notification sent successfully.")
            logger.info("Telegram notification sent: %s", text)
        else:
            print(
                "Failed to send notification. "
                f"Status code: {response.status_code}"
            )

            logger.error(
                "Telegram notification failed. "
                "Status code: %s, response: %s",
                response.status_code,
                response.text,
            )

    except requests.RequestException:
        print(
            "Telegram request failed. "
            f"See log for details: {LOG_PATH}"
        )
        logger.exception("Telegram request failed")

    except Exception:
        print(
            "Unexpected error while sending Telegram notification. "
            f"See log for details: {LOG_PATH}"
        )
        logger.exception("Unexpected Telegram notification error")


# ---------------------------------------------------------------------------
# Teams taskbar badge detection
# ---------------------------------------------------------------------------

def _find_teams_taskbar_button():
    """Return the Teams taskbar button, or None when it cannot be found.

    Windows UI Automation controls can become stale while the taskbar is
    updating. Property reads are therefore protected individually.
    """

    try:
        root = auto.GetRootControl()
        windows = root.GetChildren()

    except Exception:
        logger.exception("Unable to enumerate desktop controls")
        return None

    for win in windows:
        try:
            class_name = win.ClassName or ""

        except Exception:
            # The element may have disappeared between enumeration and access.
            logger.debug(
                "Skipped a stale desktop UI Automation element",
                exc_info=True,
            )
            continue

        if "Shell_TrayWnd" not in class_name:
            continue

        try:
            for ctrl, _ in auto.WalkControl(win, maxDepth=12):
                try:
                    control_type = ctrl.ControlTypeName or ""

                    if control_type != "ButtonControl":
                        continue

                    app_id = (ctrl.AutomationId or "").lower()
                    name = (ctrl.Name or "").lower()

                    # The real Teams taskbar button contains the MSTeams app ID.
                    # Exclude the Teams microphone/mute taskbar control.
                    if (
                        TEAMS_APP_ID_HINT in app_id
                        and "microphone" not in name
                    ):
                        return ctrl

                except Exception:
                    # A child control may become stale while being inspected.
                    logger.debug(
                        "Skipped a stale taskbar control",
                        exc_info=True,
                    )
                    continue

        except Exception:
            # Walking the taskbar hierarchy itself can occasionally fail.
            logger.exception(
                "Temporary failure while walking taskbar controls"
            )
            continue

    return None


def get_unread_count():
    """Read the Teams taskbar badge count.

    Returns:
        int: The current unread count. Zero means there is no badge.
        None: The Teams button could not be found or read during this poll.
    """

    try:
        button = _find_teams_taskbar_button()

        if button is None:
            return None

        # UI Automation property 30013 is HelpText.
        help_text = button.GetPropertyValue(30013) or ""
        match = _BADGE_RE.search(str(help_text))

        return int(match.group(1)) if match else 0

    except Exception:
        # The taskbar button can become stale after being found but before
        # GetPropertyValue is called.
        logger.exception("Temporary error while reading Teams badge")
        return None


# ---------------------------------------------------------------------------
# Teams incoming-call detection
# ---------------------------------------------------------------------------

def _extract_caller(candidates):
    """Extract the caller from text such as:

    'Guest Ramachandra, Nagapriya is calling you'

    Returns:
        The caller name, or None when no name can be extracted.
    """

    best = ""

    for text in candidates:
        try:
            idx = text.lower().find("is calling you")
            prefix = text[:idx].strip() if idx > 0 else ""

            if len(prefix) > len(best):
                best = prefix

        except Exception:
            logger.debug(
                "Unable to process incoming-call candidate text",
                exc_info=True,
            )

    return best or None


def get_incoming_call():
    """Detect an incoming Teams call card.

    Returns:
        tuple[bool, str | None\]:
            is_call indicates whether a call card was detected.
            caller_name may be None if the name has not rendered yet.
    """

    try:
        root = auto.GetRootControl()
        windows = root.GetChildren()

    except Exception:
        logger.exception(
            "Unable to enumerate desktop controls for call detection"
        )
        return False, None

    for win in windows:
        try:
            class_name = win.ClassName or ""
            window_name = win.Name or ""

        except Exception:
            # The top-level control may have disappeared.
            logger.debug(
                "Skipped stale top-level control during call detection",
                exc_info=True,
            )
            continue

        if (
            class_name != "TeamsWebView"
            or window_name != "Microsoft Teams"
        ):
            continue

        is_call = False
        candidates = []

        try:
            for ctrl, _ in auto.WalkControl(win, maxDepth=30):
                try:
                    control_type = ctrl.ControlTypeName or ""
                    name = (ctrl.Name or "").strip()
                    name_lower = name.lower()

                    if (
                        control_type == "ButtonControl"
                        and name_lower in CALL_BUTTON_NAMES
                    ):
                        is_call = True

                    if "is calling you" in name_lower:
                        candidates.append(name)

                except Exception:
                    # Teams may redraw the call card during enumeration.
                    logger.debug(
                        "Skipped a stale Teams call-card control",
                        exc_info=True,
                    )
                    continue

        except Exception:
            logger.exception(
                "Temporary failure while walking Teams call controls"
            )
            continue

        if is_call:
            return True, _extract_caller(candidates)

    return False, None


# ---------------------------------------------------------------------------
# Main watcher
# ---------------------------------------------------------------------------

def watch_teams():
    """Continuously monitor Teams and send Telegram notifications."""

    print("Watching Microsoft Teams badge + incoming calls...")
    print("Press Ctrl+C to stop.")
    print(f"Error log: {LOG_PATH}")

    logger.info("Teams watcher started")

    last_count = 0
    call_active = False
    call_pending_polls = 0
    warned_missing = False

    while True:
        try:
            # Incoming call detection
            is_call, caller = get_incoming_call()

            if is_call:
                if not call_active:
                    if caller:
                        message = (
                            f"Incoming Microsoft Teams call from {caller}"
                        )

                        print(message)
                        logger.info(message)
                        send_noti_message(message)

                        call_active = True
                        call_pending_polls = 0

                    else:
                        # The call card is visible, but the caller name
                        # may need a few polling cycles to render.
                        call_pending_polls += 1

                        if call_pending_polls >= 3:
                            message = (
                                "Incoming Microsoft Teams call - "
                                "Unknown caller"
                            )

                            print(message)
                            logger.info(message)
                            send_noti_message(message)

                            call_active = True
                            call_pending_polls = 0
            else:
                call_active = False
                call_pending_polls = 0

            # Unread badge detection
            count = get_unread_count()

            if count is None:
                if not warned_missing:
                    message = (
                        "Teams taskbar button temporarily unavailable. "
                        "Is Teams running and pinned?"
                    )

                    print(message)
                    logger.warning(message)
                    warned_missing = True

                # Keep the previous count to prevent duplicate notifications.
                time.sleep(POLL_INTERVAL)
                continue

            warned_missing = False

            if count > last_count:
                message = (
                    f"Teams badge increased: {last_count} -> {count}"
                )

                print(message)
                logger.info(message)

                send_noti_message(
                    "New Microsoft Teams activity - "
                    f"{count} unread notification(s)."
                )

            last_count = count

        except KeyboardInterrupt:
            # Pass Ctrl+C to main() for clean shutdown.
            raise

        except Exception:
            # Do not terminate for a temporary UI Automation failure.
            logger.exception(
                "Unexpected error during Teams polling cycle"
            )

            print(
                "Temporary polling error. The watcher will retry. "
                f"See: {LOG_PATH}"
            )

        time.sleep(POLL_INTERVAL)


def main():
    """Application entry point."""

    try:
        watch_teams()

    except KeyboardInterrupt:
        print("\nStopped.")
        logger.info("Teams watcher stopped by user")

    except Exception:
        logger.exception("Fatal unhandled application error")

        print()
        print("A fatal error stopped the Teams watcher.")
        print(f"Check the log file: {LOG_PATH}")

        input("Press Enter to close...")


if __name__ == "__main__":
    main()

                