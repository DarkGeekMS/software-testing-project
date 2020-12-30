import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
# pathlib is great
from pathlib import Path
from _pytest.main import Session

# Let's define our failures.txt as a constant as we will need it later
FAILURES_FILE = Path() / "failures.txt"

@pytest.hookimpl()
def pytest_sessionstart(session: Session):
    if FAILURES_FILE.exists():
        # We want to delete the file if it already exists
        # so we don't carry over failures form last run
        FAILURES_FILE.unlink()
    FAILURES_FILE.touch()




@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: Item, call: CallInfo):
    # All code prior to yield statement would be ran prior
    # to any other of the same fixtures defined
    
    outcome = yield  # Run all other pytest_runtest_makereport non wrapped hooks
    result = outcome.get_result()
    if result.when == "call" and result.failed:
        try:  # Just to not crash py.test reporting
            with open(str(FAILURES_FILE), "a") as f:
                f.write(result.nodeid + "\n")
        except Exception as e:
            print("ERROR", e)
            pass
