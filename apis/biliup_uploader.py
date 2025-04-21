import subprocess
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_to_bilibili(biliup_path: str, config_file: str = "config.yaml"):
    """
    在指定的 biliup-rs 目录下执行上传命令。

    Args:
        biliup_path: biliup-rs 工具所在的目录路径。
        config_file: biliup-rs 使用的配置文件名 (相对于 biliup_path)。
    """
    command = ["./biliup", "upload", "-c", config_file]
    command_str = " ".join(command) # 用于日志记录

    logger.info(f"准备在目录 {biliup_path} 执行上传命令: {command_str}")

    try:
        # 确保 biliup_path 存在且是一个目录
        if not os.path.isdir(biliup_path):
            logger.error(f"指定的 biliup-rs 路径无效或不是目录: {biliup_path}")
            raise FileNotFoundError(f"Biliup path not found or not a directory: {biliup_path}")

        # 检查 biliup 可执行文件是否存在 (基本检查)
        biliup_executable = os.path.join(biliup_path, "biliup")
        if not os.path.isfile(biliup_executable) or not os.access(biliup_executable, os.X_OK):
             logger.warning(f"无法找到 biliup 可执行文件或没有执行权限: {biliup_executable}")
             # 根据需要可能需要抛出错误

        result = subprocess.run(
            command,
            cwd=biliup_path, # 在指定目录下执行
            check=True,      # 如果命令返回非零退出码则抛出异常
            capture_output=True, # 捕获 stdout 和 stderr
            text=True,       # 以文本模式处理输出
            encoding='utf-8' # 显式指定编码
        )
        logger.info(f"biliup-rs 上传命令标准输出:\n{result.stdout}")
        if result.stderr:
            logger.warning(f"biliup-rs 上传命令标准错误输出:\n{result.stderr}")
        logger.info("Bilibili 上传命令执行成功。")

    except FileNotFoundError as e:
        logger.error(f"执行上传命令失败: {e}。请检查 BILIUP_RS_PATH 是否正确配置，并且该目录下包含 biliup 可执行文件。")
        raise # 重新抛出异常，让 main.py 捕获
    except subprocess.CalledProcessError as e:
        logger.error(f"biliup-rs 上传命令执行失败，返回码: {e.returncode}")
        logger.error(f"标准输出:\n{e.stdout}")
        logger.error(f"标准错误:\n{e.stderr}")
        raise # 重新抛出异常
    except Exception as e:
        logger.error(f"执行 biliup-rs 上传时发生未知错误: {e}")
        raise # 重新抛出异常 