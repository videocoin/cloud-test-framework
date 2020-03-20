# VideoCoin API Test Framework
The videocoin-api-test-framework exercises the various endpoints (used internally and externally) the VideoCoin cloud uses.

## Environment

### Python
python3.7 is currently being used for the development of this test framework

## Set-up

### Create virtualenv
`virtualenv -p python3 venv`

### Install dependencies
`pip install -r requirements.txt`

## Running tests

### Run all tests
Run all tests with `pytest` from the root directory of this project

Usage:

`pytest`

### Run tests by category
Run tests based on custom pytest markers that categorize the tests by type. Available markers:

- `smoke`: Runs minimal smoke tests to check health of cloud. Runs should be kept under 30 minutes
- `functional`: More thorough test of all features in cloud. Include positive and negative tests
- `performance`: Longer, metric based tests that take more time because of test repetition. Tests create metrics to compare to KPI baseline

Usage:

`pytest -m smoke`

### Run tests with an RTMP Runner fixture
Run tests with an RTMP Runner fixture, allowing usage of the `RTMP Runner` project (more here: <<<Kenneth needs to put this repo on the organization after some clean up>>>) to perform outsourced RTMP streaming into ingest. The default value is `192.168.1.158:8000` (which is just a non-static IP from a computer in the SJ office).

Usage:
`pytest --rtmp_runner=127.0.0.1:8000`
