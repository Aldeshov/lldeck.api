class CardState:
    """
        Constants for personal Theme mode of web-site
        choices=THEME_MODES default=IDLE
    """

    STATE_IDLE = 0
    STATE_VIEWED = 1
    STATE_AGAIN = 2
    STATE_GOOD = 3

    CARD_STATES = (
        (STATE_IDLE, "Card state: IDLE (None)"),
        (STATE_VIEWED, "Card state: Viewed"),
        (STATE_AGAIN, "Card state: Again"),
        (STATE_GOOD, "Card state: Good")
    )
