import logging
import sys
import config # 引入配置文件
from apis.remove_invalid_documents import BackupCleaner
from apis.danmaku_converter import process_folder as convert_danmaku
from apis.video_encoder import process_folder as encode_video

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

    logger.info("Danmaku Compress 流程执行完毕")

if __name__ == "__main__":
    main()
