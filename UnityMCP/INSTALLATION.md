# Unity MCP Server - Hướng Dẫn Cài Đặt

## Yêu Cầu Hệ Thống

- **Python**: 3.10 hoặc cao hơn (Yêu cầu cho MCP framework)
- **Unity Editor**: 2023.3.0f1 trở lên (khuyến nghị)
- **Hệ điều hành**: Windows, macOS, hoặc Linux
- **Claude Desktop**: Phiên bản mới nhất (cho tích hợp MCP client)

⚠️ **Quan trọng**: MCP (Model Context Protocol) framework yêu cầu Python 3.10 trở lên. Nếu bạn đang sử dụng Python 3.9 hoặc thấp hơn, bạn cần nâng cấp Python.

## Bước 1: Cài Đặt Dependencies

```bash
# Clone repository (nếu chưa có)
git clone https://github.com/anhnguyenvn/UnityMCP.git
cd UnityMCP

# Cài đặt Python dependencies
pip install -r requirements.txt
```

## Bước 2: Cấu Hình Unity Paths

### Cách 1: Sử dụng Environment Variables (Khuyến nghị)

Tạo file `.env` trong thư mục gốc:

```bash
# .env
UNITY_MCP_UNITY_EDITOR_PATH=/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity
UNITY_MCP_UNITY_PROJECT_PATH=/path/to/your/unity/project
UNITY_MCP_LOG_LEVEL=INFO
```

**Lưu ý đường dẫn theo platform:**
- **macOS**: `/Applications/Unity/Hub/Editor/[version]/Unity.app/Contents/MacOS/Unity`
- **Windows**: `C:\Program Files\Unity\Hub\Editor\[version]\Editor\Unity.exe`
- **Linux**: `/opt/Unity/Editor/Unity`

### Cách 2: Chỉnh sửa trực tiếp config.py

Mở file `config.py` và cập nhật:

```python
# Trong class MCPConfig
unity_editor_path: Optional[str] = Field(
    default="/path/to/your/Unity/Editor",  # Thay đổi đường dẫn này
    description="Path to Unity Editor executable"
)
unity_project_path: Optional[str] = Field(
    default="/path/to/your/unity/project",  # Thay đổi đường dẫn này
    description="Default Unity project path"
)
```

## Bước 3: Copy Unity Bridge Script

1. Mở Unity project của bạn
2. Copy file `unity_bridge.cs` vào thư mục `Assets/Scripts/` (tạo thư mục nếu chưa có)
3. Unity sẽ tự động compile script

## Bước 4: Cấu Hình Claude Desktop

### Tìm file cấu hình Claude Desktop:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### Thêm cấu hình MCP server:

```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "python",
      "args": ["/full/path/to/UnityMCP/main.py"],
      "env": {
        "UNITY_MCP_UNITY_EDITOR_PATH": "/Applications/Unity/Hub/Editor/2023.3.0f1/Unity.app/Contents/MacOS/Unity",
        "UNITY_MCP_UNITY_PROJECT_PATH": "/path/to/your/unity/project",
        "UNITY_MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

**Quan trọng**: Thay thế `/full/path/to/UnityMCP/main.py` bằng đường dẫn tuyệt đối đến file main.py

### Sử dụng file cấu hình mẫu:

```bash
# Copy file mẫu và chỉnh sửa
cp claude_desktop_config.example.json claude_desktop_config.json
# Chỉnh sửa đường dẫn trong file này
```

## Bước 5: Chạy và Test Server

### Chạy server standalone (để test):

```bash
# Chạy server với cấu hình mặc định
python main.py

# Chạy với tham số tùy chỉnh
python main.py --unity-editor "/path/to/Unity" --project "/path/to/project" --log-level DEBUG

# Chỉ validate cấu hình
python main.py --validate-only
```

### Test với Claude Desktop:

1. Khởi động lại Claude Desktop
2. Tạo conversation mới
3. Thử các lệnh Unity MCP:
   - "Scan Unity project structure"
   - "Build Unity project"
   - "Run Unity tests"

## Troubleshooting

### Lỗi Python Version
**Lỗi**: `ModuleNotFoundError: No module named 'mcp'`

**Nguyên nhân**: Python version thấp hơn 3.10

**Giải pháp**:
1. Kiểm tra Python version:
   ```bash
   python --version
   python3 --version
   ```

2. Nâng cấp Python (macOS với Homebrew):
   ```bash
   brew install python@3.11
   ```

3. Hoặc sử dụng pyenv:
   ```bash
   pyenv install 3.11.0
   pyenv global 3.11.0
   ```

### Lỗi thường gặp:

1. **"Unity Editor not found"**:
   - Kiểm tra đường dẫn Unity Editor trong cấu hình
   - Đảm bảo Unity đã được cài đặt

2. **"Invalid Unity project path"**:
   - Đảm bảo đường dẫn trỏ đến thư mục chứa `Assets/` và `ProjectSettings/`
   - Kiểm tra quyền truy cập thư mục

3. **"MCP server not responding"**:
   - Kiểm tra log trong Claude Desktop
   - Chạy server standalone để debug
   - Kiểm tra đường dẫn Python và main.py

### Kiểm tra logs:

```bash
# Server logs sẽ xuất hiện trong stderr
python main.py 2> unity_mcp_debug.log

# Hoặc xem log file Unity
tail -f /tmp/unity_mcp.log
```

## Cấu Hình Nâng Cao

### Security Settings:

```python
# Trong config.py
allowed_paths: List[str] = Field(
    default_factory=lambda: ["/path/to/unity/projects", "/path/to/assets"],
    description="Allowed file system paths"
)
```

### Custom Tools:

```python
# Bật/tắt các tools cụ thể
enabled_tools: List[str] = Field(
    default_factory=lambda: [
        "project.scan",
        "build.run",
        "test.playmode",
        # Thêm hoặc bỏ tools theo nhu cầu
    ]
)
```

## Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra file log
2. Chạy `python main.py --validate-only` để kiểm tra cấu hình
3. Tạo issue trên GitHub repository

---

**Lưu ý**: Đảm bảo tất cả đường dẫn sử dụng đường dẫn tuyệt đối và phù hợp với hệ điều hành của bạn.