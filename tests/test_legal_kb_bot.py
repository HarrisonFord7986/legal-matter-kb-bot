from legal_kb_bot import MatterIntake, decide_follow_up


def test_deadline_language_triggers_follow_up():
    intake = MatterIntake("M-104", "Acme", "When is the response due?", deadline="2026-09-15")
    assert decide_follow_up(intake, "The filing deadline is 15 September; follow up two days before.") is True


def test_without_deadline_no_follow_up():
    intake = MatterIntake("M-105", "Acme", "Send the signed document")
    assert decide_follow_up(intake, "The signed document is ready.") is False
