# Graduation Project Architecture

## Project Title
**Development of an Online Platform for Learning Python Programming with an Interactive Code Execution System**

---

## 1) System Architecture Choice

### Recommended style: **Modular Monolith (Django) + Isolated Code Runner Worker**

For a university graduation project, this is the best trade-off between engineering quality and delivery speed.

- **Core platform** (users/courses/lessons/tasks/progress/submissions API + web pages) runs as one Django project (monolith).
- **Code execution** is isolated as a separate runtime component (worker service) that launches Docker sandboxes.
- Communication between Django and the runner is asynchronous through a job queue.

### Why not full microservices?
- You would spend significant effort on service discovery, distributed auth, tracing, and deployment complexity.
- For this scope, microservices add overhead with little academic benefit.

### Why modular monolith works well
- Simpler deployment and debugging.
- Keeps domain boundaries using Django apps.
- Easy to scale later by splitting `code_runner` first if needed.
- Preserves clean architecture concepts expected from senior design.

---

## 2) Project Folder Structure

```text
python-learning-platform/
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py
├── apps/
│   ├── users/
│   ├── courses/
│   ├── lessons/
│   ├── tasks/
│   ├── submissions/
│   └── code_runner/
├── templates/
│   ├── base.html
│   ├── components/
│   └── pages/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
├── docker/
│   ├── app/Dockerfile
│   ├── runner/Dockerfile
│   ├── compose.yml
│   ├── sandbox/seccomp.json
│   └── sandbox/run_executor.sh
├── scripts/
│   ├── wait_for_db.sh
│   └── create_superuser.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── api/
└── README.md
```

---

## 3) Django Apps Structure

### `users`
- Custom `User` model.
- Authentication, profile, roles (`student`, `instructor`, `admin`).
- JWT token endpoints integration.

Suggested files:
- `models.py`, `serializers.py`, `views.py`, `urls.py`, `permissions.py`, `services.py`

### `courses`
- Course metadata, enrollment, publication state.
- Course listing and detail endpoints.

### `lessons`
- Lessons belong to courses.
- Ordering, lesson content, lesson type (theory/practice).

### `tasks`
- Programming tasks attached to lessons.
- Difficulty, starter code, constraints.
- Hidden/public test cases.

### `submissions`
- User solution attempts.
- Status lifecycle (`queued`, `running`, `passed`, `failed`, `error`, `timeout`).
- Stores execution output and score.

### `code_runner`
- Queue producer/consumer integration.
- Docker execution adapter.
- Resource limits, sandbox policies, result parser.

---

## 4) Database Schema (PostgreSQL)

## Core Models and Fields

### 1. `User`
- `id` (PK)
- `email` (unique)
- `username` (unique)
- `password` (hashed)
- `first_name`, `last_name`
- `role` (`student`, `instructor`, `admin`)
- `is_active`, `is_staff`, `is_superuser`
- `date_joined`, `last_login`

### 2. `Course`
- `id` (PK)
- `title`
- `slug` (unique)
- `description`
- `level` (`beginner`, `intermediate`, `advanced`)
- `is_published`
- `created_by` (FK → `User`, instructor)
- `created_at`, `updated_at`

### 3. `Lesson`
- `id` (PK)
- `course` (FK → `Course`)
- `title`
- `content` (Markdown/HTML)
- `order_index`
- `lesson_type` (`theory`, `practice`, `quiz`)
- `estimated_minutes`
- `is_published`
- `created_at`, `updated_at`

### 4. `Task`
- `id` (PK)
- `lesson` (FK → `Lesson`)
- `title`
- `description`
- `input_format`
- `output_format`
- `constraints`
- `difficulty` (`easy`, `medium`, `hard`)
- `starter_code`
- `solution_template`
- `max_score`
- `time_limit_ms`
- `memory_limit_mb`
- `is_published`
- `created_at`, `updated_at`

### 5. `TestCase`
- `id` (PK)
- `task` (FK → `Task`)
- `input_data`
- `expected_output`
- `is_hidden` (public sample vs hidden grader test)
- `weight`
- `order_index`

### 6. `Submission`
- `id` (PK)
- `user` (FK → `User`)
- `task` (FK → `Task`)
- `source_code`
- `language` (for now fixed default: `python`)
- `status` (`queued`, `running`, `passed`, `failed`, `error`, `timeout`)
- `score`
- `passed_tests`
- `total_tests`
- `stdout`
- `stderr`
- `execution_time_ms`
- `memory_used_kb`
- `runner_log`
- `submitted_at`
- `evaluated_at`

