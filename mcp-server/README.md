# System Time MCP Server

Một MCP (Model Context Protocol) server đơn giản để lấy thời gian hệ thống với nhiều định dạng khác nhau.

## Tính năng

- Lấy thời gian hiện tại theo nhiều định dạng (ISO, locale, Unix timestamp, UTC, detailed)
- Hỗ trợ múi giờ khác nhau
- Cung cấp thông tin chi tiết về thời gian (ngày trong tuần, tháng, năm, v.v.)

## Cài đặt và Sử dụng

### 1. Build MCP Server

```powershell
# Chạy script build
.\build.ps1
```

Hoặc build thủ công:

```powershell
cd mcp-server
npm install
npm run build
```

### 2. Cấu hình VS Code

MCP server đã được cấu hình trong `.vscode/settings.json`:

```json
{
  "chat.mcp.enabled": true,
  "chat.mcp.servers": {
    "system-time": {
      "command": "node",
      "args": ["c:\\Users\\tiach\\Downloads\\polymind\\mcp-server\\dist\\index.js"],
      "description": "System time MCP server - provides current system time in various formats"
    }
  }
}
```

### 3. Sử dụng trong GitHub Copilot Chat

Sau khi build và cấu hình, bạn có thể sử dụng các tools sau trong GitHub Copilot Chat:

#### `get_current_time`
Lấy thời gian hiện tại với định dạng chỉ định:

- **format**: `iso`, `locale`, `unix`, `utc`, `detailed`
- **timezone**: Múi giờ (ví dụ: 'Asia/Ho_Chi_Minh', 'UTC')

#### `get_time_info`
Lấy thông tin chi tiết về thời gian hiện tại:

- **include_timezone**: Có bao gồm thông tin múi giờ không (mặc định: true)

## Ví dụ sử dụng

Trong GitHub Copilot Chat, bạn có thể hỏi:

- "Thời gian hiện tại là gì?"
- "Cho tôi thời gian theo múi giờ Việt Nam"
- "Unix timestamp hiện tại là bao nhiêu?"
- "Thông tin chi tiết về thời gian hiện tại"

## Cấu trúc dự án

```
mcp-server/
├── src/
│   └── index.ts          # MCP server implementation
├── dist/                 # Compiled JavaScript
├── package.json          # Node.js dependencies
├── tsconfig.json         # TypeScript configuration
├── build.ps1            # Build script
└── README.md            # Documentation
```

## Troubleshooting

1. **Lỗi build**: Đảm bảo Node.js và npm đã được cài đặt
2. **MCP server không hoạt động**: Kiểm tra đường dẫn trong settings.json
3. **Lỗi permission**: Chạy PowerShell với quyền Administrator nếu cần

## Development

Để phát triển thêm:

```powershell
# Watch mode
npm run dev

# Test server
node dist/index.js
```
