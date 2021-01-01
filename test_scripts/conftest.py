import csv
import re
import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
# pathlib is great
from pathlib import Path
from _pytest.main import Session
from exceptions_test import Contour


pytest_plugins = ("html", "sugar")

def pytest_addoption(parser):
    testplan = parser.getgroup('testplan')
    testplan.addoption("--testplan",
        action="store",
        default=None,
        help="generate cvs containing test metadata and exit without running test."
    )

def pytest_collection_modifyitems(session, config, items):
    path = config.getoption('testplan')
    if path:
        with open(path, mode='w', newline='') as fd:
            writer = csv.writer(fd, delimiter=',', quotechar='"',
                quoting=csv.QUOTE_MINIMAL)
            writer.writerow(["title", "description", "markers"])
            # writer.writerow(["title", "markers"])
            for item in items:
                if item.cls:
                    title = f"{item.module.__name__}.py::{item.cls.__name__}::{item.name}"
                else:
                    title = f"{item.module.__name__}.py::{item.name}"
                if item.obj.__doc__:
                    description = re.sub('\n', '\n', item.obj.__doc__.strip())
                else:
                    description = ""
                markers = ','.join([m.name for m in item.iter_markers()])

                writer.writerow([title, description, markers])
                # writer.writerow([title, markers])
        
        pytest.exit(f"Generated test plan: {path}")


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


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, int) and isinstance(right, int) and op == "==":
        return [
            "equality of 2 integers:",
            "   vals: {} != {}".format(left, right),
        ]
    elif isinstance(left, Contour) and isinstance(right, Contour) and op == "==":
        if(len(left.contour_array) != len(right.contour_array)):
            return [
                "equality of 2 contour lists",
                "Lengths: {} of contour 1 != {} of contour 2".format(len(left.contour_array), len(right.contour_array))
            ]
        else:
            return [
                "equality of 2 contour lists",
                "Contour inner values are different"
            ]