### 7. `Progress`
- `id` (PK)
- `user` (FK → `User`)
- `course` (FK → `Course`)
- `lesson` (nullable FK → `Lesson`)
- `task` (nullable FK → `Task`)
- `status` (`not_started`, `in_progress`, `completed`)
- `completion_percent`
- `last_accessed_at`
- `completed_at`

## Supporting Models (recommended)

### `Enrollment`
- `user` (FK → `User`)
- `course` (FK → `Course`)
- `enrolled_at`
- Unique constraint: (`user`, `course`)

### `SubmissionTestResult`
- `submission` (FK → `Submission`)
- `test_case` (FK → `TestCase`)
- `status`
- `actual_output`
- `execution_time_ms`

## Relationships Summary
- One `Course` has many `Lesson`.
- One `Lesson` has many `Task`.
- One `Task` has many `TestCase`.
- One `User` has many `Submission`.
- One `Task` has many `Submission`.
- `Progress` links user learning state to course/lesson/task granularity.
- `Enrollment` links many-to-many between users and courses.

---

## 5) REST API Endpoints (DRF)

Base prefix: `/api/v1/`

### Authentication
- `POST /auth/register/`
- `POST /auth/login/`
- `POST /auth/token/refresh/`
- `POST /auth/logout/`
- `GET /auth/me/`
- `PATCH /auth/me/`

### Courses
- `GET /courses/` (list, filters by level/published)
- `POST /courses/` (instructor/admin)
- `GET /courses/{id}/`
- `PATCH /courses/{id}/`
- `DELETE /courses/{id}/`
- `POST /courses/{id}/enroll/`
- `GET /courses/{id}/progress/`

### Lessons
- `GET /courses/{course_id}/lessons/`
- `POST /courses/{course_id}/lessons/` (instructor)
- `GET /lessons/{id}/`
- `PATCH /lessons/{id}/`
- `DELETE /lessons/{id}/`

### Tasks
- `GET /lessons/{lesson_id}/tasks/`
- `POST /lessons/{lesson_id}/tasks/` (instructor)
- `GET /tasks/{id}/`
- `PATCH /tasks/{id}/`
- `DELETE /tasks/{id}/`
- `GET /tasks/{id}/testcases/` (instructor/admin only; hide for students)

### Submissions
- `POST /tasks/{task_id}/submissions/` (submit solution)
- `GET /tasks/{task_id}/submissions/my/`
- `GET /submissions/{id}/`
- `GET /submissions/{id}/results/`

### Run Code (without grading or with sample tests)
- `POST /code/run/`  
  Body: `{ "task_id": ..., "source_code": "...", "mode": "dry_run|submit" }`
- `GET /code/run/{job_id}/status/`

### Progress
- `GET /progress/me/`
- `GET /progress/courses/{course_id}/`
- `POST /progress/lessons/{lesson_id}/complete/`

---

## 6) Secure Code Execution Architecture (Docker Sandbox)

## Components
1. **Django API service**: receives submissions/run requests.
2. **Queue broker** (Redis/RabbitMQ): stores jobs.
3. **Runner worker** (Celery worker in `code_runner` app): consumes jobs.
4. **Sandbox container** (ephemeral Docker container per run): executes untrusted Python code.
5. **Result store** (PostgreSQL): saves `Submission` status and test results.

## Execution flow
1. Student sends code to `/code/run/` or `/tasks/{id}/submissions/`.
2. API validates and saves `Submission(status=queued)`.
3. API pushes job to queue.
4. Worker receives job and prepares isolated temp directory with:
   - student code
   - executor script
   - serialized test cases
5. Worker starts Docker container with strict limits:
   - `--network none`
   - CPU quota
   - memory limit
   - process limit (`pids-limit`)
   - read-only filesystem (+ writable `/tmp`)
   - non-root user
   - dropped Linux capabilities
   - seccomp/apparmor profile
   - execution timeout (kill if exceeded)
6. Container runs tests and returns JSON result.
7. Worker parses result, updates `Submission` + `SubmissionTestResult`.
8. Frontend polls `/code/run/{job_id}/status/` and shows feedback.

## Essential sandbox protections
- Disable outbound network.
- Prevent host filesystem mounts except controlled temp volume.
- Enforce strict timeout and memory limits.
- Restrict dangerous Python modules if needed (secondary protection).
- Log every execution event for audit.

