# Backend (Flask)

Setup and runtime instructions have been moved to the consolidated file at `build/README.md`.

This folder contains a minimal Flask entrypoint: `main.py`.

Endpoint provided by this backend:
- GET / -> friendly JSON message

Notes:
- For setup and running instructions, see `build/README.md` at the project root.
- For production usage import `create_app` from `src/backend/main.py` and run under a WSGI server.
