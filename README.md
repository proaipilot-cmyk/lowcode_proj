# 🤖 Agentic Test Automation Tool

A low-code, agentic tool that accepts freeform user steps, navigates web applications via Playwright, and auto-generates a complete **Page Object Model** test framework in Python.

## Architecture

```
lowcode_analytics/
├── app.py                         # Flask web server (UI + API)
├── requirements.txt               # Python dependencies
├── agent/
│   ├── __init__.py
│   ├── step_parser.py             # NL step → structured action
│   ├── browser_agent.py           # Playwright browser driver + element discovery
│   ├── object_repository.py       # JSON-based shared object repository
│   ├── page_generator.py          # POM class generator
│   ├── test_generator.py          # pytest test file generator
│   ├── report_generator.py        # HTML execution report + pytest runner
│   └── scaffold.py                # Output project structure creator
├── templates/
│   └── index.html                 # Web UI
├── static/
│   └── style.css                  # Dark theme styling
└── output/                        # ← Generated test project
    ├── object_repository/
    │   └── repository.json        # Shared element locators
    ├── pages/
    │   ├── base_page.py           # Base page object
    │   └── <page_name>.py         # Auto-generated page objects
    ├── tests/
    │   └── test_user_flow.py      # Auto-generated pytest tests
    ├── reports/
    │   ├── execution_report.html  # Step execution report
    │   └── report.html            # pytest-html report
    ├── conftest.py                # Shared pytest fixtures
    └── pytest.ini                 # pytest configuration
```

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Launch the web UI

```bash
python app.py
```

Open **http://localhost:5000** in your browser.

### 3. Enter test steps

Type freeform steps like:

```
1. Go to https://example.com/login
2. Enter 'admin' in username field
3. Enter 'secret123' in password field
4. Click Login button
5. Verify dashboard page is displayed
6. Click on Reports link
```

### 4. Click **Run**

The tool will:
1. Parse your steps into structured actions
2. Launch a Playwright browser and execute each step
3. Discover all interactive elements on every page visited
4. Build a shared **Object Repository** (`repository.json`)
5. Generate **Page Object Model** classes under `output/pages/`
6. Generate **pytest tests** under `output/tests/`
7. Produce an **execution report** under `output/reports/`

### 5. Run the generated tests

```bash
cd output
python -m pytest tests/ --html=reports/report.html --self-contained-html -v
```

Or in headed mode (visible browser):

```bash
cd output
python -m pytest tests/ --headed --html=reports/report.html --self-contained-html -v
```

## Supported Actions

| Keyword | Action | Example |
|---------|--------|---------|
| `go to`, `navigate to`, `open`, `visit` | Navigate to URL | `Go to https://example.com` |
| `enter`, `type`, `fill` | Input text | `Enter 'admin' in username field` |
| `click`, `press`, `tap` | Click element | `Click Login button` |
| `select`, `choose` | Select dropdown | `Select 'Option A' from dropdown` |
| `hover`, `mouse over` | Hover element | `Hover over Settings menu` |
| `verify`, `check`, `assert` | Assert visibility | `Verify dashboard is displayed` |
| `wait`, `pause` | Wait | `Wait 3 seconds` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web UI |
| `POST` | `/api/run` | Execute steps + generate all artifacts |
| `POST` | `/api/parse` | Preview parsed steps (no browser) |
| `GET` | `/api/repository` | Get current object repository |
| `GET` | `/api/tree` | Get output project tree |

## Generated Output

- **Object Repository** (`repository.json`): Shared JSON file mapping page names → elements → locators. Referenced across all generated page objects.
- **Page Objects** (`pages/*.py`): One class per page, inheriting from `BasePage`. Locators as attributes, action methods for each element.
- **Tests** (`tests/test_user_flow.py`): pytest test class that replays user steps using page objects.
- **Reports**: HTML execution report + pytest-html report with pass/fail details.

## Design Principles

- **Reusability**: Page objects are independent and composable
- **Single source of truth**: Object repository is the master locator store
- **Playwright-native locators**: Prefers `get_by_role`, `get_by_label`, `get_by_placeholder` over fragile CSS/XPath
- **Extensible**: Add new action patterns in `step_parser.py`, new locator strategies in `browser_agent.py`
