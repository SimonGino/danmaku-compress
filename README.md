# Danmaku Compress: 弹幕视频自动化处理工具

这是一个 Python 脚本项目，旨在自动化处理录播文件或其他视频，包含以下主要流程：

1.  **（可选）清理无效备份：** 扫描指定备份文件夹，删除体积过小的 FLV 视频文件及其关联的 XML 弹幕文件。
2.  **弹幕格式转换：** 将指定处理文件夹中的 XML 格式弹幕文件批量转换为 ASS 格式。
3.  **视频压制与合并：** 使用 FFmpeg 将指定处理文件夹中的 FLV 视频文件与转换后的 ASS 弹幕文件合并，并压制成 MP4 格式。

## 功能特性

*   **自动化流程：** 一键执行清理、转换、压制三个步骤。
*   **配置灵活：** 通过 `config.py` 文件轻松指定备份和处理文件夹路径。
*   **备份清理：** 可根据文件大小（默认为 < 1MB）自动删除无效的 FLV 和 XML 文件，保持备份目录整洁。
*   **弹幕转换：** 利用 `dmconvert` 库将 XML 弹幕转换为兼容性更好的 ASS 格式。
*   **视频压制：** 调用系统中的 FFmpeg，使用 `libx264` 编码器（兼容性较好）将弹幕硬编码到视频中，生成 MP4 文件。
*   **自动删除源文件：** 成功压制 MP4 后，默认会删除原始的 FLV 和 ASS 文件以节省空间（可在代码中修改此行为）。

## 环境要求

*   **Python 3:** 脚本基于 Python 3 编写。
*   **FFmpeg:** 必须在系统环境变量中可以调用 `ffmpeg` 命令。视频压制功能依赖此程序。
*   **dmconvert 库:** 弹幕转换功能需要此 Python 库。你可以通过 pip 安装：
    ```bash
    pip install dmconvert 
    ```
    (如果 `dmconvert` 不是标准的 PyPI 包，请根据其来源进行安装)。

## 安装与配置

1.  **获取项目：**
    ```bash
    git clone <your-repo-url> # 或者直接下载 ZIP 文件解压
    cd danmaku-compress
    ```
2.  **安装依赖：**
    ```bash
    pip install dmconvert # 如上所述安装 dmconvert
    # 建议创建一个 requirements.txt 文件管理依赖
    ```
3.  **配置路径：**
    *   打开 `config.py` 文件。
    *   修改 `BACKUP_FOLDER` 为你的备份文件夹路径（相对于项目根目录），脚本将在此处执行清理操作。
    *   修改 `PROCESSING_FOLDER` 为你的待处理视频和弹幕文件夹路径（相对于项目根目录），脚本将在此处执行弹幕转换和视频压制。
    *   确保这两个文件夹存在并且具有正确的读写权限。

## 使用方法

1.  **准备文件：**
    *   将需要清理的 FLV 和 XML 文件放入 `config.BACKUP_FOLDER` 指定的目录。
    *   将需要转换和压制的 XML 和 FLV 文件放入 `config.PROCESSING_FOLDER` 指定的目录。
2.  **运行脚本：**
    在项目根目录下打开终端，执行：
    ```bash
    python main.py
    ```
3.  **查看结果：**
    *   脚本会按顺序执行清理、转换、压制操作，并在终端输出日志信息。
    *   最终生成的 MP4 文件会保存在 `config.PROCESSING_FOLDER` 指定的目录中。
    *   注意：原始的 FLV 和 ASS 文件（在处理目录中）默认会被删除。

## 注意事项

*   **文件命名：** 清理功能默认只处理文件名以 `银剑君录播` 开头且包含 `T` 的 FLV 文件。视频压制依赖于 FLV 和 ASS 文件具有相同的主文件名（不含扩展名）。
*   **编码设置：** `video_encoder.py` 中默认使用 `libx264` 进行软件编码，以获得较好的兼容性。如果你的 Linux 系统支持并配置了硬件加速（如 NVENC, VAAPI），可以修改 `encode` 函数中的 `ffmpeg` 命令以利用硬件加速，提高速度。
*   **错误处理：** 脚本包含基本的错误处理，但如果 FFmpeg 或 `dmconvert` 出错，流程可能会中断。请检查终端输出的日志以获取详细信息。
*   **删除源文件：** 如果不希望在压制成功后删除原始的 FLV 和 ASS 文件，可以修改 `apis/video_encoder.py` 中 `encode` 函数，在调用 `subprocess.run` 后移除删除文件的逻辑，或者在 `main.py` 调用 `encode_video` 时传递 `test_mode=True` 参数（如果 `video_encoder.py` 支持该参数并传递给了 `encode` 函数）。
