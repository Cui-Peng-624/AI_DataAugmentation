from 整合版本1014 import main

import re

def extract_categories(filename):
    # 使用正则表达式匹配文件名格式
    match = re.match(r'(\d+-.+?) - (.+)', filename)
    if match:
        main_category = match.group(1).strip()
        sub_category = match.group(2).strip()
        return main_category, sub_category
    else:
        return None, None
    
# 示例调用
if __name__ == "__main__":
    file_names = ["14-安全节能环保 - 安全应急死亡人数数据统计", "14-安全节能环保 - 安全应急信息化投入金额统计", "14-安全节能环保 - 节能环保企业名单", "14-安全节能环保 - 企业业务考核体系设计", "14-安全节能环保 - 应急能力评估体系"]

    for file_name in file_names:
        main_category, sub_category = extract_categories(file_name)
        file_path = f"筛选出指定行之后的数据集/{main_category}/{file_name}.csv"
        save_path = f"1029扩充后的数据集/{main_category}/{file_name}_expanded.csv"
        save_invalid_path = f"invalid_outputs/{main_category}/{sub_category}.txt"

        num_entries = 20
        custom_requirements = ""
        required_total_rows = 30000
        # 执行主流程
        main(file_path, save_path, main_category, sub_category, num_entries, custom_requirements, required_total_rows, save_invalid_path)