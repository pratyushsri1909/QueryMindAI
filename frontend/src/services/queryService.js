/**
 * QueryMind AI — Frontend API Client Service
 *
 * Dedicated service module handling communication with the FastAPI backend.
 * Uses native Fetch API with robust error handling and response normalization.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Check backend service availability and database connectivity via GET /health?include_db=true
 * @returns {Promise<{ healthy: boolean, status?: string, database?: string, error?: string }>}
 */
export async function checkBackendHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health?include_db=true`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      return { healthy: false, error: `HTTP ${response.status} from health check` };
    }

    const data = await response.json();
    return {
      healthy: data.status === 'healthy',
      status: data.status,
      database: data.database || 'disconnected',
    };
  } catch (err) {
    return {
      healthy: false,
      database: 'disconnected',
      error: err instanceof Error ? err.message : 'Backend unreachable',
    };
  }
}

/**
 * Check dedicated PostgreSQL health status via GET /api/v1/database/health
 * @returns {Promise<{ status: string, database: string, database_type: string }>}
 */
export async function getDatabaseHealth() {
  const response = await fetch(`${API_BASE_URL}/api/v1/database/health`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Database health check failed (HTTP ${response.status})`);
  }
  return response.json();
}

/**
 * Retrieve actual student records from PostgreSQL via GET /api/v1/database/students
 * @returns {Promise<{ success: boolean, source: string, count: number, data: Array }>}
 */
export async function getDatabaseStudents() {
  const response = await fetch(`${API_BASE_URL}/api/v1/database/students`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' },
  });
  if (!response.ok) {
    throw new Error(`Failed to fetch student records from database (HTTP ${response.status})`);
  }
  return response.json();
}

/**
 * Submit natural language query to the backend query pipeline: POST /api/v1/query
 *
 * @param {string} query - The natural language database query.
 * @param {string|null} executionMode - Optional override: 'mock' or 'database'.
 * @returns {Promise<object>} The parsed QueryResponse payload.
 * @throws {Error} Descriptive error message with status code and server detail.
 */
export async function executeQuery(query, executionMode = null) {
  let response;
  const payload = { query };
  if (executionMode) {
    payload.execution_mode = executionMode;
  }

  try {
    response = await fetch(`${API_BASE_URL}/api/v1/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(payload),
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
  getDatabaseHealth,
  getDatabaseStudents,
  executeQuery,
};
