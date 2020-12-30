import csv
import pytest
import re

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