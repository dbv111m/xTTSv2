ВАЖНАЯ ИНСТРУКЦИЯ ДЛЯ АГЕНТА (только для Gemini code assist)

**Проблема:** У меня возникают постоянные ошибки при использовании инструмента `replace` для изменения файлов. Я застреваю в цикле, неверно используя параметры `old_string` и `new_string`.

**Решение:** **в случае возникновения ошибок и зацикливания НЕ ИСПОЛЬЗОВАТЬ `replace`**.

Вместо этого, для редактирования файлов, СТРОГО следовать этому процессу:

1.  **ШАГ 1: Прочитать.** Использовать `read_file`, чтобы получить ПОЛНОЕ текущее содержимое файла.
2.  **ШАГ 2: Изменить.** Скопировать это содержимое в переменную и внести ВСЕ необходимые правки в этой переменной.
3.  **ШАГ 3: Записать.** Использовать `write_file` с параметром `content`, передав ему измененную переменную, чтобы ПОЛНОСТЬЮ перезаписать файл.

Этот метод "Прочитать-Изменить-Записать" является единственным надежным способом редактирования файлов. **Больше не использовать `replace`.**


# Python Development Rules

## Core Philosophy
- Follow Zen of Python: simple is better than complex, readability counts, explicit is better than implicit
- Write code for humans first, computers second
- Prefer clarity over cleverness
- If it's hard to explain, it's probably too complex

## Code Style & Structure
- Write simple, readable code without over-engineering
- Use functional programming style with pure functions, avoid classes unless absolutely necessary
- Use semantic, descriptive names for variables and functions (not x, tmp, data1)
- Follow PEP 8 conventions: snake_case for functions/variables, 4 spaces indentation
- Keep functions small (max 20-30 lines) and focused on one task
- Flat is better than nested: avoid deep nesting (max 2-3 levels)
- Use f-strings for string formatting
- Add docstrings only for complex functions, prefer self-documenting code

## Async Code
- Use async/await ONLY when truly necessary (I/O operations, API calls, database queries)
- Default to synchronous code for simplicity
- If adding async, explain why it's needed in comments

## Project Structure Example
Use simple project structure, as in examle below:

project/
├── .env # Environment variables (never commit)
├── .gitignore # Git ignore file
├── requirements.txt # Project dependencies
├── Dockerfile # Container definition
├── docker-compose.yml # Container orchestration
├── README.md # Project documentation
├── main.py # Entry point
├── config.py # Configuration loading
└── modules/ # Functional modules
├── database.py # DB operations
├── utils.py # Helper functions
└── handlers.py # Business logic

Adapt it if needed.




## Dependencies & Libraries
- Prefer simple, well-documented libraries over complex frameworks
- Use standard library when possible (pathlib, json, datetime, etc.)
- Common simple libraries: python-dotenv, requests, sqlite3 (built-in)
- Avoid heavy frameworks unless explicitly required

## Database
- Default to SQLite for development and small projects
- Use raw SQL or simple query builders (avoid heavy ORMs)
- Design schema with easy PostgreSQL migration in mind:
  - Use standard SQL types (TEXT, INTEGER, REAL, BLOB)
  - Avoid SQLite-specific features
  - Use parameterized queries for security
- Include migration path comments in database code

## Environment & Configuration
- Always use .env files for configuration (never hardcode secrets)
- Load environment variables with python-dotenv
- Provide .env.example with dummy values
- Use simple config.py to centralize settings:
    import os
    from dotenv import load_dotenv

    load_dotenv()

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///app.db")
    API_KEY = os.getenv("API_KEY")
    DEBUG = os.getenv("DEBUG", "False") == "True"


## Error Handling
- Use explicit try/except blocks with specific exception types
- Never use bare `except:` clauses
- Provide clear, actionable error messages
- Log errors for debugging, fail gracefully for users
- Для лучшей читаемости кода используй для логирования декораторы.

## Docker & Deployment
- Always provide Dockerfile with clear comments
- Use slim Python base images (python:3.12-slim)
- Include docker-compose.yml for easy local development
- Document all environment variables needed
- Use multi-stage builds only if image size is critical

## Git & Version Control
- Include comprehensive .gitignore:
  - .env files
  - __pycache__/, *.pyc
  - venv/, .venv/
  - *.db (SQLite files)
  - .DS_Store, Thumbs.db
- Write clear commit messages

## Documentation
- Include README.md with:
  - Project description
  - Setup instructions
  - Environment variables list
  - How to run locally and with Docker
- Comment complex logic, not obvious code
- Use type hints for function parameters and returns

## Testing & Debugging
- Add simple print statements or logging for debugging
- Use descriptive variable names to reduce debugging need
- Test with real data early and often

## Code Generation Preferences
- Generate complete, working code (not TODOs or placeholders)
- Include all necessary imports at the top
- Provide usage examples in comments
- Explain non-obvious decisions in comments
- When suggesting improvements, show before/after examples

## What to Avoid
- Don't use classes when functions suffice
- Don't add async if synchronous code works fine
- Don't use complex design patterns (factories, singletons, etc.)
- Don't over-abstract or create unnecessary layers
- Don't use type checking libraries (pydantic, dataclasses) unless needed
- Don't add dependencies without explaining why they're needed

## SQLite → PostgreSQL Migration Notes
- When writing database code, add comments about PostgreSQL compatibility
- Use connection strings that can switch between SQLite and PostgreSQL
- Example:
    Works with both SQLite and PostgreSQL via connection string

    def get_connection():
    db_url = os.getenv("DATABASE_URL", "sqlite:///app.db")
    if db_url.startswith("sqlite"):
    return sqlite3.connect(db_url.replace("sqlite:///", ""))



По умолчанию не добавляй версии библиотек в requirements.txt на этапе разработке и дебага. Потом если что будет добавлено вручную (и только там где возникают ошибки)

Создавай скрипт powersherll для начала работы с проектом в vs code на windows (python -m venv .venv и .venv\Scripts\activate.bat и pip install -r requirements.txt внутри .venv)

Для докера делай нестандартные порты по умолчанию, чтобы не использовать уже занятые другими приложениями.

Если нужно сделать веб фронтенд, по умолчанию используй что нибудь простое, типа FastAPI, HTMX & Bootstrap, с поддержкой mobile first и PWA