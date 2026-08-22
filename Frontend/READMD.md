# Medical RAG Frontend

A dependency-free static frontend for the Medical RAG backend. It combines a modern medical landing page inspired by the reference image with the operational screens needed by the RAG system.

## Features

- Hero section styled like a modern medical clinic website.
- Backend token connection field for authenticated FastAPI requests.
- Built-in account creation and sign-in flow that stores the access token for the browser session.
- PDF upload flow using `POST /documents/upload`.
- Document processing action using `POST /documents/{document_id}/process`.
- Clinical Q&A panel using `POST /rag/answer`.
- Answer, evaluation metrics, and retrieved evidence display.

## Setup without Node.js or npm

This frontend is plain HTML, CSS, and JavaScript. You do **not** need to install `npm` with `pip`, and the PyPI package named `npm` is not the Node.js package manager.

From the repository root, run:

```bash
cd Frontend
python3 -m http.server 5173
```

Then open:

```text
http://localhost:5173
```

## Optional npm scripts

If real Node.js/npm is already installed on your machine, you can use the convenience scripts:

```bash
cd Frontend
npm run dev
```

That command runs the same Python static server behind the scenes.

## Backend URL

The UI defaults to `http://localhost:5000` for the FastAPI backend. To override it without rebuilding, set this before `src/main.js` runs:

```html
<script>window.MEDICAL_RAG_API_BASE_URL = 'http://localhost:5000';</script>
```

## Run the backend and database

Serving the static frontend alone does **not** start the API or PostgreSQL, so
form entries cannot be saved until the following services are running. In a
second terminal, from the repository root:

```bash
cd Backend
cp .env.example .env
# Edit .env and set DATABASE_URL, SECRET_KEY, ALGORITHM, and ACCESS_TOKEN_EXPIRE_MINUTES.
docker compose up -d postgres
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 5000
```

For the PostgreSQL container in `docker-compose.yml`, use the following local
database URL in `Backend/.env`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/medical_rag
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

When the page opens, the connection label reports whether `GET /health` can
reach both the API and its database. If it reports **Backend unavailable**,
resolve that before attempting sign-in or data uploads.

## Backend CORS

The backend accepts requests from the default frontend development URLs
`http://localhost:5173` and `http://127.0.0.1:5173`. To deploy the frontend at
another origin, set `CORS_ORIGINS` in `Backend/.env` to a comma-separated list:

```env
CORS_ORIGINS=https://medical.example.com
```

## Validation

With Node.js installed:

```bash
npm run build
```

Without Node.js, you can still smoke-test the page by serving it with Python and opening the browser URL above.

## Troubleshooting: page appears as plain text

If the browser shows the content as an unstyled list of text and links, the CSS file is not being loaded or the page was opened from the wrong location.

1. Stop any previous frontend server.
2. Start the server from inside the `Frontend` directory:

```bash
cd Frontend
python3 -m http.server 5173
```

3. Open the exact URL:

```text
http://localhost:5173/
```

4. Verify that the stylesheet is reachable:

```text
http://localhost:5173/src/styles.css
```

If that URL does not show CSS code, the server is not running from the `Frontend` directory. Restart it from the correct directory and hard refresh the page with