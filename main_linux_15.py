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
    file_names = ["15-智能网联汽车 - 宏观基础-交通数据", "15-智能网联汽车 - 交通-道路交通情况", "15-智能网联汽车 - 交通-公共交通情况实体属性", "15-智能网联汽车 - 交通-广东省城际客流总体分布", "15-智能网联汽车 - 交通-国内主要城市地铁运营数据", "15-智能网联汽车 - 交通-客运交通概况", "15-智能网联汽车 - 交通-枢纽口岸运行情况", "15-智能网联汽车 - 交通-现状枢纽运营数据", "15-智能网联汽车 - 交通-现状铁路运行数据", "15-智能网联汽车 - 居民出行特征"]

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