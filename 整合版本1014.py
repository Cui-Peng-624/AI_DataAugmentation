import os
import pandas as pd
from pydantic import BaseModel, create_model
from openai import OpenAI

# 设置代理环境（如果需要）
os.environ["http_proxy"] = "127.0.0.1:7890"
os.environ["https_proxy"] = "127.0.0.1:7890"

# config.py
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 读取
ZetaTechs_api_key = os.getenv('ZetaTechs_api_key')
ZetaTechs_api_base = os.getenv('ZetaTechs_api_base')

client = OpenAI(api_key=ZetaTechs_api_key, base_url=ZetaTechs_api_base)

# 读取 CSV 文件并忽略空列，保留“采集时间”和“备注【疑问汇总】”
def load_csv(file_path):
    df = pd.read_csv(file_path)
    # 找到不为空的列名
    non_empty_columns = df.columns[df.notna().any()].tolist()
    # 加入需要保留的列
    required_columns = ["采集来源", "来源链接", "采集时间", "备注【疑问汇总】"]
    final_columns = [col for col in non_empty_columns if col not in required_columns] + required_columns
    # 根据有效列筛选数据，并保留“采集时间”和“备注【疑问汇总】”列
    df = df[final_columns]
    return df

# 自动生成 column_mapping，忽略 "采集时间" 和 "备注【疑问汇总】"
def generate_column_mapping(df):
    columns_to_include = df.columns[:-2]  # 忽略最后两列
    column_mapping = {col: col for col in columns_to_include}
    return column_mapping

# 创建大模型的输入
def create_model_input(df, column_mapping):
    input_data = []
    for _, row in df.iterrows():
        mapped_input = {column_mapping[key]: row[key] for key in column_mapping}
        input_data.append(mapped_input)
    return input_data

def generate_data(system_prompt, user_prompt):
    messages_to_model=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
      ]

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages_to_model,
        # timeout=180  # 设置为120秒，确保有足够的时间
    )

    generated_data = completion.choices[0].message.content
    
    return generated_data

import json
from OutputValidator import OutputValidator

def process_generated_data(input_data, generated_data, save_invalid_path):
    """
    处理生成的数据，验证其有效性，并根据结果进行进一步处理或保存无效数据。

    :param input_data: 输入数据，用于创建验证器。
    :param generated_data: 生成的数据，需要进行验证。
    :param save_invalid_path: 保存无效输出的文件路径，默认为 "invalid_output.txt"。
    :return: 如果数据有效，返回增强后的数据；否则返回 None。
    """
    # 创建验证器
    expected_columns = list(input_data[0].keys())
    validator = OutputValidator(expected_columns)

    # 验证输出
    if validator.is_valid(generated_data):
        # 输出有效，可以进行进一步处理
        preprocessed_data = validator.preprocess_output(generated_data)
        parsed_data = json.loads(preprocessed_data)
        augmented_data = parsed_data["generated_data"]
        # print("Generated valid data:", type(augmented_data), len(augmented_data), "\n\n", augmented_data)
        print("Generated valid data.")
        return augmented_data
    else:
        # 输出无效，保存以供后续人工处理
        validator.save_invalid_output(generated_data, save_invalid_path)
        print("Generated invalid data. Saved to '{}' for manual processing.".format(save_invalid_path))
        return None

from pydantic import create_model

# 生成 Extraction 模型的函数
def generate_extraction_model(num_columns_to_augment):
    fields = {f'column{i+1}': (list[str], ...) for i in range(num_columns_to_augment)}
    return create_model('Extraction', **fields)

def extract_generated_data(generated_data, num_columns_to_augment):
    Extraction = generate_extraction_model(num_columns_to_augment)

    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", # gpt-4o-mini-2024-07-18
        messages=[
            {"role": "system", "content": "You are an expert at structured data extraction. Extract the data into the exact column structure provided."},
            {"role": "user", "content": generated_data}
        ],
        response_format=Extraction,
    )
    
    extracted_generated_data = completion.choices[0].message.parsed   
    return extracted_generated_data

