# captseemab-inventory-notifications (packaging workspace)

This folder is an isolated packaging workspace for the `inventory_notifications` library.
It is intended to be used to build and publish the package independently from the main backend repo.

Install (after publishing):

    pip install captseemab-inventory-notifications

Local test & build
------------------

Create a venv and install test dependencies:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install -r requirements-dev.txt

Run tests:

    pytest -q

Build package:

    python -m build

Upload to TestPyPI:

    python -m twine upload --repository testpypi dist/* -u __token__ -p <TEST_PYPI_TOKEN>
# InventoryNotificationPackage
