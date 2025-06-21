import { Pool, PoolClient, QueryResult } from 'pg';
import { BaseService, ServiceEndpoint, ServiceResponse } from './base.service.js';
import { config } from '../config.js';

export interface TableInfo {
  table_name: string;
  table_schema: string;
  table_type: string;
}

export interface ColumnInfo {
  column_name: string;
  data_type: string;
  is_nullable: string;
  column_default: string | null;
}

export interface QueryRequest {
  query: string;
  params?: any[];
}

export class PostgresService extends BaseService {
  name = 'postgres';
  version = '1.0.0';
  description = 'PostgreSQL database management service';

  private pool: Pool | null = null;

  getEndpoints(): ServiceEndpoint[] {
    return [
      {
        path: '/postgres/status',
        method: 'GET',
        description: 'Get PostgreSQL connection status'
      },
      {
        path: '/postgres/tables',
        method: 'GET',
        description: 'List all tables in the database',
        parameters: {
          schema: 'string (optional, default: public)'
        }
      },
      {
        path: '/postgres/table/:tableName/schema',
        method: 'GET',
        description: 'Get table schema information'
      },
      {
        path: '/postgres/query',
        method: 'POST',
        description: 'Execute a SQL query',
        parameters: {
          query: 'string (SQL query)',
          params: 'array (optional query parameters)'
        }
      },
      {
        path: '/postgres/table/:tableName/data',
        method: 'GET',
        description: 'Get table data with pagination',
        parameters: {
          limit: 'number (default: 100)',
          offset: 'number (default: 0)'
        }
      }
    ];
  }

  async initialize(): Promise<void> {
    try {
      this.pool = new Pool(config.database);

      // Test connection
      const client = await this.pool.connect();
      await client.query('SELECT NOW()');
      client.release();

      console.log('PostgreSQL service initialized successfully');
    } catch (error) {
      console.error('Failed to initialize PostgreSQL service:', error);
      throw error;
    }
  }

  async cleanup(): Promise<void> {
    if (this.pool) {
      await this.pool.end();
      this.pool = null;
    }
  }

  async healthCheck(): Promise<ServiceResponse<any>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, null, 'PostgreSQL pool not initialized');
      }

      const client = await this.pool.connect();
      const result = await client.query('SELECT NOW() as current_time, version() as version');
      client.release();

      return this.createResponse(true, {
        service: this.name,
        status: 'healthy',
        database_time: result.rows[0].current_time,
        version: result.rows[0].version
      });
    } catch (error) {
      return this.createResponse(false, null, `PostgreSQL health check failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getConnectionStatus(): Promise<ServiceResponse<any>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, null, 'PostgreSQL pool not initialized');
      }

      return this.createResponse(true, {
        total_connections: this.pool.totalCount,
        idle_connections: this.pool.idleCount,
        waiting_connections: this.pool.waitingCount,
        database_config: {
          host: config.database.host,
          port: config.database.port,
          database: config.database.database,
          user: config.database.user
        }
      });
    } catch (error) {
      return this.createResponse(false, null, `Failed to get connection status: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  async getTables(schema: string = 'public'): Promise<ServiceResponse<TableInfo[]>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, [], 'PostgreSQL pool not initialized');
      }

      const query = `
        SELECT table_name, table_schema, table_type 
        FROM information_schema.tables 
        WHERE table_schema = $1
        ORDER BY table_name
      `;

      const result = await this.pool.query(query, [schema]);
      return this.createResponse(true, result.rows);
    } catch (error) {
      return this.createResponse(false, [], `Failed to get tables: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
  async getTableSchema(tableName: string): Promise<ServiceResponse<ColumnInfo[]>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, [], 'PostgreSQL pool not initialized');
      }

      const query = `
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
      `;

      const result = await this.pool.query(query, [tableName]);
      return this.createResponse(true, result.rows);
    } catch (error) {
      return this.createResponse(false, [], `Failed to get table schema: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async executeQuery(queryRequest: QueryRequest): Promise<ServiceResponse<any>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, null, 'PostgreSQL pool not initialized');
      }

      const result = await this.pool.query(queryRequest.query, queryRequest.params);

      return this.createResponse(true, {
        rows: result.rows,
        row_count: result.rowCount,
        command: result.command,
        fields: result.fields?.map(field => ({
          name: field.name,
          dataTypeID: field.dataTypeID
        }))
      });
    } catch (error) {
      return this.createResponse(false, null, `Query execution failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async getTableData(tableName: string, limit: number = 100, offset: number = 0): Promise<ServiceResponse<any>> {
    try {
      if (!this.pool) {
        return this.createResponse(false, null, 'PostgreSQL pool not initialized');
      }

      // Validate table name to prevent SQL injection
      const tableCheckQuery = `
        SELECT table_name FROM information_schema.tables 
        WHERE table_name = $1 AND table_schema = 'public'
      `;
      const tableCheck = await this.pool.query(tableCheckQuery, [tableName]);

      if (tableCheck.rows.length === 0) {
        return this.createResponse(false, null, `Table '${tableName}' not found`);
      }

      const query = `SELECT * FROM "${tableName}" LIMIT $1 OFFSET $2`;
      const result = await this.pool.query(query, [limit, offset]);

      return this.createResponse(true, {
        table_name: tableName,
        rows: result.rows,
        row_count: result.rowCount,
        limit,
        offset
      });
    } catch (error) {
      return this.createResponse(false, null, `Failed to get table data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }
}
