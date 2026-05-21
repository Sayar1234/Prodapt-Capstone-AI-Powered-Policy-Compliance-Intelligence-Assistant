# Policy Compliance Intelligence Frontend

React + TypeScript + Tailwind UI for the FastAPI backend.

## Package List

Install/update everything with:

```bash
npm install
```

Direct packages used by the app:

```bash
npm install react react-dom lucide-react clsx tailwind-merge
npm install -D @vitejs/plugin-react vite typescript tailwindcss postcss autoprefixer eslint typescript-eslint @types/react @types/react-dom @types/node eslint-plugin-react-hooks eslint-plugin-react-refresh globals
```

## Backend Connection

By default the frontend calls:

```text
http://localhost:8000/api/v1
```

Override it with a local env file:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Run

Start the backend first, then run:

```bash
npm run dev -- --host 127.0.0.1 --port 5173
```

Open:

```text
http://127.0.0.1:5173
```

## Verify

```bash
npm run lint
npm run build
```

Both commands should pass before demo or deployment.
