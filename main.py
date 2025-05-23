import logging
import sys
import time
import threading
import schedule
import config
from fastapi import FastAPI, BackgroundTasks, HTTPException # 引入 FastAPI 相关组件
from pydantic import BaseModel # 用于定义响应模型 (可选但推荐)

from apis.remove_invalid_documents import BackupCleaner
from apis.danmaku_converter import process_folder as convert_danmaku
from apis.video_encoder import process_folder as encode_video
from apis.biliup_uploader import upload_to_bilibili

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- 自动处理任务 ---
def process_files_automatically():
    """定期执行清理、转换弹幕和压制视频的任务"""
    results = {"status": "pending", "messages": [], "errors": []}

    def log_and_record(level, message, is_error=False):
        if level == logging.INFO:
            logger.info(message)
            results["messages"].append(message)
        elif level == logging.WARNING:
            logger.warning(message)
            results["messages"].append(f"WARN: {message}")
        elif level == logging.ERROR:
            logger.error(message)
            results["errors"].append(message)
            results["status"] = "partial_failure" if results["messages"] else "failure"

    # 1. 清理无效备份文件
    try:
        log_and_record(logging.INFO, "定时任务: 开始清理无效备份文件")
        cleaner = BackupCleaner(backup_dir=config.BACKUP_FOLDER)
        cleaner.remove_small_backups(min_size_mb=1.0)
        log_and_record(logging.INFO, "定时任务: 无效备份文件清理完成")
    except Exception as e:
        log_and_record(logging.ERROR, f"定时任务: 清理备份文件时出错: {e}")
        return results

    # 2. 转换弹幕文件 (XML -> ASS)
    try:
        log_and_record(logging.INFO, "定时任务: 开始转换弹幕文件 (XML -> ASS)")
        convert_danmaku(folder=config.PROCESSING_FOLDER)
        log_and_record(logging.INFO, "定时任务: 弹幕文件转换完成")
    except Exception as e:
        log_and_record(logging.ERROR, f"定时任务: 转换弹幕文件时出错: {e}")
        return results

    # 3. 压制视频 (FLV+ASS -> MP4)
    try:
        log_and_record(logging.INFO, "定时任务: 开始压制视频 (FLV+ASS -> MP4)")
        encode_video(folder=config.PROCESSING_FOLDER)
        log_and_record(logging.INFO, "定时任务: 视频压制完成")
    except Exception as e:
        log_and_record(logging.ERROR, f"定时任务: 压制视频时出错: {e}")
        return results

    if not results["errors"]:
         results["status"] = "success"
    log_and_record(logging.INFO, "定时任务: 自动处理流程执行完毕")
    return results

# --- 上传处理任务 ---
def upload_files():
    """执行上传处理任务"""
    results = {"status": "pending", "messages": [], "errors": []}

    def log_and_record(level, message, is_error=False):
        if level == logging.INFO:
            logger.info(message)
            results["messages"].append(message)
        elif level == logging.WARNING:
            logger.warning(message)
            results["messages"].append(f"WARN: {message}")
        elif level == logging.ERROR:
            logger.error(message)
            results["errors"].append(message)
            results["status"] = "partial_failure" if results["messages"] else "failure"

    # 上传视频到 Bilibili
    try:
        log_and_record(logging.INFO, "API任务: 开始上传视频到 Bilibili")
        if not config.BILIUP_RS_PATH:
            log_and_record(logging.WARNING, "未在配置中找到 BILIUP_RS_PATH，跳过上传步骤。请在 .env 文件中设置。")
        else:
            upload_to_bilibili(biliup_path=config.BILIUP_RS_PATH)
            log_and_record(logging.INFO, "API任务: Bilibili 上传任务已启动")
    except Exception as e:
        log_and_record(logging.ERROR, f"API任务: 上传到 Bilibili 时出错: {e}")
        # 上传失败通常不阻止返回成功状态，但记录错误

    if not results["errors"]:
         results["status"] = "success"
    log_and_record(logging.INFO, "API任务: 上传流程执行完毕")
    return results