def convert_extracted_generated_data_to_df(extracted_generated_data):
    # print(extracted_generated_data, "\n\n")
    # 初始化一个空字典，用于存储列名和对应的列数据
    data_dict = {}
    
    # 遍历 extracted_generated_data，每个元素是一个 (列名, 列数据) 的元组
    for col_name, col_data in extracted_generated_data:
        # 将列名和对应的列数据添加到字典中
        data_dict[col_name] = col_data
    
    # 将字典转化为 DataFrame
    df = pd.DataFrame(data_dict) # 这里可能会报错：ValueError: All arrays must be of the same length。列表长度不一致
    # print(df.head())
    return df

# 修改后的 transform_data 函数
def transform_data(augmented_data):
    # 获取所有的列名，并计算列的数量
    columns = list(augmented_data[0].keys())
    num_columns_to_augment = len(columns)
    
    # 动态生成 Extraction 模型
    Extraction = generate_extraction_model(num_columns_to_augment)
    
    # 初始化一个字典来存储转换后的数据
    transformed = {f'column{i+1}': [] for i in range(num_columns_to_augment)}
    
    # 填充数据
    for row in augmented_data:
        for i, (col, value) in enumerate(row.items()):
            transformed[f'column{i+1}'].append(str(value))
    
    # 将转换后的字典转换为 Extraction 对象
    return Extraction(**transformed)

def convert_extracted_generated_data_to_df(extracted_generated_data):
    # print(extracted_generated_data, "\n\n")
    # 初始化一个空字典，用于存储列名和对应的列数据
    data_dict = {}
    
    # 遍历 extracted_generated_data，每个元素是一个 (列名, 列数据) 的元组
    for col_name, col_data in extracted_generated_data:
        # 将列名和对应的列数据添加到字典中
        data_dict[col_name] = col_data
    
    # 将字典转化为 DataFrame
    df = pd.DataFrame(data_dict) # 这里可能会报错：ValueError: All arrays must be of the same length。列表长度不一致
    # print(df.head())
    return df

# 将扩展生成的数据与原始数据合并
def merge_data(original_df, extracted_generated_data_df, num_columns_to_augment):
    # 获取原始数据的列名，去掉最后的 "采集时间" 和 "备注【疑问汇总】" 两列
    original_columns = original_df.columns[:-2]
    
    # 生成数据的列名为 column1, column2, ...，将其映射为原始数据的列名
    extracted_generated_data_df.columns = original_columns[:num_columns_to_augment]
    
    # 为生成的数据添加 "采集时间" 和 "备注【疑问汇总】" 两列，默认填充为 None
    extracted_generated_data_df["采集时间"] = None
    extracted_generated_data_df["备注【疑问汇总】"] = None

    # print(extracted_generated_data_df.head())
    
    # 将原始数据和生成数据按列拼接起来
    merged_df = pd.concat([original_df, extracted_generated_data_df], axis=0)
    
    return extracted_generated_data_df, merged_df # 现在 extracted_generated_data_df 的格式是正确的，可以直接拼接到 merged_df 中

###########################################################
###########################################################
###########################################################
from create_prompts import create_system_prompt_1, create_system_prompt_2

from create_prompts import create_user_prompt_1, create_user_prompt_2, create_user_prompt_3, create_user_prompt_4, create_user_prompt_5, create_user_prompt_6, create_user_prompt_7, create_user_prompt_8

# 确保文件夹存在
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

