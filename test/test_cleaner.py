import pytest

from controllers.cleaner_controller import CleanerController

DAYS_LIMIT = 0

@pytest.fixture
def cleaner(db_context):
    yield CleanerController(db_context, DAYS_LIMIT)

def test_clean_old(cleaner, db_context):
    rows_before = db_context.count_rows()
    cleaner.clean_old()
    rows_after = db_context.count_rows()
    assert rows_before > rows_after