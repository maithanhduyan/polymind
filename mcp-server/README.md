# Multi-Service MCP Server

A comprehensive HTTP server providing multiple services including time management and PostgreSQL database operations.

## Services

### 🕒 Time Service
- Get current system time in various formats
- Retrieve detailed time information
- Support for multiple timezones

### 🗄️ PostgreSQL Service  
- Database connection management
- Execute SQL queries
- Browse tables and schemas
- Data retrieval with pagination

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Environment Setup
Copy `.env.example` to `.env` and configure your settings:
```bash
cp .env.example .env
```

### 3. Build and Start
```bash
npm run build
npm start
```

## API Endpoints

### Service Discovery
- `GET /` - List all available services and endpoints
- `GET /health` - Global health check for all services

### Time Service
- `GET /time` - Get current time
  - Query params: `format` (iso, locale, unix, utc, detailed), `timezone`
- `GET /time/info` - Get detailed time information
  - Query params: `include_timezone` (boolean)

### PostgreSQL Service
- `GET /postgres/status` - Database connection status
- `GET /postgres/tables` - List all tables
  - Query params: `schema` (default: public)
- `GET /postgres/table/{tableName}/schema` - Get table schema
- `GET /postgres/table/{tableName}/data` - Get table data
  - Query params: `limit` (default: 100), `offset` (default: 0)
- `POST /postgres/query` - Execute SQL query
  - Body: `{ "query": "SELECT * FROM users", "params": [] }`

## Examples

### Time Service
```bash
# Get current time in detailed format
curl "http://localhost:3000/time?format=detailed&timezone=Asia/Ho_Chi_Minh"

# Get time information
curl "http://localhost:3000/time/info"
```

### PostgreSQL Service
```bash
# Get database status
curl "http://localhost:3000/postgres/status"

# List tables
curl "http://localhost:3000/postgres/tables"

# Get table schema
curl "http://localhost:3000/postgres/table/users/schema"

# Execute custom query
curl -X POST "http://localhost:3000/postgres/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) FROM users WHERE active = $1", "params": [true]}'
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | 3000 |
| `HOST` | Server host | 0.0.0.0 |
| `DB_HOST` | PostgreSQL host | localhost |
| `DB_PORT` | PostgreSQL port | 5432 |
| `DB_NAME` | Database name | mcp_server |
| `DB_USER` | Database user | postgres |
| `DB_PASSWORD` | Database password | password |
| `DB_SSL` | Enable SSL | false |

## Development

### Build
```bash
npm run build
```

### Watch Mode
```bash
npm run dev
```

## Architecture

The server uses a service registry pattern where each service:
- Extends `BaseService` abstract class
- Implements initialization, cleanup, and health checks
- Provides endpoint definitions
- Handles service-specific routing

Services are automatically registered and managed by the `ServiceRegistry` class.

## Error Handling

All responses follow a consistent format:
```json
{
  "success": boolean,
  "data": any,
  "error": string,
  "timestamp": string
}
```

## Adding New Services

1. Create a new service class extending `BaseService`
2. Implement required methods: `getEndpoints()`, `initialize()`, `cleanup()`, `healthCheck()`
3. Add service registration in `main()` function
4. Add request handler in `handleServiceRequest()` function
