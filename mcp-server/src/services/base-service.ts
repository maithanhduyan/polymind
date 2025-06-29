// Generated by Copilot

/**
 * Base Service Interface - Defines the contract for all MCP services
 * All services must implement this interface to be compatible with the server
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';

/**
 * Service Interface - Base contract for all services
 * Mọi service phải implement interface này để tương thích với server
 */
export interface Service {
  /** Namespace duy nhất cho service (e.g., 'time', 'calc') */
  readonly namespace: string;

  /** Tên hiển thị của service */
  readonly name: string;

  /** Phiên bản của service (semantic versioning) */
  readonly version: string;

  /** Mô tả chức năng của service */
  readonly description: string;

  /**
   * Liệt kê tất cả các tools có sẵn trong service
   * @returns Promise chứa danh sách tools
   */
  listTools(): Promise<{ tools: Tool[] }>;

  /**
   * Gọi một tool cụ thể trong service
   * @param name Tên của tool cần gọi
   * @param args Tham số đầu vào cho tool
   * @returns Promise chứa kết quả của tool
   */
  callTool(name: string, args: any): Promise<any>;
}
