import os
import fnmatch
import subprocess
import datetime
import shlex
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def encode(video, ass, mp4, test_mode=False):
    """压制视频并合并弹幕"""
    # 调整 FFmpeg 命令以提高 Linux 兼容性，使用 libx264 软件编码器
    cmd = f'ffmpeg -hwaccel vaapi -i {shlex.quote(video)} ' \
          f'-vf "ass={shlex.quote(ass)}" ' \
          f'-c:v h264_qsv -preset veryfast -preset veryfast -global_quality 22  -c:a copy -y {shlex.quote(mp4)}'

    logger.info(f"开始压制时间：{datetime.datetime.now()}")
    logger.info(f"执行命令: {cmd}") # 添加日志记录执行的命令
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.stderr:
            logger.info(result.stderr.decode('utf-8'))

        # 非测试模式下删除源文件
        if not test_mode:
            try:
                os.remove(video)
                os.remove(ass)
                logger.info(f"已删除源文件: {video} 和 {ass}")
            except Exception as e:
                logger.error(f"删除源文件失败: {e}")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg 压制失败: {e.stderr.decode('utf-8')}")
        raise

    logger.info(f"结束压制时间：{datetime.datetime.now()}")

def process_folder(folder=".", test_mode=False):
    """处理文件夹中的所有FLV和ASS文件"""
    folder = os.path.abspath(folder)
    all_files = os.listdir(folder)
    logger.info(f"当前目录下的文件：{all_files}")

    flv_files = [os.path.join(folder, f) for f in all_files if fnmatch.fnmatch(f.lower(), "*.flv")]
    ass_files = [os.path.join(folder, f) for f in all_files if fnmatch.fnmatch(f.lower(), "*.ass")]

    logger.info(f"找到的FLV文件：{flv_files}")
    logger.info(f"找到的ASS文件：{ass_files}")

    if not flv_files or not ass_files:
        logger.warning("未找到FLV或ASS文件！")
        return

    for flv_file in flv_files:
        flv_name = os.path.splitext(os.path.basename(flv_file))[0]
        ass_file = next((ass for ass in ass_files if os.path.splitext(os.path.basename(ass))[0] == flv_name), None)

        if not ass_file:
            logger.warning(f"未找到与 {flv_file} 匹配的ASS文件，跳过处理。")
            continue

        logger.info(f"正在处理文件：{flv_file} 和 {ass_file}")
        mp4_file = os.path.splitext(flv_file)[0] + ".mp4"
        encode(flv_file, ass_file, mp4_file, test_mode)
