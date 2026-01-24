# Build / Project Setup — Quick Start

This file contains consolidated setup instructions for running the frontend and backend locally, plus developer setup notes for WSL and VS Code.

## Frontend — Quick Start

The frontend lives in `src/frontend` and uses Vite + React. You will need Node.js (v16+ or compatible) and npm (or yarn/pnpm) installed.

1. Install dependencies

PowerShell (Windows):

```powershell
cd src/frontend; npm install
```

WSL / Bash:

```bash
cd src/frontend
npm install
```

2. Run the dev server

macOS / WSL / Bash:

```bash
# from project root
cd src/frontend
npm run dev
```

PowerShell (Windows):

```powershell
cd src/frontend
npm run dev
```

Vite defaults to port 5173. If you need the frontend to call the backend during development, either configure a proxy in `vite.config.js` or call the backend by absolute URL (e.g., http://localhost:5000/).

3. Build for production

```bash
cd src/frontend
npm run build
```

4. Preview the production build locally

```bash
cd src/frontend
npm run preview
```

Notes:

- If you use a different package manager (yarn/pnpm) replace `npm install` and `npm run ...` with the appropriate commands.
- For a development experience where the frontend and backend run together, consider configuring a dev proxy in `vite.config.js` so requests to `/api` are proxied to `http://localhost:5000/`.

---

## Backend — Quick Start

Quick steps to run the backend locally. WSL / Ubuntu is recommended since the workspace is under WSL in this project.

1. Create a virtual environment and install dependencies (WSL)

From WSL (project root):

```bash
./scripts/setup_backend.sh
```

This will create a `.venv` directory (if missing) and install packages from `src/backend/requirements.txt`.

If you prefer manual steps:

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

WSL / Bash:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r src/backend/requirements.txt
```

2. Run the app

macOS / WSL / Bash:

```bash
# from the project root
.venv/bin/python src/backend/main.py
```

PowerShell (Windows):

```powershell
.\.venv\Scripts\python.exe src\backend\main.py
```

The app will start on 0.0.0.0:5000 by default. Set `FLASK_DEBUG=1` to enable debug.

Notes:

- If you plan to serve with a production WSGI server (gunicorn/uvicorn) import `create_app` from `src/backend/main.py` and pass it to the server.

---

## Developer / VS Code (WSL) notes

These steps help remove editor diagnostics (red squiggles) by ensuring VS Code/Pylance uses the project venv.

1. Open the project in Remote - WSL so VS Code runs inside the WSL environment (status bar should show "WSL: Ubuntu").

2. Select the interpreter: `/home/<user>/project_team_16/Project/.venv/bin/python`

- Command Palette -> "Python: Select Interpreter" -> choose the path above. If it's not shown, use "Enter interpreter path" and paste it.

3. Restart the Python language server (Pylance)

- Command Palette -> "Python: Restart Language Server" or Command Palette -> "Developer: Reload Window".

4. Run the backend (WSL)

```bash
.venv/bin/python src/backend/main.py
```

Notes:

- We don't use `.env` files in this repository per project convention; environment variables are read directly from the OS environment.
- `.gitignore` excludes `.venv`, `.vscode`, and common build artifacts.
