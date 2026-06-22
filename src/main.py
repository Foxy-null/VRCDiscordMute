import logging
import time
import ctypes
import keyboard
from tinyoscquery.query import OSCQueryBrowser, OSCQueryClient
from psutil import process_iter
import os
import sys
import configparser
import openvr
from typing import List, NamedTuple

AVATAR_CHANGE_PARAMETER = "/avatar/change"
PARAMETER_PREFIX = "/avatar/parameters/"
MUTESELF_PARAMETER = PARAMETER_PREFIX + "MuteSelf"
DISABLE_PARAMETER = PARAMETER_PREFIX + "DisableDiscordMute"

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")


KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
INPUT_KEYBOARD = 1
ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong


class KeyStroke(NamedTuple):
    scan_code: int
    extended: bool = False


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_ushort),
        ("wParamH", ctypes.c_ushort),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("union", INPUT_UNION),
    ]


SCAN_CODES = {
    "escape": KeyStroke(0x01),
    "esc": KeyStroke(0x01),
    "1": KeyStroke(0x02),
    "2": KeyStroke(0x03),
    "3": KeyStroke(0x04),
    "4": KeyStroke(0x05),
    "5": KeyStroke(0x06),
    "6": KeyStroke(0x07),
    "7": KeyStroke(0x08),
    "8": KeyStroke(0x09),
    "9": KeyStroke(0x0A),
    "0": KeyStroke(0x0B),
    "-": KeyStroke(0x0C),
    "minus": KeyStroke(0x0C),
    "=": KeyStroke(0x0D),
    "equals": KeyStroke(0x0D),
    "backspace": KeyStroke(0x0E),
    "tab": KeyStroke(0x0F),
    "q": KeyStroke(0x10),
    "w": KeyStroke(0x11),
    "e": KeyStroke(0x12),
    "r": KeyStroke(0x13),
    "t": KeyStroke(0x14),
    "y": KeyStroke(0x15),
    "u": KeyStroke(0x16),
    "i": KeyStroke(0x17),
    "o": KeyStroke(0x18),
    "p": KeyStroke(0x19),
    "[": KeyStroke(0x1A),
    "left bracket": KeyStroke(0x1A),
    "]": KeyStroke(0x1B),
    "right bracket": KeyStroke(0x1B),
    "enter": KeyStroke(0x1C),
    "return": KeyStroke(0x1C),
    "ctrl": KeyStroke(0x1D),
    "control": KeyStroke(0x1D),
    "left ctrl": KeyStroke(0x1D),
    "left control": KeyStroke(0x1D),
    "a": KeyStroke(0x1E),
    "s": KeyStroke(0x1F),
    "d": KeyStroke(0x20),
    "f": KeyStroke(0x21),
    "g": KeyStroke(0x22),
    "h": KeyStroke(0x23),
    "j": KeyStroke(0x24),
    "k": KeyStroke(0x25),
    "l": KeyStroke(0x26),
    ";": KeyStroke(0x27),
    "semicolon": KeyStroke(0x27),
    "'": KeyStroke(0x28),
    "apostrophe": KeyStroke(0x28),
    "`": KeyStroke(0x29),
    "grave": KeyStroke(0x29),
    "shift": KeyStroke(0x2A),
    "left shift": KeyStroke(0x2A),
    "\\": KeyStroke(0x2B),
    "backslash": KeyStroke(0x2B),
    "z": KeyStroke(0x2C),
    "x": KeyStroke(0x2D),
    "c": KeyStroke(0x2E),
    "v": KeyStroke(0x2F),
    "b": KeyStroke(0x30),
    "n": KeyStroke(0x31),
    "m": KeyStroke(0x32),
    ",": KeyStroke(0x33),
    "comma": KeyStroke(0x33),
    ".": KeyStroke(0x34),
    "period": KeyStroke(0x34),
    "/": KeyStroke(0x35),
    "slash": KeyStroke(0x35),
    "right shift": KeyStroke(0x36),
    "numpad *": KeyStroke(0x37),
    "num *": KeyStroke(0x37),
    "multiply": KeyStroke(0x37),
    "alt": KeyStroke(0x38),
    "left alt": KeyStroke(0x38),
    "space": KeyStroke(0x39),
    "caps lock": KeyStroke(0x3A),
    "capslock": KeyStroke(0x3A),
    "f1": KeyStroke(0x3B),
    "f2": KeyStroke(0x3C),
    "f3": KeyStroke(0x3D),
    "f4": KeyStroke(0x3E),
    "f5": KeyStroke(0x3F),
    "f6": KeyStroke(0x40),
    "f7": KeyStroke(0x41),
    "f8": KeyStroke(0x42),
    "f9": KeyStroke(0x43),
    "f10": KeyStroke(0x44),
    "pause": KeyStroke(0x45),
    "scroll lock": KeyStroke(0x46),
    "scrolllock": KeyStroke(0x46),
    "numpad 7": KeyStroke(0x47),
    "num 7": KeyStroke(0x47),
    "numpad 8": KeyStroke(0x48),
    "num 8": KeyStroke(0x48),
    "numpad 9": KeyStroke(0x49),
    "num 9": KeyStroke(0x49),
    "numpad -": KeyStroke(0x4A),
    "num -": KeyStroke(0x4A),
    "subtract": KeyStroke(0x4A),
    "numpad 4": KeyStroke(0x4B),
    "num 4": KeyStroke(0x4B),
    "numpad 5": KeyStroke(0x4C),
    "num 5": KeyStroke(0x4C),
    "numpad 6": KeyStroke(0x4D),
    "num 6": KeyStroke(0x4D),
    "numpad +": KeyStroke(0x4E),
    "num +": KeyStroke(0x4E),
    "add": KeyStroke(0x4E),
    "numpad 1": KeyStroke(0x4F),
    "num 1": KeyStroke(0x4F),
    "numpad 2": KeyStroke(0x50),
    "num 2": KeyStroke(0x50),
    "numpad 3": KeyStroke(0x51),
    "num 3": KeyStroke(0x51),
    "numpad 0": KeyStroke(0x52),
    "num 0": KeyStroke(0x52),
    "numpad .": KeyStroke(0x53),
    "num .": KeyStroke(0x53),
    "decimal": KeyStroke(0x53),
    "f11": KeyStroke(0x57),
    "f12": KeyStroke(0x58),
    "f13": KeyStroke(0x64),
    "f14": KeyStroke(0x65),
    "f15": KeyStroke(0x66),
    "f16": KeyStroke(0x67),
    "f17": KeyStroke(0x68),
    "f18": KeyStroke(0x69),
    "f19": KeyStroke(0x6A),
    "f20": KeyStroke(0x6B),
    "f21": KeyStroke(0x6C),
    "f22": KeyStroke(0x6D),
    "f23": KeyStroke(0x6E),
    "f24": KeyStroke(0x76),
    "right ctrl": KeyStroke(0x1D, True),
    "right control": KeyStroke(0x1D, True),
    "right alt": KeyStroke(0x38, True),
    "alt gr": KeyStroke(0x38, True),
    "altgr": KeyStroke(0x38, True),
    "numpad /": KeyStroke(0x35, True),
    "num /": KeyStroke(0x35, True),
    "divide": KeyStroke(0x35, True),
    "numpad enter": KeyStroke(0x1C, True),
    "num enter": KeyStroke(0x1C, True),
    "insert": KeyStroke(0x52, True),
    "ins": KeyStroke(0x52, True),
    "delete": KeyStroke(0x53, True),
    "del": KeyStroke(0x53, True),
    "home": KeyStroke(0x47, True),
    "end": KeyStroke(0x4F, True),
    "page up": KeyStroke(0x49, True),
    "pgup": KeyStroke(0x49, True),
    "page down": KeyStroke(0x51, True),
    "pgdn": KeyStroke(0x51, True),
    "up": KeyStroke(0x48, True),
    "up arrow": KeyStroke(0x48, True),
    "down": KeyStroke(0x50, True),
    "down arrow": KeyStroke(0x50, True),
    "left": KeyStroke(0x4B, True),
    "left arrow": KeyStroke(0x4B, True),
    "right": KeyStroke(0x4D, True),
    "right arrow": KeyStroke(0x4D, True),
    "num lock": KeyStroke(0x45, True),
    "numlock": KeyStroke(0x45, True),
    "print screen": KeyStroke(0x37, True),
    "printscreen": KeyStroke(0x37, True),
    "prtsc": KeyStroke(0x37, True),
    "break": KeyStroke(0x46, True),
    "windows": KeyStroke(0x5B, True),
    "win": KeyStroke(0x5B, True),
    "left windows": KeyStroke(0x5B, True),
    "left win": KeyStroke(0x5B, True),
    "right windows": KeyStroke(0x5C, True),
    "right win": KeyStroke(0x5C, True),
    "apps": KeyStroke(0x5D, True),
    "application": KeyStroke(0x5D, True),
    "context menu": KeyStroke(0x5D, True),
}


