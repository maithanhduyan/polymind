import { BaseService, ServiceEndpoint, ServiceResponse } from './base.service.js';

export class TimeService extends BaseService {
  name = 'time';
  version = '1.0.0';
  description = 'System time management service';

  getEndpoints(): ServiceEndpoint[] {
    return [
      {
        path: '/time',
        method: 'GET',
        description: 'Get current system time',
        parameters: {
          format: 'string (iso, locale, unix, utc, detailed)',
          timezone: 'string (timezone name or "local")'
        }
      },
      {
        path: '/time-info',
        method: 'GET',
        description: 'Get detailed time information',
        parameters: {
          include_timezone: 'boolean'
        }
      }
    ];
  }

  async initialize(): Promise<void> {
    // No initialization needed for time service
  }

  async cleanup(): Promise<void> {
    // No cleanup needed for time service
  }

  async healthCheck(): Promise<ServiceResponse<any>> {
    try {
      const now = new Date();
      return this.createResponse(true, {
        service: this.name,
        status: 'healthy',
        current_time: now.toISOString()
      });
    } catch (error) {
      return this.createResponse(false, null, 'Time service health check failed');
    }
  }

  getCurrentTime(format: string = "iso", timezone: string = "local"): string {
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

  getTimeInfo(includeTimezone: boolean = true) {
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
