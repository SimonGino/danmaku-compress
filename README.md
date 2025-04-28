# Danmaku Compress: 弹幕视频自动化处理工具

这是一个 Python 脚本项目，旨在自动化处理录播文件或其他视频，包含以下主要流程：

1.  **（可选）清理无效备份：** 扫描指定备份文件夹，删除体积过小的 FLV 视频文件及其关联的 XML 弹幕文件。
2.  **弹幕格式转换：** 将指定处理文件夹中的 XML 格式弹幕文件批量转换为 ASS 格式。
3.  **视频压制与合并：** 使用 FFmpeg 将指定处理文件夹中的 FLV 视频文件与转换后的 ASS 弹幕文件合并，并压制成 MP4 格式。
4.  **视频上传：** 支持通过 API 调用将处理完成的视频上传至 Bilibili。

## 功能特性

*   **自动化流程：** 定时自动执行清理、转换、压制三个步骤，默认每15分钟检查一次是否有新文件需要处理。
*   **独立上传控制：** 视频压制与上传流程分离，可通过单独的 API 触发上传操作。
*   **未完成文件识别：** 自动识别并跳过未完成的录制文件（`.flv.part` 和相关未完成的 XML 文件）。
*   **API 接口：** 提供 RESTful API 接口，可手动触发处理或上传流程。
*   **配置灵活：** 通过 `config.py` 文件轻松指定备份和处理文件夹路径。
*   **备份清理：** 可根据文件大小（默认为 < 1MB）自动删除无效的 FLV 和 XML 文件，保持备份目录整洁。
*   **弹幕转换：** 利用 `dmconvert` 库将 XML 弹幕转换为兼容性更好的 ASS 格式。
*   **视频压制：** 调用系统中的 FFmpeg，使用 QSV 硬件加速（如果支持）将弹幕硬编码到视频中，生成 MP4 文件。
*   **自动删除源文件：** 成功压制 MP4 后，默认会删除原始的 FLV 和 ASS 文件以节省空间（可在代码中修改此行为）。

## 环境要求

*   **Python 3:** 脚本基于 Python 3 编写。
*   **FFmpeg:** 必须在系统环境变量中可以调用 `ffmpeg` 命令。视频压制功能依赖此程序。
*   **Python 库:** 需要安装以下库：
    ```bash
    pip install python-dotenv dmconvert fastapi uvicorn schedule
    ```
    (建议将依赖写入 `requirements.txt` 文件: `echo -e "python-dotenv\ndmconvert\nfastapi\nuvicorn\nschedule" > requirements.txt && pip install -r requirements.txt`)
