# Medical RAG Frontend

A dependency-free static frontend for the Medical RAG backend. It combines a modern medical landing page inspired by the reference image with the operational screens needed by the RAG system.

## Features

- Hero section styled like a modern medical clinic website.
- Backend token connection field for authenticated FastAPI requests.
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

The UI defaults to `http://localhost:8000` for the FastAPI backend. To override it without rebuilding, set this before `src/main.js` runs:

```html
<script>window.MEDICAL_RAG_API_BASE_URL = 'http://localhost:8000';</script>
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