Thiết kế Model Context Protocol (MCP) cho dự án Unity
Giới thiệu

Model Context Protocol (MCP) là một lớp trung gian cho phép Large‑Language Models (LLM) gọi các chức năng liên quan tới một dự án Unity một cách an toàn và có kiểm soát. Nhiệm vụ của MCP là nhận yêu cầu dưới dạng JSON, xác thực dữ liệu theo JSON Schema, thực thi các hành động (quét dự án, build, chạy test, audit tài sản, sinh mã, v.v.), theo dõi tiến trình dưới dạng stream log và trả về kết quả có cấu trúc. Tài liệu này mô tả kiến trúc tổng thể, các tool cụ thể, mã mẫu của MCP server (NodeJS) và Unity Bridge (C# Editor script), quy trình demo, yêu cầu bảo mật, kiểm thử, CI, và gợi ý mở rộng.

Giả định

Phiên bản Unity: 2022/2023 LTS sử dụng URP/HDRP, .NET Standard 2.1.

Hệ điều hành mục tiêu: hỗ trợ macOS và Windows cho cả môi trường máy trạm và CI. Nếu người dùng không chỉ rõ, triển khai mẫu sử dụng NodeJS (TypeScript) làm MCP server và C# editor script làm Unity Bridge.

Đường dẫn dự án: cấu trúc chuẩn của Unity gồm Assets/, Packages/, ProjectSettings/ và các workflow CI (GitHub Actions/GitLab). Thư mục cho phép ghi sẽ được giới hạn (allow‑list) – ví dụ Assets/Scripts/AI/** hoặc ProjectSettings/**.

1. Kiến trúc tổng thể
1.1 Sơ đồ luồng dữ liệu
flowchart TB
    subgraph "LLM Client"
        A["Yêu cầu tool\n(JSON request)"]
    end
    subgraph "MCP Server (NodeJS)"
        B["HTTP/IPC endpoint\nXác thực JSON\nStream log"]
        C["Executor\n(child_process hoặc IPC)"]
    end
    subgraph "Unity Bridge (C# Editor)"
        D["Command Handler\n(Reader/Writer)\n– nhận JSON qua STDIN/NamedPipe"]
    end
    subgraph "Unity Editor/CLI"
        E["Editor API & CLI\n(build, test, scan, profiler, asset import)"]
    end
    subgraph "File System & CI"
        F["Assets/Packages/ProjectSettings\nUnity Build Output\nCI pipelines"]
    end

    A <--> |HTTP/IPC| B
    B --> |spawn/IPC| C
    C <--> |STDIN/STDOUT| D
    D --> |call Unity API / CLI| E
    E <--> F
    E --> |logs & reports| C
    C --> |JSON response, stream| B --> A


Kênh truyền:

LLM ⇄ MCP Server: giao tiếp thông qua HTTP/HTTPS hoặc IPC (ví dụ Unix domain socket). MCP server nhận yêu cầu JSON, xác thực bằng Ajv/Zod, gán operationId duy nhất và trả về stream log dưới dạng JSONL.

MCP Server ⇄ Unity Bridge: sử dụng child_process.spawn để chạy Unity.exe với tham số -batchmode/-quit và chỉ định phương thức -executeMethod hoặc bằng kênh NamedPipe/STDIO tới một EditorWindow trong phiên bản Unity đang chạy. Kết quả và lỗi được truyền qua STDOUT/STDERR.

Unity Bridge ⇄ Unity Editor/CLI: script C# trong dự án xử lý lệnh (đọc JSON, gọi API tương ứng, thực hiện hủy bỏ theo file flag, thu thập log). Với build/test có thể gọi trực tiếp CLI (-runTests, -buildTarget), với các thao tác chi tiết (quét scene, audit asset, codegen) dùng Editor API.

Unity Editor ⇄ File System/CI: Unity truy xuất file trong Assets/, Packages/ và ghi kết quả vào thư mục được allow‑list (ví dụ Builds/, TestResults/). Trong môi trường CI, Unity sử dụng cache/accelerator, test runner hay builder action.

1.2 Luồng lỗi và log

Log stream: mọi tool xuất log thành định dạng JSONL gồm trường timestamp, level (info/warn/error), message và operationId. MCP Server chuyển log theo chunk tới client, hỗ trợ hủy bỏ (cancelation) qua endpoint.

Lỗi chuẩn hóa: mỗi tool định nghĩa errorCode (ví dụ BUILD_FAILED, TEST_TIMEOUT, INVALID_SCHEMA). Unity CLI trả mã exit ≠ 0 được ánh xạ thành lỗi tiêu chuẩn.

Hủy bỏ/Timeout: MCP tạo file flag cancel.flag trong thư mục tạm; Unity Bridge thường xuyên kiểm tra file để hủy tác vụ dài. Timeout được cấu hình trên server; khi vượt quá thời gian, tiến trình con bị kill và trả lỗi TIMEOUT.

2. Bộ tool

Các tool được định nghĩa bằng JSON Schema Draft‑07. Mỗi tool có name, purpose, inputSchema, outputSchema và danh sách errors. Input/Output chỉ chấp nhận kiểu nguyên thủy (string, number, boolean, array, object) và phải mô tả rõ ràng. Bảng dưới đây tóm tắt các tool chính. Các bảng chỉ chứa trường ngắn gọn; mô tả chi tiết nằm trong phần chữ.

2.1 project.scan
Trường (input)	Kiểu	Bắt buộc	Mô tả
patterns	array<string>	có	Danh sách glob filter (ví dụ ["Assets/Scenes/**/*.unity", "Assets/Prefabs/**/*.prefab"]).
includeScripts	boolean	không	Nếu true, bao gồm cả tệp .cs quan trọng.

Output: danh sách đối tượng chứa path, type (scene/prefab/script), có thể kèm thêm thuộc tính (size, guid). Lỗi: SCAN_FAILED.

2.2 build.run
Trường (input)	Kiểu	Bắt buộc	Mô tả
target	string	có	Mục tiêu build: android, ios, win64, osx, webgl. Tham khảo tài liệu CLI; Unity hỗ trợ các build target qua tùy chọn -buildTarget
docs.unity3d.com
.
scriptingBackend	string	không	mono hoặc il2cpp.
developmentBuild	boolean	không	Bật chế độ dev build (bao gồm symbol).
outputPath	string	có	Thư mục đầu ra (đã allow‑list).
timeoutMinutes	number	không	Giới hạn thời gian build.

Output: trạng thái (success: true/false), đường dẫn build, kích thước file, log compile. Lỗi: BUILD_FAILED, INVALID_TARGET, TIMEOUT.

2.3 test.playmode & test.editmode
Trường (input)	Kiểu	Bắt buộc	Mô tả
filters	object	không	Tuỳ chọn filter theo testCategory, testName, testNamespace. Unity CLI cho phép -testFilter/-testPlatform và -testResults
docs.unity3d.com
.
outputPath	string	có	Thư mục chứa kết quả junit XML.
timeoutMinutes	number	không	Timeout toàn bộ test.
collectCoverage	boolean	không	Thu thập báo cáo coverage (nếu có).

Output: passed, failed, skipped, junitPath. Khi failed > 0, MCP có thể thu thập 10 dòng log quanh lỗi đầu tiên. Lỗi: TEST_FAILED, TEST_TIMEOUT, TEST_FILTER_INVALID.

2.4 scene.validate
Trường (input)	Kiểu	Bắt buộc	Mô tả
scenes	array<string>	có	Danh sách scene cần kiểm tra.
checks	array<string>	không	Các loại kiểm tra: missingScripts, lightmaps, tags, layers, staticFlags.

Output: danh sách vi phạm. Ví dụ: {path: "Assets/Scenes/Main.unity", issue: "MissingScript", gameObject: "Enemy", componentIndex: 2}.

Các kiểm tra tham khảo:

Missing scripts: Unity cung cấp GameObjectUtility.GetMonoBehavioursWithMissingScriptCount để đếm số component bị mất và RemoveMonoBehavioursWithMissingScript để xoá
docs.unity3d.com
. Ta sử dụng chức năng đếm để báo cáo.

Static flags: thuộc tính GameObject.isStatic trả về true khi bất kỳ StaticEditorFlags nào được đặt
docs.unity3d.com
. Kiểm tra object bị đánh dấu static không mong muốn.

Tags & Layers: thuộc tính GameObject.layer cho biết layer (0–31); Unity dành các layer 0–5 cho hệ thống và cho phép dùng từ layer 5 trở lên
docs.unity3d.com
. Thuộc tính GameObject.tag lưu tag và cần được khai báo trong Tag Manager
docs.unity3d.com
.

Lightmaps: kiểm tra renderer có lightmapIndex >= 0 và cờ ContributeGI (một giá trị của StaticEditorFlags).

Lỗi: VALIDATION_FAILED, SCENE_NOT_FOUND.

2.5 asset.audit
Trường (input)	Kiểu	Bắt buộc	Mô tả
paths	array<string>	có	Glob filter cho asset (ví dụ Assets/Characters/**/*.png).
checks	array<string>	không	textureSize, meshOptimization, importSettings.

Output: danh sách cảnh báo, ví dụ {"path": "Assets/Characters/Hero.png", "issue": "TextureTooLarge", "maxSize": 4096}.

Texture quá lớn: thuộc tính TextureImporter.maxTextureSize đặt kích thước tối đa; texture lớn hơn sẽ được giảm xuống cỡ này khi import
docs.unity3d.com
. MCP có thể cảnh báo khi texture gốc vượt qua ngưỡng (ví dụ > 2048 px).

Mesh optimization: ModelImporter.optimizeMeshPolygons và optimizeMeshVertices tối ưu hoá thứ tự polygon/vertex để cải thiện việc cache GPU
docs.unity3d.com
. Nếu cờ này bị tắt hoặc mesh có nhiều đỉnh, MCP gợi ý bật optimize.

Import settings khác: kiểm tra readable, compression, rig.

Lỗi: AUDIT_FAILED.

2.6 codegen.apply
Trường (input)	Kiểu	Bắt buộc	Mô tả
path	string	có	File C# mục tiêu (thuộc allow‑list).
patch	string	có	Nội dung diff (Unified diff).
dryRun	boolean	không	Nếu true, chỉ trả về preview diff mà không ghi file.

Output: {applied: boolean, diff: string}. Nếu dryRun là true, applied=false và diff mô tả thay đổi. Lỗi: PATCH_FAILED, PATH_NOT_ALLOWED.

2.7 editor.exec
Trường (input)	Kiểu	Bắt buộc	Mô tả
method	string	có	Tên static method hoặc menu item đã được allow‑list (ví dụ MyCompany.Tools.ClearCache).
args	array<any>	không	Tham số truyền vào.

Output: {result: any}. Lỗi: METHOD_NOT_ALLOWED, EXECUTION_FAILED.

2.8 perf.profile
Trường (input)	Kiểu	Bắt buộc	Mô tả
frames	number	không	Số khung hình cần thu (mặc định 300).
outputPath	string	có	Đường dẫn file .raw hoặc .data nơi lưu snapshot.

Output: {snapshotPath: string, sizeBytes: number}. Lỗi: PROFILE_FAILED.

Thực hiện: Unity hỗ trợ các tham số -profiler-enable, -profiler-log-file, và -profiler-capture-frame-count để tự động stream dữ liệu profiler sang file .raw khi khởi động
docs.unity.cn
. MCP gọi CLI với các tham số này; khi hoàn thành, file snapshot sẽ được trả về cho LLM (kèm kích thước) nhưng không chứa dữ liệu bí mật.

3. Mã mẫu
3.1 MCP Server (TypeScript/NodeJS)

Dưới đây là ví dụ đơn giản của MCP server dùng NodeJS với Express. Mã này khởi tạo HTTP server, đăng ký tool build.run và test.playmode, sử dụng Ajv để xác thực input, và gọi Unity bằng child_process.spawn. Những phần liên quan tới sandbox (restrict fs) và allow‑list cần được bổ sung theo nhu cầu dự án.

// mcpServer.ts
import express from 'express';
import { spawn } from 'child_process';
import Ajv from 'ajv';
import { nanoid } from 'nanoid';

const app = express();
app.use(express.json());

// Định nghĩa schema cho build.run (chỉ ví dụ ngắn)
const buildSchema = {
  type: 'object',
  properties: {
    target: { type: 'string' },
    scriptingBackend: { type: 'string', enum: ['mono', 'il2cpp'], nullable: true },
    developmentBuild: { type: 'boolean' },
    outputPath: { type: 'string' }
  },
  required: ['target', 'outputPath'],
  additionalProperties: false
};

const ajv = new Ajv();
const validateBuild = ajv.compile(buildSchema);

// Stream logs back to client
function streamProcess(proc: any, res: any, operationId: string) {
  proc.stdout.on('data', (data: Buffer) => {
    data.toString().split('\n').forEach((line: string) => {
      if (line.trim().length > 0) {
        res.write(JSON.stringify({ operationId, level: 'info', message: line }) + '\n');
      }
    });
  });
  proc.stderr.on('data', (data: Buffer) => {
    data.toString().split('\n').forEach((line: string) => {
      if (line.trim().length > 0) {
        res.write(JSON.stringify({ operationId, level: 'error', message: line }) + '\n');
      }
    });
  });
  proc.on('close', (code: number) => {
    res.write(JSON.stringify({ operationId, level: 'info', message: `process_exit:${code}` }) + '\n');
    res.end();
  });
}

app.post('/tool/build.run', (req, res) => {
  const operationId = nanoid();
  const body = req.body;
  if (!validateBuild(body)) {
    return res.status(400).json({ errorCode: 'INVALID_SCHEMA', details: validateBuild.errors });
  }
  res.setHeader('Content-Type', 'application/jsonl');

  // Xây dựng lệnh Unity CLI
  const unityArgs = [
    '-batchmode', '-quit',
    '-projectPath', process.env.PROJECT_PATH ?? '.',
    '-buildTarget', body.target,
    '-executeMethod', 'MCPBridge.BuildPlayer',
    // truyền thêm tham số qua argv hoặc biến môi trường
  ];
  // Spawn Unity
  const proc = spawn(process.env.UNITY_PATH ?? 'Unity', unityArgs, { env: process.env });
  streamProcess(proc, res, operationId);
});

app.listen(8000, () => console.log('MCP Server listening on port 8000')); 


Giải thích:

Server khởi tạo endpoint /tool/build.run nhận JSON. Ajv được dùng để xác thực theo schema. Nếu input hợp lệ, hàm spawn gọi Unity CLI ở chế độ -batchmode và -quit. Các tham số cụ thể (như target, outputPath) có thể được truyền qua biến môi trường hoặc file tạm; trong ví dụ này ta gọi một method MCPBridge.BuildPlayer trong Unity Bridge.

Hàm streamProcess đọc stdout và stderr, chuyển mỗi dòng thành JSONL gồm operationId, level và message. Khi process kết thúc, ghi thêm một sự kiện process_exit.

Trong môi trường thực, cần cấu hình process.env.UNITY_PATH trỏ tới Unity.exe (Windows) hoặc /Applications/Unity/Unity.app/Contents/MacOS/Unity (macOS) và process.env.PROJECT_PATH tới thư mục dự án.

Mã mẫu chưa bao gồm sandbox --permission của Node; khi triển khai, nên chạy Node với cờ --no-deprecation --permission --allow-fs-read=* --allow-fs-write=allowed_dir để giới hạn truy cập file
nodejs.org
.

3.2 Unity Bridge (C# Editor script)

Unity Bridge chạy trong Editor ở chế độ batchmode hoặc headless và nhận lệnh qua STDIN hoặc NamedPipe. Dưới đây là ví dụ giản lược cho hai tool: build và chạy test. Script này nằm trong Assets/Editor/MCPBridge.cs.

using System;
using System.IO;
using System.Text;
using System.Threading;
using UnityEditor;
using UnityEditor.TestTools;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.TestTools;

public static class MCPBridge
{
    // Đọc JSON từ stdin và dispatch tới handler
    public static void Main() {
        try {
            string json = Console.In.ReadToEnd();
            var cmd = JsonUtility.FromJson<MCPCommand>(json);
            switch (cmd.tool) {
                case "build.run":
                    HandleBuild(cmd.payload);
                    break;
                case "test.playmode":
                    HandleTest(cmd.payload, TestMode.PlayMode);
                    break;
                case "test.editmode":
                    HandleTest(cmd.payload, TestMode.EditMode);
                    break;
                // Các tool khác được bổ sung tương tự
                default:
                    WriteError("UNKNOWN_TOOL", "Tool not implemented");
                    break;
            }
        } catch (Exception ex) {
            WriteError("BRIDGE_ERROR", ex.Message);
        }
    }

    // Ví dụ build bằng BuildPipeline
    private static void HandleBuild(string payloadJson) {
        var payload = JsonUtility.FromJson<BuildRequest>(payloadJson);
        var options = new BuildPlayerOptions();
        options.scenes = EditorBuildSettingsScene.GetActiveSceneList();
        options.locationPathName = payload.outputPath;
        options.target = GetBuildTarget(payload.target);
        options.options = payload.developmentBuild ? BuildOptions.Development | BuildOptions.AllowDebugging : BuildOptions.None;
        var report = BuildPipeline.BuildPlayer(options);
        if (report.summary.result == BuildResult.Succeeded) {
            WriteJSON(new { success = true, outputPath = payload.outputPath, sizeBytes = new FileInfo(payload.outputPath).Length });
        } else {
            WriteError("BUILD_FAILED", report.summary.ToString());
        }
    }

    // Ví dụ chạy test dùng TestRunnerApi
    private static void HandleTest(string payloadJson, TestMode mode) {
        var payload = JsonUtility.FromJson<TestRequest>(payloadJson);
        var testRunnerApi = ScriptableObject.CreateInstance<TestRunnerApi>();
        var filter = new Filter() { testMode = mode, categoryNames = payload.filters?.categories };
        int passed = 0, failed = 0, skipped = 0;
        var finishedEvent = new ManualResetEvent(false);
        testRunnerApi.RegisterCallbacks(new TestRunCallback {
            testFinishedEvent = r => {
                if (r.resultStatus == TestResultState.Passed) passed++;
                else if (r.resultStatus == TestResultState.Failed) failed++;
                else skipped++;
            },
            runFinishedEvent = result => finishedEvent.Set()
        });
        testRunnerApi.Execute(new ExecutionSettings(filter));
        // Chờ test hoàn thành hoặc timeout
        if (!finishedEvent.WaitOne(TimeSpan.FromMinutes(payload.timeoutMinutes))) {
            WriteError("TEST_TIMEOUT", "Test exceeded timeout");
            return;
        }
        // Ghi junit nếu cần
        // ... viết file junit XML tại payload.outputPath ...
        WriteJSON(new { passed, failed, skipped, junitPath = payload.outputPath });
    }

    // Helper: ánh xạ chuỗi target thành BuildTarget
    private static BuildTarget GetBuildTarget(string target) {
        return target switch {
            "android" => BuildTarget.Android,
            "ios" => BuildTarget.iOS,
            "win64" => BuildTarget.StandaloneWindows64,
            "osx" => BuildTarget.StandaloneOSX,
            "webgl" => BuildTarget.WebGL,
            _ => BuildTarget.NoTarget,
        };
    }

    private static void WriteJSON(object obj) {
        Console.WriteLine(JsonUtility.ToJson(obj));
    }

    private static void WriteError(string code, string message) {
        Console.WriteLine(JsonUtility.ToJson(new { errorCode = code, message }));
    }

    // Structs dùng cho JSON deserialization
    [Serializable]
    private struct MCPCommand { public string tool; public string payload; }
    [Serializable]
    private struct BuildRequest { public string target; public bool developmentBuild; public string outputPath; }
    [Serializable]
    private struct TestRequest { public TestFilter filters; public string outputPath; public float timeoutMinutes; }
    [Serializable]
    private struct TestFilter { public string[] categories; }
    private class TestRunCallback : ICallbacks
    {
        public Action<ITestResultAdaptor> testFinishedEvent;
        public Action<ITestResultAdaptor> runFinishedEvent;
        public void RunStarted(ITestAdaptor testsToRun) {}
        public void RunFinished(ITestResultAdaptor result) => runFinishedEvent?.Invoke(result);
        public void TestStarted(ITestAdaptor test) {}
        public void TestFinished(ITestResultAdaptor result) => testFinishedEvent?.Invoke(result);
    }
}


Giải thích:

Phương thức Main đọc JSON từ STDIN, phân tích thành MCPCommand (gồm tên tool và payload). Sau đó chuyển tới hàm xử lý phù hợp.

HandleBuild sử dụng BuildPipeline.BuildPlayer. Tài liệu Unity nêu rằng sử dụng BuildPipeline.BuildPlayer cùng BuildPlayerOptions để build player và nhận BuildReport
docs.unity3d.com
. Kết quả thành công trả về kích thước file, thất bại trả BUILD_FAILED.

HandleTest sử dụng TestRunnerApi và Filter để chạy test playmode hoặc editmode (testCategory có thể truyền qua payload.filters.categories). Tài liệu Unity khuyến cáo dùng TestRunnerApi để chạy test trong code
docs.unity.cn
. Hàm đợi test hoàn thành với ManualResetEvent và trả lại thống kê.

Các tool khác (scan scene, audit asset, codegen) có thể được cài đặt tương tự: load asset bằng AssetDatabase, gọi GameObjectUtility hoặc ModelImporter để kiểm tra thuộc tính, sau đó ghi kết quả ra console dưới dạng JSON.

Cần triển khai cơ chế hủy bỏ: một thread kiểm tra file cancel.flag và khi tồn tại thì hủy BuildPipeline hoặc TestRunnerApi.

3.3 Mẫu CI (GitHub Actions)

Đoạn YAML sau minh hoạ cách tích hợp MCP trong CI để chạy test hoặc build khi được LLM kích hoạt. Sử dụng action game-ci/unity-test-runner@v4 làm ví dụ
game.ci
.

name: unity-mcp-ci
on:
  workflow_dispatch:
  workflow_call:
    inputs:
      operation:
        type: string
        description: 'Tool to run via MCP (e.g., build.run, test.playmode)'
      payload:
        type: string
        description: 'JSON payload for the tool'
jobs:
  run-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Unity Test Runner
        uses: game-ci/unity-test-runner@v4
        with:
          unityVersion: '2022.3.4f1'
          projectPath: '.'
          githubToken: ${{ secrets.GITHUB_TOKEN }}
      - name: Install Node & dependencies
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm install
      - name: Run MCP Tool
        env:
          UNITY_PATH: /opt/unity/Editor/Unity
          PROJECT_PATH: ${{ github.workspace }}
        run: |
          node dist/mcpServer.js &
          MCP_PID=$!
          sleep 5
          # Gửi request tới MCP server (ví dụ build.run)
          curl -X POST -H 'Content-Type: application/json' \
               -d "${{ inputs.payload }}" \
               http://localhost:8000/tool/${{ inputs.operation }} || true
          kill $MCP_PID



CI job trên có thể được gọi bởi LLM thông qua workflow_dispatch API, cho phép kiểm soát quyền thực thi. Trước khi chạy, license Unity cần được cấu hình như hướng dẫn của GameCI – thiết lập biến môi trường UNITY_LICENSE, UNITY_EMAIL, UNITY_PASSWORD
game.ci
.

4. Demo tool‑call flow
Kịch bản: build Android IL2CPP dev build, chạy playmode test, nếu thất bại thì đề xuất fix

LLM gửi yêu cầu build:

{
  "tool": "build.run",
  "payload": {
    "target": "android",
    "scriptingBackend": "il2cpp",
    "developmentBuild": true,
    "outputPath": "Builds/AndroidDev"
  }
}


MCP server xác thực input và stream log. Nếu build thành công, trả:

{"operationId":"abc123","level":"info","message":"process_exit:0"}
{"success":true,"outputPath":"Builds/AndroidDev","sizeBytes":105432345}


LLM gửi yêu cầu chạy test playmode:

{
  "tool": "test.playmode",
  "payload": {
    "filters": { "categories": ["AI_Navigation"] },
    "outputPath": "TestResults/playmode.xml",
    "timeoutMinutes": 20
  }
}


Unity Bridge sử dụng TestRunnerApi để chạy test PlayMode. Kết quả:

{"passed":12,"failed":1,"skipped":0,"junitPath":"TestResults/playmode.xml"}


Nếu failed > 0, MCP có thể tự động phân tích file junit để trích log của trường hợp đầu tiên và gọi tool nav.guides hoặc ai.review (mở rộng) để đề xuất fix. Ví dụ: gửi codegen.apply với diff patch để sửa component bị null.

Log rút gọn

Log stream (JSONL) chứa dấu thời gian, mức severity và message. Ví dụ:

{"operationId":"abc123","level":"info","message":"Building for android..."}
{"operationId":"abc123","level":"error","message":"Assets/Scripts/Enemy.cs(45,13): error CS0103: The name 'navAgent' does not exist"}
{"operationId":"abc123","level":"info","message":"process_exit:1"}

5. Bảo mật & quyền hạn

An toàn là ưu tiên hàng đầu. Dưới đây là các biện pháp:

Allow‑list đường dẫn: chỉ cho phép ghi vào các thư mục được chỉ định (Builds/, TestResults/, Assets/Scripts/AI/**). Mọi truy cập ngoài danh sách bị từ chối (PATH_NOT_ALLOWED).

Sandbox Node: chạy MCP server bằng cờ --permission để hạn chế đọc/ghi file hệ thống
nodejs.org
. Hạn chế network nếu không cần thiết.

Ẩn thông tin nhạy cảm: token/secret (Unity license, mật khẩu, API key) phải được cung cấp ở cấp server/CI và không bao giờ được log hay trả về cho LLM. Khi có lỗi, chỉ trả mã và mô tả chung.

Require dry‑run: các tool ghi file (codegen.apply, build.run) phải hỗ trợ tùy chọn dryRun. LLM phải nhận diff và xác nhận trước khi áp dụng.

Kiểm tra input schema: Ajv/Zod bắt buộc. Bất kỳ trường không khai báo đều bị từ chối (INVALID_SCHEMA).

Timeout & Cancelation: mọi hành động dài (build/test/audit) phải hỗ trợ timeout. File flag cancel.flag hoặc endpoint /cancel/{operationId} cho phép hủy. Nếu bị kill, ghi log.

Allow‑list method: editor.exec chỉ cho phép gọi các menu/method đã đăng ký trong file cấu hình (allowedMethods.json).

Quyền CI: LLM gọi CI bằng workflow_dispatch cần được kiểm soát qua GitHub/GitLab permission. Administrator có thể giới hạn branch hoặc require approval.

6. Kiểm thử & nghiệm thu
6.1 Unit test

Schema validation: viết test dùng ajv (Node) hoặc jsonschema (Python) để đảm bảo mọi schema đúng cú pháp và validator hoạt động như mong muốn
python-jsonschema.readthedocs.io
.

Parser JSON: test quá trình serialise/deserialise MCPCommand, BuildRequest, TestRequest trong Unity Bridge.

6.2 Test tích hợp

Build & Test: chạy tool build.run và test.playmode trên project mẫu (có script và test). So sánh log và output.

Scene scan: tạo scene giả với GameObject bị thiếu script, layer sai, cờ static. Kiểm tra tool scene.validate phát hiện đúng.

Asset audit: import texture lớn (>2048 px), mesh có optimize tắt, và kiểm tra cảnh báo.

Fault injection: mô phỏng Unity trả exit code 1, test timeout, file lock (mở file đích trong process khác) để bảo đảm MCP trả lỗi BUILD_FAILED, TEST_TIMEOUT, PATCH_FAILED.

6.3 Checklist an toàn cho tool ghi/patch

Đầu vào hợp lệ theo schema.

Đường dẫn thuộc allow‑list.

Thực hiện dry‑run và trình bày diff cho user.

Nhận xác nhận rõ ràng từ user trước khi ghi.

Kiểm tra lại file sau khi ghi (hash, kích thước) để đảm bảo integrity.

7. CI & vận hành

Tách môi trường: cài đặt MCP server như daemon cục bộ trên máy phát triển, và chạy song song với Unity Editor. Trong CI, chạy MCP trong container/dịch vụ riêng với quyền tối thiểu.

Caching Unity: sử dụng caching (GameCI Accelerator) để giảm thời gian build.

Log lưu trữ: lưu log JSONL kèm operationId trong object storage. Cho phép tái tạo lỗi khi cần.

Cold‑start optimization: sử dụng Editor headless persistent (mở một phiên Editor và giữ lắng nghe HTTP/NamedPipe) để giảm thời gian khởi động < 10 giây. Lựa chọn CLI batchmode cho quy trình nặng (build/test dài) hoặc khi Editor không cần chạy sẵn.

Cross‑platform: MCP server định nghĩa đường dẫn abstract, sử dụng path.join để tương thích Windows/macOS. Unity build target win64/osx/android/ios cần cài đặt SDK tương ứng.

8. Mở rộng

Cơ cấu plugin hoá cho phép thêm tool mới mà không thay đổi core. Ví dụ:

nav.guides: cung cấp hướng dẫn sửa lỗi phổ biến sau khi validate hoặc audit (tra cứu doc/knowledge base).

ai.review: phân tích diff của Pull Request và đề xuất cải tiến theo guideline đồ hoạ URP/HDRP.

code.lint: chạy Roslyn/StyleCop để kiểm tra coding style, trả về đề xuất.

scene.optimize: tự động gợi ý combine mesh, batching static, occlusion culling.

Kết luận

Model Context Protocol đưa ra một kiến trúc rõ ràng, an toàn và có khả năng mở rộng để LLM tương tác với dự án Unity. Các công cụ được định nghĩa bằng JSON Schema, thực thi thông qua MCP server và Unity Bridge, kết hợp với log có cấu trúc, sandbox và cơ chế hủy bỏ giúp đảm bảo độ tin cậy. Với lộ trình triển khai trên, đội phát triển có thể tích hợp LLM vào quy trình build/test/quản lý dự án mà vẫn giữ kiểm soát quyền hạn và bảo mật.