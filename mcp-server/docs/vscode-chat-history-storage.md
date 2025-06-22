# VS Code Copilot Chat History Storage

## Tổng quan
VS Code Copilot Chat lưu trữ lịch sử cuộc trò chuyện trong các file JSON được lưu cục bộ trên máy tính của người dùng. Dữ liệu này không được đồng bộ hóa với cloud mà chỉ tồn tại trên máy cục bộ.

## Vị trí lưu trữ

### Windows
```
%APPDATA%\Code\User\workspaceStorage\[workspace-hash]\
```

Ví dụ cụ thể:
```
C:\Users\[username]\AppData\Roaming\Code\User\workspaceStorage\8b4b244c99eded79a96acc9cccbe38ca\
```

### Cấu trúc thư mục
```
workspaceStorage/
├── [workspace-hash]/
│   ├── chatSessions/           # Lịch sử chat chính
│   ├── chatEditingSessions/    # Lịch sử chat editing
│   ├── state.vscdb            # Database trạng thái VS Code
│   ├── state.vscdb.backup     # Backup database
│   └── workspace.json         # Metadata workspace
```

## Cách xác định Workspace Hash

Workspace hash được tạo từ SHA1 của đường dẫn workspace (chữ thường):

```powershell
$workspacePath = "c:\Users\tiach\Downloads\polymind"
Add-Type -AssemblyName System.Security
$hasher = [System.Security.Cryptography.SHA1]::Create()
$bytes = [System.Text.Encoding]::UTF8.GetBytes($workspacePath.ToLower())
$hash = $hasher.ComputeHash($bytes)
[System.BitConverter]::ToString($hash) -replace '-', '' | % {$_.ToLower()}
```

## Định dạng Chat Sessions

### Cấu trúc file JSON
Mỗi cuộc trò chuyện được lưu trong file JSON riêng biệt với tên là UUID:

```
chatSessions/
├── 188197c8-2a31-46f0-ba2e-23ee11b543e7.json
├── 227e098a-158f-4d35-be36-dcce4302a1a6.json
└── ...
```

### Nội dung file JSON
```json
{
  "version": 3,
  "requesterUsername": "maithanhduyan",
  "requesterAvatarIconUri": {
    "$mid": 1,
    "path": "/u/7606112",
    "scheme": "https",
    "authority": "avatars.githubusercontent.com",
    "query": "v=4"
  },
  "responderUsername": "GitHub Copilot",
  "responderAvatarIconUri": {
    "id": "copilot"
  },
  "initialLocation": "panel",
  "requests": [
    {
      "requestId": "request_c4665702-d5ff-4cd4-8be1-d4ae14e69972",
      "message": {
        "parts": [
          {
            "range": {
              "start": 0,
              "endExclusive": 80
            },
            "editorRange": {
              "startLineNumber": 1,
              "startColumn": 1,
              "endLineNumber": 3,
              "endColumn": 25
            },
            "text": "Nội dung tin nhắn từ user",
            "kind": "text"
          }
        ]
      },
      "response": {
        "responseId": "response_xyz",
        "text": "Nội dung phản hồi từ Copilot",
        "timestamp": "2025-06-22T08:52:28.000Z"
      }
    }
  ]
}
```

## Thống kê Chat History

### Kích thước file
- File chat nhỏ: ~100KB - 500KB
- File chat trung bình: 1MB - 5MB  
- File chat lớn: 10MB - 40MB+

### Số lượng
- Mỗi workspace có thể có hàng chục đến hàng trăm file chat
- Không có giới hạn tự động xóa

## Các loại Chat Session

### 1. chatSessions/
- Lịch sử chat thông thường trong VS Code Chat panel
- Các cuộc trò chuyện về code, debug, giải thích

### 2. chatEditingSessions/
- Lịch sử chat editing (inline chat)
- Các cuộc trò chuyện về chỉnh sửa code trực tiếp

## Bảo mật và Quyền riêng tư

### Lưu trữ cục bộ
- Tất cả dữ liệu chat được lưu cục bộ
- Không được đồng bộ với GitHub/Microsoft cloud
- Chỉ có thể truy cập với quyền user trên máy tính

