import os
import logging
from pathlib import Path

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BackupCleaner:
    """
    用于清理 backup 文件夹中无效备份文件的类。
    """
    def __init__(self, backup_dir: str = "backup"):
        """
        初始化 BackupCleaner。

        Args:
            backup_dir: 备份文件夹相对于项目根目录的路径。默认为 "backup"。
        """
        self.backup_path = Path(backup_dir)
        if not self.backup_path.is_dir():
            logging.warning(f"备份文件夹 {self.backup_path} 不存在或不是一个目录。")
            # 可以选择在这里抛出异常或创建目录
            # self.backup_path.mkdir(parents=True, exist_ok=True)

    def remove_small_backups(self, min_size_mb: float = 1.0):
        """
        遍历 backup 文件夹，删除小于指定大小 (MB) 的 .flv 文件及其对应的 .xml 文件。

        Args:
            min_size_mb: 文件大小的阈值 (MB)。小于此大小的 .flv 文件将被删除。默认为 1.0 MB。
        """
        if not self.backup_path.is_dir():
            logging.error(f"无法访问备份文件夹: {self.backup_path}")
            return

        min_size_bytes = min_size_mb * 1024 * 1024
        count_deleted = 0

        logging.info(f"开始扫描备份文件夹: {self.backup_path}")
        for item in self.backup_path.iterdir():
            # 检查是否是文件以及后缀是否为 .flv
            if item.is_file() and item.suffix == '.flv':
                # 简单的名称检查（可以根据需要使用更复杂的正则表达式）
                if item.name.startswith("银剑君录播") and "T" in item.name:
                    try:
                        file_size = item.stat().st_size
                        if file_size < min_size_bytes:
                            logging.info(f"找到小于 {min_size_mb}MB 的文件: {item.name} ({file_size / 1024 / 1024:.2f}MB)")

                            # 构建对应的 xml 文件路径
                            xml_file = item.with_suffix('.xml')

                            # 删除 flv 文件
                            try:
                                item.unlink()
                                logging.info(f"已删除文件: {item.name}")
                                count_deleted += 1
                            except OSError as e:
                                logging.error(f"删除文件 {item.name} 时出错: {e}")

                            # 删除对应的 xml 文件（如果存在）
                            if xml_file.exists() and xml_file.is_file():
                                try:
                                    xml_file.unlink()
                                    logging.info(f"已删除对应的 XML 文件: {xml_file.name}")
                                except OSError as e:
                                    logging.error(f"删除文件 {xml_file.name} 时出错: {e}")
                            else:
                                logging.warning(f"未找到对应的 XML 文件或该路径不是文件: {xml_file.name}")

                    except FileNotFoundError:
                         # 文件在检查大小和删除之间可能已被移除
                         logging.warning(f"文件 {item.name} 在处理过程中消失。")
                    except Exception as e:
                        logging.error(f"处理文件 {item.name} 时发生未知错误: {e}")

        logging.info(f"扫描完成。总共删除了 {count_deleted} 个小于 {min_size_mb}MB 的 FLV 文件 (及其 XML 文件)。")
