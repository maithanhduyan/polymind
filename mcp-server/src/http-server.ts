#!/usr/bin/env node

import http from 'http';
import url from 'url';
import { config } from './config.js';
import { BaseService } from './services/base.service.js';
import { TimeService } from './services/time.service.js';
import { PostgresService } from './services/postgres.service.js';

// Service Registry
class ServiceRegistry {
  private services: Map<string, BaseService> = new Map();

  async registerService(service: BaseService): Promise<void> {
    await service.initialize();
    this.services.set(service.name, service);
    console.log(`Service '${service.name}' registered successfully`);
  }

  getService(name: string): BaseService | undefined {
    return this.services.get(name);
  }

  getAllServices(): BaseService[] {
    return Array.from(this.services.values());
  }

  async cleanup(): Promise<void> {
    for (const service of this.services.values()) {
      await service.cleanup();
    }
    this.services.clear();
  }

  getServiceEndpoints() {
    const endpoints: any = {};
    for (const service of this.services.values()) {
      endpoints[service.name] = {
        version: service.version,
        description: service.description,
        endpoints: service.getEndpoints()
      };
    }
    return endpoints;
  }
}

const serviceRegistry = new ServiceRegistry();

// HTTP Server
function createHttpServer(): http.Server {
  const httpServer = http.createServer(async (req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('Content-Type', 'application/json');

    // Handle preflight requests
    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    try {
      const parsedUrl = url.parse(req.url || '', true);
      const pathname = parsedUrl.pathname || '';
      const query = parsedUrl.query;
      const method = req.method;

      // Root endpoint - service discovery
      if (pathname === '/') {
        res.writeHead(200);
        res.end(JSON.stringify({
          success: true,
          message: 'Multi-Service MCP Server',
          version: '1.0.0',
          services: serviceRegistry.getServiceEndpoints()
        }));
        return;
      }

      // Global health check
      if (pathname === '/health') {
        const healthChecks = await Promise.all(
          serviceRegistry.getAllServices().map(async service => {
            const health = await service.healthCheck();
            return { service: service.name, ...health };
          })
        );

        const allHealthy = healthChecks.every(check => check.success);
        res.writeHead(allHealthy ? 200 : 503);
        res.end(JSON.stringify({
          success: allHealthy,
          timestamp: new Date().toISOString(),
          services: healthChecks
        }));
        return;
      }

      // Route to specific services
      const pathParts = pathname.split('/').filter(part => part);
      if (pathParts.length === 0) {
        res.writeHead(404);
        res.end(JSON.stringify({ success: false, error: 'Endpoint not found' }));
        return;
      }

      const serviceName = pathParts[0];
      const service = serviceRegistry.getService(serviceName);

      if (!service) {
        res.writeHead(404);
        res.end(JSON.stringify({
          success: false,
          error: `Service '${serviceName}' not found`,
          available_services: Array.from(serviceRegistry.getAllServices().map(s => s.name))
        }));
        return;
      }

      // Handle service-specific routes
      await handleServiceRequest(service, req, res, pathParts.slice(1), query, method);

    } catch (error) {
      console.error('Server error:', error);
      res.writeHead(500);
      res.end(JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error'
      }));
    }
  });

  return httpServer;
}

// Handle requests for specific services
async function handleServiceRequest(
  service: BaseService,
  req: http.IncomingMessage,
  res: http.ServerResponse,
  pathParts: string[],
  query: any,
  method: string | undefined
) {
  if (service instanceof TimeService) {
    await handleTimeServiceRequest(service, req, res, pathParts, query, method);
  } else if (service instanceof PostgresService) {
    await handlePostgresServiceRequest(service, req, res, pathParts, query, method);
  } else {
    res.writeHead(404);
    res.end(JSON.stringify({ success: false, error: 'Service handler not implemented' }));
  }
}

// Time Service Request Handler
async function handleTimeServiceRequest(
  service: TimeService,
  req: http.IncomingMessage,
  res: http.ServerResponse,
  pathParts: string[],
  query: any,
  method: string | undefined
) {
  const endpoint = pathParts[0];

  switch (endpoint) {
    case 'current':
    case undefined: // /time
      const format = (query.format as string) || 'iso';
      const timezone = (query.timezone as string) || 'local';
      const time = service.getCurrentTime(format, timezone);

      res.writeHead(200);
      res.end(JSON.stringify({
        success: true,
        data: {
          time,
          format,
          timezone: timezone !== 'local' ? timezone : 'local'
        }
      }));
      break;

    case 'info':
      const includeTimezone = query.include_timezone !== 'false';
      const timeInfo = service.getTimeInfo(includeTimezone);

      res.writeHead(200);
      res.end(JSON.stringify({
        success: true,
        data: timeInfo
      }));
      break;

    default:
      res.writeHead(404);
      res.end(JSON.stringify({
        success: false,
        error: `Time service endpoint '${endpoint}' not found`
      }));
  }
}

