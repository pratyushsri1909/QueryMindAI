/**
 * QueryMind AI — Frontend API Client Service
 *
 * Dedicated service module handling communication with the FastAPI backend.
 * Uses native Fetch API with robust error handling and response normalization.
 */

const RAW_API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_BASE_URL = RAW_API_BASE_URL.replace(/\/+$/, '');

async function _extractErrorMessage(response, fallbackMessage) {
  try {
    const data = await response.json();
    if (typeof data?.detail === 'string') return data.detail;
    if (data?.detail?.message) return data.detail.message;
    if (data?.message) return data.message;
  } catch {
    // Ignore non-JSON error bodies
  }
  return `${fallbackMessage} (HTTP ${response.status})`;
}

/**
 * Check backend service availability and database connectivity via GET /health?include_db=true
 * @returns {Promise<{ healthy: boolean, status?: string, database?: string, mode?: string, databaseName?: string|null, error?: string }>}
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
      return {
        healthy: false,
        status: 'offline',
        database: 'disconnected',
        mode: 'unknown',
        databaseName: null,
        error: `HTTP ${response.status} from health check`,
      };
    }

    const data = await response.json();
    return {
      healthy: data.status === 'healthy',
      status: data.status,
      database: data.database || 'disconnected',
      mode: data.mode || 'mock',
      databaseName: data.database_name || null,
    };
  } catch (err) {
    return {
      healthy: false,
      status: 'offline',
      database: 'disconnected',
      mode: 'unknown',
      databaseName: null,
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
    throw new Error(await _extractErrorMessage(response, 'Database health check failed'));
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
    throw new Error(await _extractErrorMessage(response, 'Failed to fetch student records from database'));
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
      const detailMessage =
        typeof data.detail === 'string'
          ? data.detail
          : data.detail.message || JSON.stringify(data.detail);
      throw new Error(`Validation Error: ${detailMessage}`);
    }
    const errorDetail =
      typeof data.detail === 'string' ? data.detail : data.detail?.message;
    throw new Error(errorDetail || data.message || `Request failed with HTTP ${response.status}`);
  }

  return data;
}

export default {
  checkBackendHealth,
  getDatabaseHealth,
  getDatabaseStudents,
  executeQuery,
};
