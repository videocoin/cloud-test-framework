# VideoCoin API Test Framework
The videocoin-api-test-framework exercises the various endpoints (used internally and externally) the VideoCoin cloud uses.

## Environment

### Python
python3.7 is currently being used for the development of this test framework

### Live Planet backend cluster
All tests use the sandbox (snb) environment of the Live Planet cloud. The domain for these endpoints are hosted on https://studio.snb.videocoin.network. Please verify any accounts being used for these tests are created on the staging environment

### Default email / VideoCoin account
The default email and VideoCoin account are associated with the email kgoautomation@gmail.com. The password to this email is LivePlanet16!. Obviously, don't use this email (or any other test email described in the variable of the tests) for confidential purposes. These emails are purely for testing and should only have VideoCoin related information constrained to the snb environment in them.

## Set-up

### Create virtualenv
`virtualenv -p python3 venv`

### Install dependencies
`pip install -r req.txt`

### Install pre-commit tool for linting and formatting (optional)
`pre-commit install`

pre-commit hooks use `black` and `flake8`. Read more about them here:

Black: https://github.com/psf/black

- This project conciously ignores Black's preference to double-quote usage (see more in the `pyproject.toml` configuration file for Black)

flake8: https://github.com/PyCQA/flake8

- This project needs to describe some errors flake8 can ignore to be used in conjunction with Black (see more in the `.flake8` configuration file for flake8)

## Running tests

### Run all tests
Run all tests with `pytest` from the root directory of this project
