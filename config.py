# config.py

import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

# 从环境变量获取备份文件夹路径，如果未设置则使用默认值
BACKUP_FOLDER = os.getenv("BACKUP_FOLDER", "/vol1/1000/biliup/backup")

# 从环境变量获取处理文件夹路径，如果未设置则使用默认值
PROCESSING_FOLDER = os.getenv("PROCESSING_FOLDER", "/vol1/1000/biliup/backup")

# 从环境变量获取 biliup-rs 工具所在的路径
BILIUP_RS_PATH = os.getenv("BILIUP_RS_PATH", "/vol1/1000/biliup/biliup-rs")
