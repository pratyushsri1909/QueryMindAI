/**
 * QueryMind AI — Frontend API Client Service
 *
 * Dedicated service module handling communication with the FastAPI backend.
 * Uses native Fetch API with robust error handling and response normalization.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Check backend service availability via GET /health
 * @returns {Promise<{ healthy: boolean, status?: string, error?: string }>}
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return { healthy: false, error: `HTTP ${response.status} from health check` };
    }

    const data = await response.json();
    return { healthy: data.status === 'healthy', status: data.status };
  } catch (err) {
    return {
      healthy: false,
      error: err instanceof Error ? err.message : 'Backend unreachable',
    };
  }
}

/**
 * Submit natural language query to the backend query pipeline: POST /api/v1/query
 *
 * @param {string} query - The natural language database query.
 * @returns {Promise<object>} The parsed QueryResponse payload.
 * @throws {Error} Descriptive error message with status code and server detail.
 */
export async function executeQuery(query) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
  } catch (networkError) {
    throw new Error(
      `Cannot connect to backend server at ${API_BASE_URL}. Ensure the FastAPI server is running.`
    );
  }

  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(
      `Invalid JSON response from server (HTTP ${response.status}).`
    );
  }

  if (!response.ok) {
    // Handle FastAPI 422 Unprocessable Entity or other error codes
    if (response.status === 422 && data.detail) {
      if (Array.isArray(data.detail)) {
        const msg = data.detail.map((d) => d.msg || d.message).join('; ');
        throw new Error(`Validation Error: ${msg}`);
      }
      throw new Error(`Validation Error: ${data.detail}`);
    }
    throw new Error(data.detail || data.message || `Request failed with HTTP ${response.status}`);
  }

  return data;
}

export default {
  checkBackendHealth,
  executeQuery,
};