---

## 7) Frontend Pages (HTML/CSS/JS + Bootstrap)

1. **Homepage**
   - Platform overview, CTA, featured courses.
2. **Auth pages**
   - Login, Register, Forgot Password (optional).
3. **Course catalog page**
   - Search/filter courses.
4. **Course detail page**
   - Syllabus, enrollment, progress bar.
5. **Lesson page**
   - Theory content + next/previous navigation.
6. **Coding page (IDE-like)**
   - Code editor area.
   - Run button.
   - Submit button.
   - Output panel (`stdout/stderr`).
   - Test result breakdown.
7. **Dashboard**
   - Enrolled courses, completion statistics, recent submissions.
8. **Profile settings**
   - User info and password change.
9. **Admin panel**
   - Django admin + optional custom instructor dashboard for content management.

---

## 8) Security Considerations

- **Auth & authorization**
  - JWT auth for API.
  - Role-based permissions per endpoint.
- **Input validation**
  - DRF serializers with strict field validation.
- **Rate limiting**
  - Limit login attempts and code-run requests.
- **Secure headers**
  - CSP, X-Frame-Options, HSTS, X-Content-Type-Options.
- **CSRF/XSS**
  - CSRF for session endpoints; escape rendered content.
- **Secrets management**
  - Use environment variables and `.env`, never hardcode secrets.
- **Database safety**
  - Use ORM, avoid raw SQL unless parameterized.
- **Audit logging**
  - Track auth events, submissions, admin changes.
- **Transport security**
  - HTTPS only in production.
- **Sandbox hardening**
  - Isolate code runner host from main infrastructure.

---

## 9) Data Flow Diagram (Textual)

```text
[Browser UI]
   | 1. API Request (login/course/task/run)
   v
[Django + DRF API]
   | 2. Read/Write domain data
   v
[PostgreSQL]

Code execution path:
[Browser UI] -- submit code --> [Django API]
[Django API] -- create submission + enqueue job --> [Queue Broker]
[Runner Worker] -- consume job --> [Docker Sandbox]
[Docker Sandbox] -- test results --> [Runner Worker]
[Runner Worker] -- update submission --> [PostgreSQL]
[Browser UI] -- poll status endpoint --> [Django API]
```

---

## 10) Architecture Explanation for a Junior Developer

Think of the platform as **two big parts**:

1. **Learning Management Part (Django Monolith)**
   - Manages users, courses, lessons, tasks, submissions, and progress.
   - Exposes REST APIs for frontend.
   - Renders HTML pages using Bootstrap templates.

2. **Execution Part (Sandbox Runner)**
   - Never runs student code directly inside Django process.
   - Uses job queue + worker + temporary Docker containers.
   - Each execution is isolated, limited, and disposable.

### Typical student journey
1. Student logs in.
2. Opens a course, reads a lesson.
3. Opens coding task and writes Python code.
4. Clicks **Run** for quick feedback (sample tests).
5. Clicks **Submit** for official grading (hidden tests included).
6. Backend stores results and updates progress dashboard.

### Why this design is professional
- Clear separation of concerns.
- Safe execution of untrusted code.
- Scalable enough for real users.
- Maintainable: each Django app has a clear domain.
- Easy to defend in graduation presentation with architectural rationale.

---

## Suggested Future Enhancements
- Real-time output via WebSocket instead of polling.
- Plagiarism detection module.
- Gamification (badges, streaks, leaderboard).
- Multi-language support (JS/C++ runners).
- Kubernetes-based autoscaling of runner workers.

---

## Base Django Project Bootstrap (Implemented)

The repository now includes a starter Django codebase under `project/` with the requested layout:

```text
project/
├── manage.py
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── users/
├── courses/
├── lessons/
├── tasks/
├── submissions/
└── code_runner/
```

Each app includes starter files: `apps.py`, `models.py`, `views.py`, `urls.py`, `admin.py`, `tests.py`, and `migrations/__init__.py`.

### Installed apps configuration
`config/settings.py` is configured with:
- Django core apps
- `rest_framework`
- `users`, `courses`, `lessons`, `tasks`, `submissions`, `code_runner`

### Base URLs
`config/urls.py` includes:
- `/admin/`
- `/health/`
- `/api/v1/users/`
- `/api/v1/courses/`
- `/api/v1/lessons/`
- `/api/v1/tasks/`
- `/api/v1/submissions/`
- `/api/v1/code-runner/`