// PostgreSQL Service Request Handler
async function handlePostgresServiceRequest(
  service: PostgresService,
  req: http.IncomingMessage,
  res: http.ServerResponse,
  pathParts: string[],
  query: any,
  method: string | undefined
) {
  const endpoint = pathParts[0];

  switch (endpoint) {
    case 'status':
      const status = await service.getConnectionStatus();
      res.writeHead(status.success ? 200 : 500);
      res.end(JSON.stringify(status));
      break;

    case 'tables':
      const schema = (query.schema as string) || 'public';
      const tables = await service.getTables(schema);
      res.writeHead(tables.success ? 200 : 500);
      res.end(JSON.stringify(tables));
      break;

    case 'table':
      if (pathParts.length < 2) {
        res.writeHead(400);
        res.end(JSON.stringify({ success: false, error: 'Table name required' }));
        return;
      }

      const tableName = pathParts[1];
      const action = pathParts[2];

      if (action === 'schema') {
        const schema = await service.getTableSchema(tableName);
        res.writeHead(schema.success ? 200 : 500);
        res.end(JSON.stringify(schema));
      } else if (action === 'data') {
        const limit = parseInt(query.limit as string) || 100;
        const offset = parseInt(query.offset as string) || 0;
        const data = await service.getTableData(tableName, limit, offset);
        res.writeHead(data.success ? 200 : 500);
        res.end(JSON.stringify(data));
      } else {
        res.writeHead(404);
        res.end(JSON.stringify({ success: false, error: 'Table action not found' }));
      }
      break;

    case 'query':
      if (method !== 'POST') {
        res.writeHead(405);
        res.end(JSON.stringify({ success: false, error: 'Method not allowed' }));
        return;
      }

      let body = '';
      req.on('data', chunk => {
        body += chunk.toString();
      });

      req.on('end', async () => {
        try {
          const queryRequest = JSON.parse(body);
          const result = await service.executeQuery(queryRequest);
          res.writeHead(result.success ? 200 : 500);
          res.end(JSON.stringify(result));
        } catch (error) {
          res.writeHead(400);
          res.end(JSON.stringify({
            success: false,
            error: 'Invalid JSON in request body'
          }));
        }
      });
      break;

    default:
      res.writeHead(404);
      res.end(JSON.stringify({
        success: false,
        error: `PostgreSQL service endpoint '${endpoint}' not found`
      }));
  }
}

// Initialize services and start server
async function main() {
  try {
    console.log('Initializing services...');

    // Register Time service (always works)
    await serviceRegistry.registerService(new TimeService());

    // Try to register PostgreSQL service (optional)
    try {
      await serviceRegistry.registerService(new PostgresService());
      console.log('PostgreSQL service enabled');
    } catch (error) {
      console.warn('PostgreSQL service disabled:', error instanceof Error ? error.message : 'Unknown error');
      console.log('Server will continue with Time service only');
    }

    console.log('Services initialization completed');

    // Start HTTP server
    const httpServer = createHttpServer();

    httpServer.listen(config.server.port, config.server.host, () => {
      console.log(`Multi-Service MCP Server running on http://${config.server.host}:${config.server.port}`);
      console.log('\nAvailable services:');

      const endpoints = serviceRegistry.getServiceEndpoints();
      for (const [serviceName, serviceInfo] of Object.entries(endpoints)) {
        console.log(`\n📋 ${serviceName.toUpperCase()} Service (v${(serviceInfo as any).version}):`);
        console.log(`   ${(serviceInfo as any).description}`);
        for (const endpoint of (serviceInfo as any).endpoints) {
          console.log(`   ${endpoint.method} /${serviceName}${endpoint.path.replace(/^\//, '/').replace(/^\/\//, '/')} - ${endpoint.description}`);
        }
      }

      console.log(`\n🔍 Service Discovery: GET http://${config.server.host}:${config.server.port}/`);
      console.log(`❤️  Global Health Check: GET http://${config.server.host}:${config.server.port}/health`);
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      console.log('\n🛑 Shutting down server...');
      await serviceRegistry.cleanup();
      httpServer.close(() => {
        console.log('Server closed');
        process.exit(0);
      });
    });

  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