# --- 定时任务调度器 ---
def run_scheduler():
    """运行定时任务调度器"""
    logger.info("启动定时任务调度器")
    # 默认每15分钟检查一次是否有新的文件需要处理
    schedule.every(15).minutes.do(process_files_automatically)
    
    # 运行调度器
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- 启动定时任务线程 ---
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()

# --- FastAPI 应用设置 ---
app = FastAPI(
    title="Danmaku Compress API",
    description="用于触发和监控弹幕视频处理流程的 API",
    version="1.0.0",
)

# 存储后台任务状态 (简单的全局状态)
background_task_status = {
    "is_running": False,
    "last_result": None
}

# --- 状态模型定义 ---
class PipelineStatus(BaseModel):
    is_running: bool
    last_result: dict | None

class TriggerResponse(BaseModel):
    message: str

# --- 后台上传任务执行函数 ---
def run_upload_background_task():
    """在后台执行上传流程并更新状态"""
    logger.info("后台任务：开始执行上传流程...")
    global background_task_status
    background_task_status["is_running"] = True
    background_task_status["last_result"] = None # 清除上次结果
    try:
        result = upload_files()
        background_task_status["last_result"] = result
        logger.info(f"后台任务：上传流程完成，结果: {result.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"后台任务：执行上传流程时发生未捕获错误: {e}", exc_info=True)
        background_task_status["last_result"] = {"status": "critical_failure", "errors": [f"未捕获的异常: {e}"]}
    finally:
        background_task_status["is_running"] = False
    logger.info("后台任务：结束执行")

# --- 手动触发处理任务 ---
def run_process_background_task():
    """在后台执行处理流程并更新状态"""
    logger.info("后台任务：开始执行处理流程...")
    global background_task_status
    background_task_status["is_running"] = True
    background_task_status["last_result"] = None # 清除上次结果
    try:
        result = process_files_automatically()
        background_task_status["last_result"] = result
        logger.info(f"后台任务：处理流程完成，结果: {result.get('status', 'unknown')}")
    except Exception as e:
        logger.error(f"后台任务：执行处理流程时发生未捕获错误: {e}", exc_info=True)
        background_task_status["last_result"] = {"status": "critical_failure", "errors": [f"未捕获的异常: {e}"]}
    finally:
        background_task_status["is_running"] = False
    logger.info("后台任务：结束执行")

# --- API 端点 ---
@app.post("/trigger_process", response_model=TriggerResponse, status_code=202)
def trigger_process_endpoint(background_tasks: BackgroundTasks):
    """
    手动触发处理流程（清理、转换、压制）在后台运行。
    
    如果已有任务在运行，则返回 429 错误。
    """
    if background_task_status["is_running"]:
        raise HTTPException(
            status_code=429,
            detail="处理流程已在运行中，请稍后再试。"
        )

    # 添加后台任务
    background_tasks.add_task(run_process_background_task)

    return {"message": "处理流程已在后台启动。"}

@app.post("/trigger_upload", response_model=TriggerResponse, status_code=202)
def trigger_upload_endpoint(background_tasks: BackgroundTasks):
    """
    触发视频上传流程在后台运行。
    
    如果已有任务在运行，则返回 429 错误。
    """
    if background_task_status["is_running"]:
        raise HTTPException(
            status_code=429,
            detail="处理流程已在运行中，请稍后再试。"
        )

    # 添加后台任务
    background_tasks.add_task(run_upload_background_task)

    return {"message": "上传流程已在后台启动。"}

@app.get("/status", response_model=PipelineStatus)
def get_status_endpoint():
    """
    获取当前处理流程的运行状态以及上次执行的结果。
    """
    # 直接返回全局状态字典，它符合 PipelineStatus 模型
    return background_task_status

# 注意：FastAPI 应用不需要 if __name__ == "__main__": app.run()
# 它将通过 uvicorn 启动
