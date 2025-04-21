import logging
import sys
import config # 引入配置文件
from apis.remove_invalid_documents import BackupCleaner
from apis.danmaku_converter import process_folder as convert_danmaku
from apis.video_encoder import process_folder as encode_video
from apis.biliup_uploader import upload_to_bilibili # 引入上传函数

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info("开始执行 Danmaku Compress 流程")

    # 1. 清理无效备份文件
    try:
        logger.info("步骤 1: 清理无效备份文件")
        cleaner = BackupCleaner(backup_dir=config.BACKUP_FOLDER)
        cleaner.remove_small_backups(min_size_mb=1.0) # 默认删除小于1MB的文件
        logger.info("无效备份文件清理完成")
    except Exception as e:
        logger.error(f"清理备份文件时出错: {e}")
        sys.exit(1)

    # 2. 转换弹幕文件 (XML -> ASS)
    try:
        logger.info("步骤 2: 转换弹幕文件 (XML -> ASS)")
        convert_danmaku(folder=config.PROCESSING_FOLDER)
        logger.info("弹幕文件转换完成")
    except Exception as e:
        logger.error(f"转换弹幕文件时出错: {e}")
        sys.exit(1)

    # 3. 压制视频 (FLV+ASS -> MP4)
    try:
        logger.info("步骤 3: 压制视频 (FLV+ASS -> MP4)")
        # 注意：video_encoder 默认会删除源 flv 和 ass 文件
        # 如果需要保留源文件，可以在 video_encoder.py 中修改或添加 test_mode=True 参数
        encode_video(folder=config.PROCESSING_FOLDER)
        logger.info("视频压制完成")
    except Exception as e:
        logger.error(f"压制视频时出错: {e}")
        sys.exit(1)

    # 4. 上传视频到 Bilibili
    try:
        logger.info("步骤 4: 上传视频到 Bilibili")
        if not config.BILIUP_RS_PATH:
            logger.warning("未在配置中找到 BILIUP_RS_PATH，跳过上传步骤。请在 .env 文件中设置。")
        else:
            upload_to_bilibili(biliup_path=config.BILIUP_RS_PATH)
            logger.info("Bilibili 上传任务已启动 (具体进度请查看 biliup-rs 的日志)")
    except Exception as e:
        logger.error(f"上传到 Bilibili 时出错: {e}")
        # 这里选择不退出 (sys.exit)，允许前面的步骤成功完成
        # 可以根据需要决定是否要在这里退出

    logger.info("Danmaku Compress 流程执行完毕")

if __name__ == "__main__":
    main()
