const API_BASE_URL = window.MEDICAL_RAG_API_BASE_URL || 'http://localhost:5000';

const elements = {
  token: document.querySelector('#token'),
  email: document.querySelector('#email'),
  password: document.querySelector('#password'),
  authForm: document.querySelector('#auth-form'),
  loginButton: document.querySelector('#login-button'),
  registerButton: document.querySelector('#register-button'),
  logoutButton: document.querySelector('#logout-button'),
  fileInput: document.querySelector('#medical-file'),
  fileName: document.querySelector('#file-name'),
  documentId: document.querySelector('#document-id'),
  query: document.querySelector('#question'),
  topK: document.querySelector('#top-k'),
  temperature: document.querySelector('#temperature'),
  uploadForm: document.querySelector('#upload-form'),
  questionForm: document.querySelector('#question-form'),
  uploadButton: document.querySelector('#upload-button'),
  processButton: document.querySelector('#process-button'),
  answerButton: document.querySelector('#answer-button'),
  statusBanner: document.querySelector('#status-banner'),
  answerTitle: document.querySelector('#answer-title'),
  answerText: document.querySelector('#answer-text'),
  scoreRow: document.querySelector('#score-row'),
  sourcesList: document.querySelector('#sources-list'),
  apiBaseLabel: document.querySelector('#api-base-label'),
};

elements.apiBaseLabel.textContent = `API base URL: ${API_BASE_URL}`;
elements.token.value = sessionStorage.getItem('medical-rag-token') || '';
updateAuthControls();


function authHeaders() {
  return elements.token.value.trim() ? { Authorization: `Bearer ${elements.token.value.trim()}` } : {};
}

async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch {
    throw new Error(`Cannot reach the backend at ${API_BASE_URL}. Start the API and verify its URL.`);
  }
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body.detail || `Request failed with status ${response.status}`);
  }
  return body;
}
async function checkBackendConnection() {
  try {
    await request('/health');
    elements.apiBaseLabel.textContent = `Backend connected: ${API_BASE_URL}`;
  } catch (error) {
    elements.apiBaseLabel.textContent = `Backend unavailable: ${API_BASE_URL}`;
    setStatus(error.message, 'error');
  }
}

function setStatus(message, type = 'success') {
  elements.statusBanner.hidden = !message;
  elements.statusBanner.textContent = message;
  elements.statusBanner.classList.toggle('error', type === 'error');
}

function setLoading(kind, active) {
  const map = {
    upload: [elements.uploadButton, 'Uploading...', 'Upload document'],
    process: [elements.processButton, 'Processing...', 'Process document'],
    answer: [elements.answerButton, 'Generating...', '💬 Generate answer'],
  };
  const [button, loadingText, readyText] = map[kind];
  button.disabled = active;
  button.textContent = active ? loadingText : readyText;
}
function updateAuthControls() {
  const isAuthenticated = Boolean(elements.token.value.trim());
  elements.logoutButton.hidden = !isAuthenticated;
  elements.loginButton.textContent = isAuthenticated ? 'Signed in' : 'Sign in';
  elements.loginButton.disabled = isAuthenticated;
  elements.registerButton.disabled = isAuthenticated;
}

async function authenticate(path) {
  const email = elements.email.value.trim();
  const password = elements.password.value;
  if (!email || !password) {
    setStatus('Enter your email and password first.', 'error');
    return;
  }

  const actionButton = path === '/auth/login' ? elements.loginButton : elements.registerButton;
  actionButton.disabled = true;
  setStatus('');
  try {
    if (path === '/auth/register') {
      await request(path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
    }
    const token = await request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    elements.token.value = token.access_token;
    sessionStorage.setItem('medical-rag-token', token.access_token);
    elements.password.value = '';
    updateAuthControls();
    setStatus(path === '/auth/register' ? 'Account created and signed in.' : 'Signed in successfully.');
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    if (!elements.token.value.trim()) {
      actionButton.disabled = false;
    }
  }
}

elements.authForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  await authenticate('/auth/login');
});

elements.registerButton.addEventListener('click', async () => {
  await authenticate('/auth/register');
});

elements.logoutButton.addEventListener('click', () => {
  elements.token.value = '';
  sessionStorage.removeItem('medical-rag-token');
  updateAuthControls();
  setStatus('Signed out.');
});

elements.token.addEventListener('input', () => {
  if (elements.token.value.trim()) {
    sessionStorage.setItem('medical-rag-token', elements.token.value.trim());
  } else {
    sessionStorage.removeItem('medical-rag-token');
  }
  updateAuthControls();
});

elements.fileInput.addEventListener('change', () => {
  elements.fileName.textContent = elements.fileInput.files?.[0]?.name || 'Choose guideline PDF';
});

elements.uploadForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const file = elements.fileInput.files?.[0];
  if (!file) {
    setStatus('Choose a medical PDF first.', 'error');
    return;
  }

  setLoading('upload', true);
  setStatus('');
  try {
    const formData = new FormData();
    formData.append('file', file);
    const data = await request('/documents/upload', {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    });
    elements.documentId.value = data.id;
    setStatus(`Uploaded ${data.file_name}. You can process it now.`);
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    setLoading('upload', false);
  }
});

elements.processButton.addEventListener('click', async () => {
  const documentId = elements.documentId.value.trim();
  if (!documentId) {
    setStatus('Upload a document or paste a document ID first.', 'error');
    return;
  }

  setLoading('process', true);
  setStatus('');
  try {
    const data = await request(`/documents/${documentId}/process`, {
      method: 'POST',
      headers: authHeaders(),
    });
    setStatus(`Processed ${data.chunk_count} chunks from ${data.page_count} pages.`);
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    setLoading('process', false);
  }
});

elements.questionForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const query = elements.query.value.trim();
  if (!query) {
    setStatus('Write a clinical question first.', 'error');
    return;
  }

  setLoading('answer', true);
  setStatus('');
  renderAnswer(null);
  try {
    const data = await request('/rag/answer', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeaders(),
      },
      body: JSON.stringify({
        query,
        top_k: Number(elements.topK.value),
        temperature: Number(elements.temperature.value),
      }),
    });
    renderAnswer(data);
  } catch (error) {
    setStatus(error.message, 'error');
  } finally {
    setLoading('answer', false);
  }
});

function renderAnswer(answer) {
  elements.answerTitle.textContent = answer ? 'Clinical response ready' : 'Your answer will appear here';
  elements.answerText.textContent = answer?.answer || 'Ask a question to see the response, retrieved chunks, sources, and evaluation details.';
  elements.scoreRow.innerHTML = '';
  Object.entries(answer?.evaluation || {}).forEach(([key, value]) => {
    const metric = document.createElement('span');
    metric.innerHTML = `${key}: <strong>${String(value)}</strong>`;
    elements.scoreRow.append(metric);
  });

  const chunks = answer?.retrieved_chunks || [];
  elements.sourcesList.innerHTML = '';
  if (!chunks.length) {
    elements.sourcesList.innerHTML = '<p class="muted">No evidence retrieved yet.</p>';
    return;
  }

  chunks.slice(0, 4).forEach((chunk) => {
    const source = document.createElement('article');
    source.className = 'source-item';
    source.innerHTML = `
      <strong>${escapeHtml(chunk.source || `Chunk ${chunk.chunk_id}`)}</strong>
      <p>${escapeHtml(chunk.text)}</p>
      <small>Score ${Number(chunk.score).toFixed(3)} · Pages ${chunk.page_start || '-'}-${chunk.page_end || '-'}</small>
    `;
    elements.sourcesList.append(source);
  });
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');
}