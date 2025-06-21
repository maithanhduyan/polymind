export interface ServiceEndpoint {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  description: string;
  parameters?: Record<string, any>;
}

export interface ServiceResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
}

export abstract class BaseService {
  abstract name: string;
  abstract version: string;
  abstract description: string;

  // Get all available endpoints for this service
  abstract getEndpoints(): ServiceEndpoint[];

  // Initialize service (connect to databases, etc.)
  abstract initialize(): Promise<void>;

  // Cleanup resources
  abstract cleanup(): Promise<void>;

  // Health check
  abstract healthCheck(): Promise<ServiceResponse<any>>;

  // Create standard response format
  protected createResponse<T>(success: boolean, data?: T, error?: string): ServiceResponse<T> {
    return {
      success,
      data,
      error,
      timestamp: new Date().toISOString()
    };
  }
}
