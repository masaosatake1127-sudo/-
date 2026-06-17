import pytest

from nutrition_tracker.food_database import FoodDatabase


@pytest.fixture()
def db():
    return FoodDatabase()


def test_loads_records(db):
    assert len(db.all_records) > 0


def test_search_partial_match(db):
    results = db.search("鶏")
    assert len(results) > 0
    assert all("鶏" in r.name for r in results)


def test_search_empty_query_returns_all(db):
    assert db.search("") == db.all_records


def test_search_no_match(db):
    assert db.search("存在しない食品xyz") == []


def test_find_exact(db):
    record = db.find_exact("白米(ご飯)")
    assert record is not None
    assert record.nutrition_per_100g.calories == 168


def test_find_exact_missing(db):
    assert db.find_exact("存在しない食品xyz") is None


def test_categories_non_empty(db):
    assert len(db.categories) > 0