---

## Run Locally

1. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `source .venv/bin/activate` (Linux/macOS)

2. Install dependencies:
   - `pip install -r project/requirements.txt`

3. Set environment variables (example):
   - `export DJANGO_SECRET_KEY='change-me'`
   - `export DJANGO_DEBUG=True`
   - `export POSTGRES_DB=python_learning`
   - `export POSTGRES_USER=postgres`
   - `export POSTGRES_PASSWORD=postgres`
   - `export POSTGRES_HOST=127.0.0.1`
   - `export POSTGRES_PORT=5432`

4. Run migrations:
   - `cd project`
   - `python manage.py migrate`

5. Start development server:
   - `python manage.py runserver`

6. Verify:
   - Open `http://127.0.0.1:8000/health/`
   - Open `http://127.0.0.1:8000/api/v1/users/`

---

## Implemented Django Models (Base Domain Layer)

The base ORM models are now implemented across apps:
- `users.User`
- `courses.Course`
- `courses.Progress`
- `lessons.Lesson`
- `tasks.Task`
- `tasks.TestCase`
- `submissions.Submission`

### Model explanations

1. **User (`users.User`)**
   - Extends `AbstractUser`.
   - Adds role (`student`, `instructor`, `admin`) for role-based behavior.
   - Uses unique email and includes profile metadata (`bio`, `date_of_birth`).
   - Includes `created_at` / `updated_at` timestamps.

2. **Course (`courses.Course`)**
   - Represents a learning track.
   - Linked to one instructor (`ForeignKey` to `User`).
   - Supports many enrolled students (`ManyToMany` to `User`).
   - Has level (`beginner`, `intermediate`, `advanced`), publication flag, slug, and timestamps.

3. **Lesson (`lessons.Lesson`)**
   - Belongs to one course (`ForeignKey`).
   - Stores ordered instructional content (`order_index`, `content`, `lesson_type`).
   - Includes estimated duration and publish state.

4. **Task (`tasks.Task`)**
   - Belongs to one lesson (`ForeignKey`).
   - Contains problem statement, starter code, I/O format, constraints, scoring, limits.
   - Includes difficulty choices (`easy`, `medium`, `hard`) and timestamps.

5. **TestCase (`tasks.TestCase`)**
   - Belongs to one task (`ForeignKey`).
   - Stores input and expected output for auto-checking.
   - Supports hidden/public tests (`is_hidden`), weighted scoring, and ordering.

6. **Submission (`submissions.Submission`)**
   - Belongs to one user and one task (`ForeignKey`).
   - Stores source code, status lifecycle, score, execution metrics, and outputs.
   - Tracks submission and evaluation times for runner integration.

7. **Progress (`courses.Progress`)**
   - Tracks learning state per user at course/lesson/task granularity.
   - Linked to user and course (required), lesson/task (optional).
   - Stores completion percentage, status (`not_started`, `in_progress`, `completed`), and learning timestamps.


---

## Implemented REST API (DRF)

The requested endpoints are implemented as follows:

1. `POST /register`
   - Creates a new user account using username/email/password.
   - Returns created user data and an auth token.

2. `POST /login`
   - Authenticates with username and password.
   - Returns auth token and basic user profile.

3. `GET /courses`
   - Returns published courses list.

4. `GET /courses/{id}`
   - Returns details for one published course.

5. `GET /lessons/{id}`
   - Returns one published lesson and its content metadata.

6. `GET /tasks/{id}`
   - Returns one published programming task including difficulty and limits.

7. `POST /submit-solution`
   - Requires authentication token.
   - Accepts `task_id`, `source_code`, optional `language`.
   - Creates a `Submission` with queued status.

8. `POST /run-code`
   - Requires authentication token.
   - Accepts source code payload and returns queued execution response.
   - Current implementation is a safe placeholder; Docker-based execution integration is next.

### Authentication usage
- Include token in requests after login/register:
  - `Authorization: Token <token>`


---

## Frontend Code Editor Page (Implemented)

A full browser-based coding page is now available at:
- `GET /editor`

### Built with
- HTML + Bootstrap
- CSS
- JavaScript
- CodeMirror (Python mode)

