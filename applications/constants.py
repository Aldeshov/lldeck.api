class Theme:
    """
        Constants for personal Theme mode of web-site
        choices=THEME_MODES default=IDLE
    """

    THEME_IDLE = 0
    THEME_SYSTEM = 1
    THEME_LIGHT = 2
    THEME_DARK = 3
    THEME_HIGH_CONTRAST = 4

    THEME_MODES = (
        (THEME_IDLE, 'Theme mode: IDLE (None)'),
        (THEME_SYSTEM, 'Theme mode: System default'),
        (THEME_LIGHT, 'Theme mode: Light'),
        (THEME_DARK, 'Theme mode: Dark'),
        (THEME_HIGH_CONTRAST, 'Theme mode: High contrast'),
    )


class ProfileStatus:
    """
        Constants for personal status of profile
        choices=PROFILE_STATUSES default=IDLE
    """

    PROFILE_IDLE = 0
    PROFILE_ACTIVE = 1
    PROFILE_BUSY = 2
    PROFILE_INACTIVE = 3

    PROFILE_STATUSES = (
        (PROFILE_IDLE, 'Profile status: IDLE (None)'),
        (PROFILE_ACTIVE, 'Profile status: Active'),
        (PROFILE_BUSY, 'Profile status: Busy'),
        (PROFILE_INACTIVE, 'Profile status: Inactive'),
    )


class UserLanguage:
    """
        Constants for personal setting of language
        choices=PROFILE_LANGUAGES default=NONE
    """

    LANGUAGE_NONE = 0
    LANGUAGE_EN = 1
    LANGUAGE_RU = 2
    LANGUAGE_KZ = 3

    PROFILE_LANGUAGES = (
        (LANGUAGE_NONE, 'Profile language setting: None'),
        (LANGUAGE_EN, 'Profile language setting: English'),
        (LANGUAGE_RU, 'Profile language setting: Russian'),
        (LANGUAGE_KZ, 'Profile language setting: Kazakh'),
    )