### Thông tin nhạy cảm
- Chat history có thể chứa:
  - Source code
  - API keys (nếu user paste vào)
  - Thông tin business logic
  - Database schemas

### Recommendations
1. **Backup định kỳ** nếu cần giữ lại lịch sử
2. **Xóa chat history** trước khi chuyển máy
3. **Không share** thư mục workspaceStorage
4. **Encrypt disk** để bảo vệ dữ liệu

## Quản lý Chat History

### Tìm workspace hiện tại
```powershell
# Tìm workspace storage gần đây nhất có chatSessions
Get-ChildItem "$env:APPDATA\Code\User\workspaceStorage" | 
  Sort-Object LastWriteTime -Descending | 
  Where-Object { Test-Path "$($_.FullName)\chatSessions" } |
  Select-Object -First 5
```

### Thống kê chat sessions
```powershell
# Đếm số file chat và tổng kích thước
$chatDir = "$env:APPDATA\Code\User\workspaceStorage\[hash]\chatSessions"
$files = Get-ChildItem $chatDir -File
Write-Host "Số file chat: $($files.Count)"
Write-Host "Tổng kích thước: $([math]::Round(($files | Measure-Object Length -Sum).Sum / 1MB, 2)) MB"
```

### Dọn dẹp chat history
```powershell
# Xóa chat cũ hơn 30 ngày
$cutoffDate = (Get-Date).AddDays(-30)
Get-ChildItem "$env:APPDATA\Code\User\workspaceStorage\*\chatSessions" -File |
  Where-Object { $_.LastWriteTime -lt $cutoffDate } |
  Remove-Item -Confirm
```

## Troubleshooting

### Chat history bị mất
- Kiểm tra workspace hash có đúng không
- Xem file backup trong state.vscdb.backup
- Chat history có thể bị xóa khi reset VS Code settings

### Performance issues
- Quá nhiều file chat lớn có thể làm chậm VS Code
- Định kỳ dọn dẹp chat cũ
- Kiểm tra dung lượng disk

### Migration
- Khi chuyển máy, copy toàn bộ thư mục workspaceStorage
- Đảm bảo workspace path giống nhau để hash khớp
- Hoặc export/import chat history quan trọng

## Tích hợp với hệ thống khác

### Backup to Database
```python
import json
import sqlite3
from pathlib import Path

def backup_chat_history(workspace_storage_path, db_path):
    """Backup VS Code chat history to SQLite database"""
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY,
            session_id TEXT,
            workspace_hash TEXT,
            timestamp TEXT,
            content TEXT,
            file_size INTEGER
        )
    ''')
    
    for chat_file in Path(workspace_storage_path).glob('*/chatSessions/*.json'):
        with open(chat_file, 'r', encoding='utf-8') as f:
            content = f.read()
            conn.execute('''
                INSERT INTO chat_history 
                (session_id, workspace_hash, timestamp, content, file_size)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                chat_file.stem,
                chat_file.parent.parent.name,
                chat_file.stat().st_mtime,
                content,
                len(content)
            ))
    
    conn.commit()
    conn.close()
```

### Analytics
```python
def analyze_chat_patterns(workspace_storage_path):
    """Phân tích patterns trong chat history"""
    stats = {
        'total_sessions': 0,
        'total_size': 0,
        'topics': {},
        'time_distribution': {}
    }
    
    for chat_file in Path(workspace_storage_path).glob('*/chatSessions/*.json'):
        stats['total_sessions'] += 1
        stats['total_size'] += chat_file.stat().st_size
        
        with open(chat_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Analyze topics, time patterns, etc.
    
    return stats
```

## Kết luận

VS Code Copilot Chat history là một nguồn dữ liệu phong phú về:
- Cách developer tương tác với AI
- Patterns của các câu hỏi thường gặp
- Code snippets và solutions
- Debugging processes

Việc hiểu rõ cách lưu trữ và quản lý chat history giúp:
- Backup dữ liệu quan trọng
- Tối ưu performance
- Bảo vệ thông tin nhạy cảm
- Tích hợp với hệ thống khác