def normalize_key_name(key: str) -> str:
    return " ".join(key.lower().replace("_", " ").replace("-", " ").split())


def resolve_hotkey(hotkey: str) -> List[KeyStroke]:
    keys = [normalize_key_name(part) for part in hotkey.split("+") if part.strip()]
    if not keys:
        raise ValueError("ToggleMuteKey is empty")

    resolved = []
    for key in keys:
        try:
            resolved.append(SCAN_CODES[key])
        except KeyError as exc:
            raise ValueError(f"Unsupported key name: {key}") from exc
    return resolved


def send_key_event(key: KeyStroke, key_up: bool = False):
    flags = KEYEVENTF_SCANCODE
    if key.extended:
        flags |= KEYEVENTF_EXTENDEDKEY
    if key_up:
        flags |= KEYEVENTF_KEYUP

    key_input = KEYBDINPUT(0, key.scan_code, flags, 0, 0)
    input_event = INPUT(INPUT_KEYBOARD, INPUT_UNION(ki=key_input))
    sent = ctypes.windll.user32.SendInput(
        1, ctypes.byref(input_event), ctypes.sizeof(INPUT))
    if sent != 1:
        raise ctypes.WinError()


def resource_path(relative_path):
    """Gets absolute path from relative path"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def wait_get_oscquery_client():
    service_info = None
    logging.info("Waiting for VRChat to be discovered.")
    while service_info is None:
        browser = OSCQueryBrowser()
        time.sleep(2)  # Wait for discovery
        service_info = browser.find_service_by_name("VRChat")
    logging.info("VRChat discovered!")
    client = OSCQueryClient(service_info)
    logging.info("Waiting for VRChat to be ready.")
    while client.query_node(AVATAR_CHANGE_PARAMETER) is None:
        time.sleep(2)
    logging.info("VRChat ready!")
    return client


def is_running() -> bool:
    """Checks if VRChat is running."""
    _proc_name = "VRChat.exe" if os.name == 'nt' else "VRChat"
    return _proc_name in (p.name() for p in process_iter())


def press_key(key: str):
    """Presses a key."""
    if os.name == 'nt':
        try:
            keys = resolve_hotkey(key)
            for resolved_key in keys:
                send_key_event(resolved_key)
            time.sleep(0.05)
            for resolved_key in reversed(keys):
                send_key_event(resolved_key, key_up=True)
            return
        except ValueError as exc:
            logging.warning("%s; falling back to keyboard library", exc)

    keyboard.press(key)
    time.sleep(0.05)
    keyboard.release(key)


def main_loop():
    state = None
    last_state = None
    key = str(config["config"]["ToggleMuteKey"])
    poll_interval = float(config["config"]["PollInterval"])

    logging.info("Waiting for VRChat to start.")
    while not is_running():
        time.sleep(3)
    logging.info("VRChat started!")

    qclient = wait_get_oscquery_client()
    while not state:
        state = qclient.query_node(MUTESELF_PARAMETER)
        if state and not state.value[0]:
            logging.warn("Waiting for user to Mute...")
        else:
            logging.info("User is Muted!")
        time.sleep(1)
    last_state = state

    while is_running():
        disable = qclient.query_node(DISABLE_PARAMETER)
        if disable and disable.value[0]:
            logging.warning("Discord Mute is disabled!")
            time.sleep(3)
            continue

        state = qclient.query_node(MUTESELF_PARAMETER)
        if state and state.value[0] != last_state.value[0]:
            logging.info(
                "User is Muted!" if state.value[0] else "User is Unmuted!")
            press_key(key)
            last_state = state
        time.sleep(poll_interval)


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config_path = resource_path('config.ini')
    read_files = config.read(config_path)
    if not read_files or not config.has_section("config"):
        raise FileNotFoundError(f"Could not read config file: {config_path}")
    appmanifest_path = resource_path(config["config"]["AppManifestFile"])

    # Init openvr
    try:
        application = openvr.init(openvr.VRApplication_Utility)
        openvr.VRApplications().addApplicationManifest(appmanifest_path)
    except Exception:
        pass

    main_loop()
