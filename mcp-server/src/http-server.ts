#!/usr/bin/env node

import http from 'http';
import url from 'url';

// Time utilities
class TimeService {
  static getCurrentTime(format: string = "iso", timezone: string = "local"): string {
    const now = new Date();
    
    switch (format) {
      case "iso":
        return now.toISOString();
      case "locale":
        if (timezone === "local") {
          return now.toLocaleString();
        } else {
          return now.toLocaleString("en-US", { timeZone: timezone });
        }
      case "unix":
        return Math.floor(now.getTime() / 1000).toString();
      case "utc":
        return now.toUTCString();
      case "detailed":
        const options: Intl.DateTimeFormatOptions = {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          timeZoneName: "short"
        };
        if (timezone !== "local") {
          options.timeZone = timezone;
        }
        return now.toLocaleString("en-US", options);
      default:
        return now.toISOString();
    }
  }

  static getTimeInfo(includeTimezone: boolean = true) {
    const now = new Date();
    
    return {
      current_time: now.toISOString(),
      local_time: now.toLocaleString(),
      unix_timestamp: Math.floor(now.getTime() / 1000),
      day_of_week: now.toLocaleDateString("en-US", { weekday: "long" }),
      day_of_month: now.getDate(),
      month: now.toLocaleDateString("en-US", { month: "long" }),
      year: now.getFullYear(),
      hour: now.getHours(),
      minute: now.getMinutes(),
      second: now.getSeconds(),
      millisecond: now.getMilliseconds(),
      ...(includeTimezone && {
        timezone_offset: now.getTimezoneOffset(),
        timezone_name: Intl.DateTimeFormat().resolvedOptions().timeZone,
      }),
    };
  }
}

// HTTP Serverfor external access
function createHttpServer() {
  const httpServer = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url || '', true);
    const pathname = parsedUrl.pathname;
    const query = parsedUrl.query;

    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    res.setHeader('Content-Type', 'application/json');

    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    try {
      switch (pathname) {
        case '/time':
          const format = (query.format as string) || 'iso';
          const timezone = (query.timezone as string) || 'local';
          const time = TimeService.getCurrentTime(format, timezone);
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

        case '/time-info':
          const includeTimezone = query.include_timezone !== 'false';
          const timeInfo = TimeService.getTimeInfo(includeTimezone);
          res.writeHead(200);
          res.end(JSON.stringify({
            success: true,
            data: timeInfo
          }));
          break;

        case '/health':
          res.writeHead(200);
          res.end(JSON.stringify({
            success: true,
            status: 'healthy',
            timestamp: new Date().toISOString()
          }));
          break;

        case '/':
          res.writeHead(200);
          res.end(JSON.stringify({
            success: true,
            message: 'System Time MCP Server',
            version: '1.0.0',
            endpoints: {
              '/time': 'Get current time (query: format, timezone)',
              '/time-info': 'Get detailed time information (query: include_timezone)',
              '/health': 'Health check'
            }
          }));
          break;

        default:
          res.writeHead(404);
          res.end(JSON.stringify({
            success: false,
            error: 'Endpoint not found'
          }));
      }
    } catch (error) {
      res.writeHead(500);
      res.end(JSON.stringify({
        success: false,
        error: error instanceof Error ? error.message : 'Internal server error'
      }));
    }
  });

  return httpServer;
}

// Main function
async function main() {
  // Run as HTTP server only
  const port = parseInt(process.env.PORT || '3000');
  const httpServer = createHttpServer();
  
  httpServer.listen(port, '0.0.0.0', () => {
    console.log(`System Time HTTP Server running on port ${port}`);
    console.log('Available endpoints:');
    console.log(`  GET http://localhost:${port}/time?format=iso&timezone=UTC`);
    console.log(`  GET http://localhost:${port}/time-info`);
    console.log(`  GET http://localhost:${port}/health`);
  });
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});