### Features included
- Write Python code in an editor.
- Run code using `POST /run-code`.
- Submit solution using `POST /submit-solution`.
- Send auth token and payload to backend APIs with Fetch.
- Display output/status messages.
- Display test/submission result table (submission id, status, passed/total, score).

### Files
- `project/templates/code_editor.html`
- `project/static/css/code_editor.css`
- `project/static/js/code_editor.js`
- `project/code_runner/views.py` (`CodeEditorPageView`)
- `project/code_runner/urls.py` (`/editor`, `/run-code`)


---

## Automatic Grading System (Implemented)

When a user calls `POST /submit-solution`, the backend now performs the full grading flow:

1. **Save submission**
   - Create `Submission(status=queued)` with source code and task link.

2. **Run code**
   - Status moves to `running`.
   - For each test case, user code is executed in an isolated temporary file using a subprocess call.

3. **Run test cases**
   - The grader loops through all `Task.test_cases` in order.
   - Each case uses the test input as `stdin`.
   - Per-case timeout is based on task `time_limit_ms`.

4. **Compare output**
   - Actual stdout and expected output are normalized (trim trailing spaces/blank edges) and compared.
   - Passed case increments `passed_tests` and accumulates weighted score.

5. **Return result**
   - Submission is finalized with:
     - `passed_tests`
     - `failed_tests` (`total_tests - passed_tests`)
     - `execution_time_ms`
     - `score`
     - final `status` (`passed`, `failed`, or `timeout`)

### API response highlights (`POST /submit-solution`)
The response now includes direct grading summary fields:
- `passed_tests`
- `failed_tests`
- `execution_time_ms`

This makes it simple for the frontend editor to show immediate grading feedback after submission.

---

## Secure Python Code Execution Design (Docker)

This project should execute untrusted user code in **ephemeral Docker sandboxes**, not inside the Django web process.

### 1) How user code is executed
1. Django receives `POST /submit-solution`.
2. Backend creates a `Submission` row (`queued`).
3. Worker prepares JSON payload containing:
   - `source_code`
   - test case inputs/expected outputs
   - `time_limit_ms`
4. Worker starts one short-lived Docker container from a runner image.
5. Container runs `executor.py`, executes user code per test case, and prints JSON result.
6. Worker parses JSON and updates `Submission` with:
   - `passed_tests`
   - `failed_tests`
   - `execution_time_ms`
   - final status.

### 2) CPU and memory limits
Use Docker runtime limits when starting the container:
- `--cpus=0.5` (or per-task policy)
- `--memory=256m`
- `--pids-limit=64`
- strict timeout in code runner (`subprocess timeout` and container kill deadline)

These prevent one submission from exhausting host resources.

### 3) Preventing malicious code
Defense-in-depth controls:
- `--network none` (no internet access)
- `--read-only` filesystem + writable tmpfs only (`/tmp`)
- run as non-root user
- `--cap-drop ALL`
- `no-new-privileges`
- custom `seccomp` profile (deny dangerous syscalls)
- short execution timeouts
- never mount host-sensitive paths

### 4) Container cleanup
- Runner containers must be **ephemeral** and removed after every run:
  - `docker run --rm ...`
- Worker should still call forced cleanup on timeout/error:
  - `docker rm -f <container_id>`
- Periodic host cleanup can be scheduled:
  - `docker container prune -f`

### Example Docker configuration
Added reference files:
- `docker/runner/Dockerfile`
- `docker/sandbox/executor.py`
- `docker/sandbox/seccomp.json`
- `docker/compose.runner-example.yml`

These files provide a concrete secure baseline you can integrate with Celery workers next.

---

## Frontend Pages (Modern UI Templates)

Implemented Bootstrap-based pages for the learning platform UI:

- `GET /homepage` → `project/templates/pages/homepage.html`
- `GET /dashboard` → `project/templates/pages/dashboard.html`
- `GET /course` → `project/templates/pages/course_page.html`
- `GET /lesson` → `project/templates/pages/lesson_page.html`
- `GET /coding` → `project/templates/pages/coding_page.html`

Shared styling is in:
- `project/static/css/platform.css`

Design goals:
- clean modern cards and spacing
- gradient hero section for landing page
- progress indicators and status badges
- dashboard stats and activity feed
- coding layout with editor area, output, and test summary

---

## Final Assembly

A full assembled view of backend/frontend/docker/database plus run commands is available in:
- `PROJECT_STRUCTURE.md`

Additional database bootstrap files:
- `database/init.sql`
- `database/README.md`