### 覆写的 main 函数 ###
# def main(file_path, save_path, main_category, sub_category, num_entries, custom_requirements, required_total_rows, save_invalid_path):
#     """
#     参数说明：
#     file_path: str, the path to the CSV file containing the original data.
#     save_path: str, the path to save the extended data.
#     main_category: str, the main category of the dataset.
#     sub_category: str, the sub-category of the dataset.
#     num_entries: int, the number of entries to generate.
#     custom_requirements: str, any custom requirements specified by the user.  
#     required_total_rows: int, the total number of rows required in the extended dataset.
#     save_invalid_path: str, the path to save the invalid data.
#     """
#     # 确保文件夹存在
#     ensure_directory_exists(os.path.dirname(file_path))
#     ensure_directory_exists(os.path.dirname(save_path))
#     ensure_directory_exists(os.path.dirname(save_invalid_path))

#     # 第一步：加载数据
#     df = load_csv(file_path)

#     # 第二步：生成column_mapping
#     column_mapping = generate_column_mapping(df)

#     # 第三步：将df中的格式化数据进行一下初步的转化 - 一个list，每一个元素都是一个字典，包含了所有的列名和对应的值
#     input_data = create_model_input(df, column_mapping)
#     columns = list(input_data[0].keys()) # 获取所有的列名 - 到“来源链接”为止
#     num_columns_to_augment = len(columns)

#     # 第四步：创建系统提示和用户提示
#     system_prompt = create_system_prompt_2()
#     user_prompt = create_user_prompt_8(input_data, main_category, sub_category, num_entries, custom_requirements) # 这个表格需要处理的列数 - 忽略 "采集时间" 和 "备注【疑问汇总】"

#     merged_df = df.copy() # 创建一个原始df的一个副本 
#     total_rows = len(merged_df)

#     while total_rows < required_total_rows:
#         try:
#             # 第5步：调用 OpenAI API 生成数据
#             generated_data = generate_data(system_prompt, user_prompt)

#             # 第6步：处理生成的数据
#             augmented_data = process_generated_data(input_data, generated_data, save_invalid_path)
            
#             if augmented_data is not None: # 如果生成的数据符合我们的格式要求 <-> 如果无效，process_generated_data() 会将错误格式的数据保存到 save_invalid_path
#                 # 第七步
#                 transformed_data = transform_data(augmented_data)

#                 # 第八步：将生成的数据转化为df
#                 transformed_data_df = convert_extracted_generated_data_to_df(transformed_data)

#                 # 第9步：合并原始数据和生成数据
#                 _, merged_df = merge_data(merged_df, transformed_data_df, num_columns_to_augment)

#                 total_rows = len(merged_df)  # 更新总行数

#                 # 每次生成都保存扩展后的数据
#                 # merged_df.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
#                 merged_df.to_csv(save_path, mode='w', header=True, index=False)
#                 print(f"扩展后的数据已保存到 {save_path}。当前总行数为 {total_rows}，继续生成数据...")
            
#             else: # 说明 generated_data 不符合我们的格式要求，我们直接对 generated_data 进行处理
#                 extracted_generated_data = extract_generated_data(generated_data, num_columns_to_augment)
#                 extracted_generated_data_df = convert_extracted_generated_data_to_df(extracted_generated_data)
#                 extracted_generated_data_df, merged_df = merge_data(merged_df, extracted_generated_data_df, num_columns_to_augment)
#                 total_rows = len(merged_df)  # 更新总行数
#                 # 每次生成都保存扩展后的数据
#                 # merged_df.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
#                 merged_df.to_csv(save_path, mode='w', header=True, index=False)
#                 print(f"本次生成的数据不符合自定义的结构要求，使用json mode提取数据。扩展后的数据已保存到 {save_path}。当前总行数为 {total_rows}，继续生成数据...")
 
#         except ValueError as e:
#             print(f"生成数据时发生错误：{str(e)}。跳过本次生成，继续下一次。")
#             continue
#         except Exception as e:
#             print(f"发生未预期的错误：{str(e)}。跳过本次生成，继续下一次。")
#             continue

