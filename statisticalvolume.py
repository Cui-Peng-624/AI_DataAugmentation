import os
import csv

def count_csv_lines(root_folder):
    total_lines = 0
    folder_lines = {}  # 用于存储每个子文件夹的行数

    # 遍历根文件夹
    for dirpath, dirnames, filenames in os.walk(root_folder):
        folder_lines[dirpath] = 0  # 初始化每个子文件夹的行数
        
        for filename in filenames:
            if filename.endswith('.csv'):
                file_path = os.path.join(dirpath, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as csvfile:
                        reader = csv.reader(csvfile)
                        # 减去1是为了不计算表头
                        lines = sum(1 for row in reader) - 1
                        total_lines += lines
                        folder_lines[dirpath] += lines  # 累加到当前子文件夹
                        # print(f"文件 {file_path} 有 {lines} 行")
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {str(e)}")

    return total_lines, folder_lines

# 使用示例
root_folder = "1029扩充后的数据集"
total_lines, folder_lines = count_csv_lines(root_folder)

print(f"所有CSV文件的总行数（不包括表头）：{total_lines}")
print("每个子文件夹的CSV文件行数：")
for folder, lines in folder_lines.items():
    print(f"{folder}: {lines} 行")