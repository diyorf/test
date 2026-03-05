# Final Project Assembly

## Folder Structure

```text
.
├── project/                      # Backend (Django + DRF)
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   ├── users/
│   ├── courses/
│   ├── lessons/
│   ├── tasks/
│   ├── submissions/
│   ├── code_runner/
│   ├── templates/               # Frontend HTML templates
│   │   ├── code_editor.html
│   │   └── pages/
│   │       ├── homepage.html
│   │       ├── dashboard.html
│   │       ├── course_page.html
│   │       ├── lesson_page.html
│   │       └── coding_page.html
│   └── static/                  # Frontend CSS/JS assets
│       ├── css/
│       └── js/
├── docker/                       # Docker runner and sandbox
│   ├── runner/
│   │   └── Dockerfile
│   ├── sandbox/
│   │   ├── executor.py
│   │   └── seccomp.json
│   └── compose.runner-example.yml
├── database/                     # Database setup files
│   ├── init.sql
│   └── README.md
├── README.md
└── PROJECT_STRUCTURE.md
```

## Component Mapping

- **Backend**: `project/` (Django apps + API + grading service)
- **Frontend**: `project/templates/` and `project/static/`
- **Docker Code Runner**: `docker/`
- **Database**: `database/` and PostgreSQL settings in `project/config/settings.py`

## Run Instructions

### 1) Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r project/requirements.txt
```

### 2) Migrate database

```bash
export POSTGRES_DB=python_learning
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_HOST=127.0.0.1
export POSTGRES_PORT=5432
cd project
python manage.py migrate
```

### 3) Run server

```bash
python manage.py runserver
```

Main pages:
- `http://127.0.0.1:8000/homepage`
- `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/course`
- `http://127.0.0.1:8000/lesson`
- `http://127.0.0.1:8000/coding`
- `http://127.0.0.1:8000/editor`

### 4) Run Docker code runner

Build runner image:

```bash
docker build -f docker/runner/Dockerfile -t python-grader-runner:local .
```

Run sandbox container with limits:

```bash
docker run --rm \
  --network none \
  --read-only \
  --tmpfs /tmp:size=64m,mode=1777 \
  --cpus=0.5 \
  --memory=256m \
  --pids-limit=64 \
  --cap-drop ALL \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=$(pwd)/docker/sandbox/seccomp.json \
  -i python-grader-runner:local
```

Or inspect compose reference:

```bash
cat docker/compose.runner-example.yml
```
