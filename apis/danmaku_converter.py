import os
import sys
import io
import fnmatch
from dmconvert import convert_xml_to_ass


# 强制设置标准输出的编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def convert_to_ass(xml, ass):
    """将弹幕文件转换为ASS格式"""
    convert_xml_to_ass(xml, ass)

    print(f"ASS 文件已生成: {ass}")

def process_folder(folder="."):
    """处理文件夹中的所有XML文件"""
    folder = os.path.abspath(folder)
    print(f"正在处理文件夹: {folder}")
    
    # 获取所有XML文件
    xml_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if fnmatch.fnmatch(file.lower(), "*.xml"):
                xml_files.append(os.path.join(root, file))

    if not xml_files:
        print("未找到XML文件！")
        return

    print(f"找到 {len(xml_files)} 个XML文件")
    
    # 处理每个XML文件
    for xml_file in xml_files:
        print(f"\n处理文件: {xml_file}")
        ass_file = os.path.splitext(xml_file)[0] + ".ass"
        try:
            convert_to_ass(xml_file, ass_file)
        except Exception as e:
            print(f"处理 {xml_file} 时出错: {e}")
            continue