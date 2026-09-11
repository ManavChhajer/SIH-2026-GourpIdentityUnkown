from fixtures import pick_fixture, FIXTURES


def test_pick_fixture_is_deterministic():
    result_a = pick_fixture("khata_page_03.jpg")
    result_b = pick_fixture("khata_page_03.jpg")
    assert result_a == result_b


def test_pick_fixture_returns_one_of_known_fixtures():
    result = pick_fixture("any_name.png")
    assert result in FIXTURES


def test_pick_fixture_sets_review_required_when_low_confidence():
    for fixture in FIXTURES:
        min_conf = min(f["confidence"] for f in fixture["fields"])
        expected = min_conf < 0.7
        assert fixture["review_required"] == expected
