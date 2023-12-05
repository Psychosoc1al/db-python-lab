from ctypes import POINTER, Structure
from ctypes.wintypes import DWORD, ULONG
from enum import Enum


class WINDOWCOMPOSITIONATTRIB(Enum):
    WCA_UNDEFINED = (0,)
    WCA_NCRENDERING_ENABLED = (1,)
    WCA_NCRENDERING_POLICY = (2,)
    WCA_TRANSITIONS_FORCEDISABLED = (3,)
    WCA_ALLOW_NCPAINT = (4,)
    WCA_CAPTION_BUTTON_BOUNDS = (5,)
    WCA_NONCLIENT_RTL_LAYOUT = (6,)
    WCA_FORCE_ICONIC_REPRESENTATION = (7,)
    WCA_EXTENDED_FRAME_BOUNDS = (8,)
    WCA_HAS_ICONIC_BITMAP = (9,)
    WCA_THEME_ATTRIBUTES = (10,)
    WCA_NCRENDERING_EXILED = (11,)
    WCA_NCADORNMENTINFO = (12,)
    WCA_EXCLUDED_FROM_LIVEPREVIEW = (13,)
    WCA_VIDEO_OVERLAY_ACTIVE = (14,)
    WCA_FORCE_ACTIVEWINDOW_APPEARANCE = (15,)
    WCA_DISALLOW_PEEK = (16,)
    WCA_CLOAK = (17,)
    WCA_CLOAKED = (18,)
    WCA_ACCENT_POLICY = (19,)
    WCA_FREEZE_REPRESENTATION = (20,)
    WCA_EVER_UNCLOAKED = (21,)
    WCA_VISUAL_OWNER = (22,)
    WCA_LAST = 23


# noinspection PyPep8Naming
class ACCENT_STATE(Enum):
    ACCENT_DISABLED = (0,)
    ACCENT_ENABLE_GRADIENT = (1,)
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = (3,)
    ACCENT_ENABLE_ACRYLICBLURBEHIND = (4,)
    ACCENT_INVALID_STATE = 5


# noinspection PyPep8Naming
class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState", DWORD),
        ("AccentFlags", DWORD),
        ("GradientColor", DWORD),
        ("AnimationId", DWORD),
    ]


class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", DWORD),
        ("Data", POINTER(ACCENT_POLICY)),
        ("SizeOfData", ULONG),
    ]
