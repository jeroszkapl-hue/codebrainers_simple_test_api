# Setup

0. Install Python 3.13.2 or newer

1. Clone repository
```bash
git clone https://github.com/pwalaszkowski/codebrainers_simple_test_api.git
```

2. Open directory with cloned repository
```bash
cd codebrainers_simple_test_api
```

3. Create Python venv 
```bash
python -m venv .venv
```

4. Activate venv
```bash
.\.venv\Scripts\Activate
```

5. Install all required Python modules
```bash
python -m pip install -r requirements.txt
```

# Running app
1. Launch app using commandline/terminal
```bash
python run.py
```

2. Navigate to: ```http://127.0.0.1:8000/```

# Running Tests
Run the test suite with pytest:
```bash
pytest
```

# Performance Tests
A simple Locust load test lives in `tests/locust/locustfile.py` (not part of the pytest suite). It logs in, then exercises the employee list/create/update/delete endpoints with weighted tasks, re-logging in automatically if the 10-minute token expires mid-run.

```bash
pip install -r tests/locust/requirements.txt   # separate from requirements.txt — Locust's web UI pulls in Flask/gevent
python run.py                                  # in one terminal

# Interactive web UI at http://localhost:8089
locust -f tests/locust/locustfile.py --host http://127.0.0.1:8000

# Or headless, e.g. a 10-user/1-minute smoke run
locust -f tests/locust/locustfile.py --host http://127.0.0.1:8000 \
    --headless --users 10 --spawn-rate 2 --run-time 1m
```

# Functional Requirements
Available [here](FUNCTIONAL_REQUIREMENTS.md)

# Downloads
CI builds standalone macOS and Windows apps on each run (see [`ci.yml`](.github/workflows/ci.yml)). Grab the latest build:

1. Open the [CI workflow runs](https://github.com/pwalaszkowski/codebrainers_simple_test_api/actions/workflows/ci.yml)
2. Pick the most recent successful run
3. Download `macos-app` or `windows-app` from the Artifacts section at the bottom of the run summary

Note: GitHub Actions artifacts expire after 90 days and require being signed in to GitHub to download.