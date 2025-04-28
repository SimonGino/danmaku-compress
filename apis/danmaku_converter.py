import os
import logging
import fnmatch
from dmconvert import convert_xml_to_ass
import subprocess
import json

logger = logging.getLogger(__name__)
def convert_to_ass(xml_file, ass_file):
    """将弹幕文件转换为ASS格式"""
    # 默认分辨率，仅在无法获取视频分辨率时使用
    font_size = 38
    sc_font_size = 30
    resolution_x = 1920
    resolution_y = 1080
    
    # 尝试获取对应视频的分辨率
    video_file = os.path.splitext(xml_file)[0] + ".flv"
    if os.path.exists(video_file):
        try:
            # 使用ffprobe获取视频分辨率
            cmd = [
                "ffprobe", 
                "-v", "error", 
                "-select_streams", "v:0", 
                "-show_entries", "stream=width,height", 
                "-of", "json", 
                video_file
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                if "streams" in data and len(data["streams"]) > 0:
                    stream = data["streams"][0]
                    resolution_x = stream.get("width", resolution_x)
                    resolution_y = stream.get("height", resolution_y)
                    logger.info(f"检测到视频分辨率: {resolution_x}x{resolution_y}")
        except Exception as e:
            logger.warning(f"获取视频分辨率失败: {e}，将使用默认分辨率")
    else:
        logger.warning(f"未找到对应视频文件: {video_file}，将使用默认分辨率")
        
    convert_xml_to_ass(font_size, sc_font_size, resolution_x, resolution_y, xml_file, ass_file)

    logger.info(f"ASS 文件已生成: {ass_file}")

def process_folder(folder="."):
    """处理文件夹中的所有XML文件"""
    folder = os.path.abspath(folder)
    logger.info(f"正在处理文件夹: {folder}")
    
    # 获取所有XML文件，过滤掉未完成的XML文件
    xml_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            # 排除 .xml.part 和其他可能未完成的XML文件
            if (fnmatch.fnmatch(file.lower(), "*.xml") and 
                not file.lower().endswith(".xml.part") and
                not file.lower().endswith(".part")):
                xml_files.append(os.path.join(root, file))

    if not xml_files:
        logger.error("未找到XML文件！")
        return

    logger.info(f"找到 {len(xml_files)} 个XML文件")
    
    # 处理每个XML文件
    for xml_file in xml_files:
        logger.info(f"\n处理文件: {xml_file}")
        
        # 检查是否有正在录制的对应FLV文件
        flv_file = os.path.splitext(xml_file)[0] + ".flv"
        flv_part_file = flv_file + ".part"
        
        if os.path.exists(flv_part_file):
            logger.warning(f"对应的视频文件 {flv_part_file} 仍在录制中，跳过此XML文件")
            continue
            
        ass_file = os.path.splitext(xml_file)[0] + ".ass"
        try:
            convert_to_ass(xml_file, ass_file)
            # 继续删除转换完的xml文件
            # os.remove(xml_file)
        except Exception as e:
            logger.error(f"处理 {xml_file} 时出错: {e}")
            continue