*   **biliup-rs (B站上传工具):** 视频上传功能依赖此外部工具。
    *   **获取:** 从官方 Releases 页面下载适合你操作系统的最新版本：[https://github.com/biliup/biliup-rs/releases](https://github.com/biliup/biliup-rs/releases)
    *   **解压:** 将下载的压缩包解压到一个**固定**的目录。
    *   **配置:** `biliup-rs` 需要进行配置才能使用。你需要：
        1.  在该目录下创建或修改 `config.yaml` 文件，配置上传参数（如线路、投稿信息模板等）。
        2.  运行一次 `./biliup login` （或根据其文档进行登录）以生成 `cookies.json` 文件，用于身份验证。
        3.  **重要:** 本 `Danmaku Compress` 脚本**不会**自动配置 `biliup-rs`。你需要参考 `biliup-rs` 的官方文档完成其自身的配置。
    *   **路径设置:** 在本项目根目录下的 `.env` 文件中，设置 `BILIUP_RS_PATH` 变量，使其指向你解压并配置好的 `biliup-rs` 所在的**目录**。

## 安装与配置

1.  **获取项目：**
    ```bash
    git clone <your-repo-url> # 或者直接下载 ZIP 文件解压
    cd danmaku-compress
    ```
2.  **安装依赖：**
    ```bash
    pip install python-dotenv dmconvert fastapi uvicorn schedule
    # 建议创建一个 requirements.txt 文件管理依赖
    ```
3.  **配置 `.env` 文件:**
    *   在项目根目录下创建（或复制 `.env.example` 为 `.env`）一个名为 `.env` 的文件。
    *   编辑 `.env` 文件，至少设置以下变量：
        *   `BACKUP_FOLDER`: 备份文件夹路径（清理操作的目标）。
        *   `PROCESSING_FOLDER`: 处理文件夹路径（转换和压制操作的目标，最终 MP4 文件会在此生成）。
        *   `BILIUP_RS_PATH`: 指向你存放 `biliup-rs` 可执行文件、`config.yaml` 和 `cookies.json` 的目录的**绝对路径**。
    *   确保这些路径对应的文件夹存在并且脚本具有读写权限。

## 使用方法

1.  **准备文件：**
    *   将需要清理的 FLV 和 XML 文件放入 `config.BACKUP_FOLDER` 指定的目录。
    *   将需要转换和压制的 XML 和 FLV 文件放入 `config.PROCESSING_FOLDER` 指定的目录。
    *   注意：系统会自动跳过以 `.flv.part` 结尾的未完成录制文件。

2.  **启动服务：**
    在项目根目录下打开终端，执行：
    ```bash
    nohup uvicorn main:app --host 0.0.0.0 --port 50009 > fastapi_app.log 2>&1 &
    ```

3.  **API 调用：**
    服务启动后，系统将开始以下工作：
    * 定时任务：每 15 分钟自动检查一次处理文件夹中是否有新的 FLV 和 XML 文件，并执行清理、转换和压制操作
    * 提供以下 API 接口（可使用 curl、Postman 或其他工具调用）：
      ```
      # 手动触发文件处理流程（清理、转换、压制）
      curl -X POST http://localhost:50009/trigger_process
      
      # 触发视频上传到 Bilibili
      curl -X POST http://localhost:50009/trigger_upload
      
      # 查询当前任务状态
      curl http://localhost:50009/status
      ```
    
    * 自动生成的 API 文档：访问 `http://localhost:50009/docs` 可查看详细的 API 文档

4.  **查看结果：**
    *   脚本会按顺序执行清理、转换、压制操作，并在终端和日志文件中输出信息。
    *   最终生成的 MP4 文件会保存在 `config.PROCESSING_FOLDER` 指定的目录中。
    *   可通过 API 调用手动触发上传操作，将处理好的视频上传至 Bilibili。

## 注意事项

*   **定时任务间隔：** 默认每 15 分钟检查一次是否有新文件需要处理。可在 `main.py` 的 `run_scheduler` 函数中修改检查频率。
*   **文件命名：** 清理功能默认只处理文件名以 `银剑君录播` 开头且包含 `T` 的 FLV 文件。视频压制依赖于 FLV 和 ASS 文件具有相同的主文件名（不含扩展名）。
*   **未完成录制文件：** 系统会自动跳过以 `.flv.part` 结尾的视频文件和对应的未完成 XML 文件，确保只处理已完成录制的文件。
*   **编码设置：** `video_encoder.py` 中默认使用 QSV 硬件加速进行编码。如果你的系统不支持 QSV，或者希望使用其他编码器（如 NVENC, VAAPI 或软件编码），可以修改 `encode` 函数中的 `ffmpeg` 命令。
*   **错误处理：** 脚本包含基本的错误处理，每个处理步骤发生错误时会记录到日志，但不会影响后续定时任务的执行。
*   **删除源文件：** 如果不希望在压制成功后删除原始的 FLV 和 ASS 文件，可以修改 `apis/video_encoder.py` 中 `encode` 函数，在调用 `subprocess.run` 后移除删除文件的逻辑，或者在调用 `encode_video` 时传递 `test_mode=True` 参数。
*   **上传依赖:** 确保 `BILIUP_RS_PATH` 在 `.env` 中正确设置，并且该目录下的 `biliup-rs` 已正确配置并能独立运行 (`./biliup upload -c config.yaml` 应能手动成功执行)。
*   **`biliup-rs` 目录结构示例 (位于 `BILIUP_RS_PATH`):**
    ```
    /path/to/your/biliup-rs/  <-- BILIUP_RS_PATH 指向这里
    ├── biliup                # biliup-rs 可执行文件
    ├── config.yaml           # biliup-rs 配置文件
    ├── cookies.json          # 登录后生成的 cookies 文件
    └── uploads/              # (可选) biliup-rs 可能使用的上传目录
    ```