### 追加模式的 main 函数 ###
def main(file_path, save_path, main_category, sub_category, num_entries, custom_requirements, required_total_rows, save_invalid_path):
    """
    参数说明：
    file_path: str, the path to the CSV file containing the original data.
    save_path: str, the path to save the extended data.
    main_category: str, the main category of the dataset.
    sub_category: str, the sub-category of the dataset.
    num_entries: int, the number of entries to generate.
    custom_requirements: str, any custom requirements specified by the user.  
    required_total_rows: int, the total number of rows required in the extended dataset.
    save_invalid_path: str, the path to save the invalid data.
    """
    # 确保文件夹存在
    ensure_directory_exists(os.path.dirname(file_path))
    ensure_directory_exists(os.path.dirname(save_path))
    ensure_directory_exists(os.path.dirname(save_invalid_path))

    # 第一步：加载数据
    df = load_csv(file_path)

    # 第二步：生成column_mapping
    column_mapping = generate_column_mapping(df)

    # 第三步：将df中的格式化数据进行一下初步的转化 - 一个list，每一个元素都是一个字典，包含了所有的列名和对应的值
    input_data = create_model_input(df, column_mapping)
    columns = list(input_data[0].keys()) # 获取所有的列名 - 到“来源链接”为止
    num_columns_to_augment = len(columns)

    # 第四步：创建系统提示和用户提示
    system_prompt = create_system_prompt_2()
    user_prompt = create_user_prompt_8(input_data, main_category, sub_category, num_entries, custom_requirements) # 这个表格需要处理的列数 - 忽略 "采集时间" 和 "备注【疑问汇总】"

    merged_df = df.copy() # 创建一个原始df的一个副本 
    total_rows = len(merged_df)

    while total_rows < required_total_rows:
        try:
            # 第5步：调用 OpenAI API 生成数据
            generated_data = generate_data(system_prompt, user_prompt)

            # 第6步：处理生成的数据
            augmented_data = process_generated_data(input_data, generated_data, save_invalid_path)
            
            if augmented_data is not None: # 如果生成的数据符合我们的格式要求 <-> 如果无效，process_generated_data() 会将错误格式的数据保存到 save_invalid_path
                # 第七步
                transformed_data = transform_data(augmented_data)

                # 第八步：将生成的数据转化为df
                transformed_data_df = convert_extracted_generated_data_to_df(transformed_data)

                # 第9步：合并原始数据和生成数据
                extracted_generated_data_df, merged_df = merge_data(merged_df, transformed_data_df, num_columns_to_augment)

                total_rows = len(merged_df)  # 更新总行数

                # 每次生成都保存扩展后的数据
                extracted_generated_data_df.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
                # merged_df.to_csv(save_path, mode='w', header=True, index=False)
                print(f"扩展后的数据已追加到 {save_path}。当前总行数为 {total_rows}，继续生成数据...")
            
            else: # 说明 generated_data 不符合我们的格式要求，我们直接对 generated_data 进行处理
                extracted_generated_data = extract_generated_data(generated_data, num_columns_to_augment)
                extracted_generated_data_df = convert_extracted_generated_data_to_df(extracted_generated_data)
                extracted_generated_data_df, merged_df = merge_data(merged_df, extracted_generated_data_df, num_columns_to_augment)
                total_rows = len(merged_df)  # 更新总行数
                # 每次生成都保存扩展后的数据
                extracted_generated_data_df.to_csv(save_path, mode='a', header=not os.path.exists(save_path), index=False)
                # merged_df.to_csv(save_path, mode='w', header=True, index=False)
                print(f"本次生成的数据不符合自定义的结构要求，使用json mode提取数据。扩展后的数据已追加到 {save_path}。当前总行数为 {total_rows}，继续生成数据...")
 
        except ValueError as e:
            print(f"生成数据时发生错误：{str(e)}。跳过本次生成，继续下一次。")
            continue
        except Exception as e:
            print(f"发生未预期的错误：{str(e)}。跳过本次生成，继续下一次。")
            continue