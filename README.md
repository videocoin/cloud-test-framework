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

Usage:

`pytest -m smoke`

### Run tests with an RTMP Runner
Run tests with an RTMP Runner fixture
```
cd rtmp_runner
make docker-build && make docker-run
```
## Docker run

Usage:
`make docker-build && make docker-run`
