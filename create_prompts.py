############################################################################################################
def create_system_prompt_1():
    return """
    You are an expert in data augmentation. You will be provided with a table structure and sample data. 
    Your task is to augment the dataset by generating new entries while maintaining consistency with the original format and meaning of the columns.
    Ensure that each generated entry follows the exact column order and data type of the original dataset.
    Focus on creating diverse and realistic entries, ensuring the augmented data aligns closely with the structure and content of the original dataset.
    """

############################################################################################################
# claude 的改进版本，
def create_system_prompt_2():
    return """
    You are an expert in data augmentation with extensive knowledge in various fields. Your task is to augment datasets by generating new entries that are diverse, realistic, and consistent with the original format and meaning of the columns.
    
    Use your broad knowledge base to:
    1. Introduce realistic variations in the data while maintaining the overall structure and relationships between fields.
    2. Incorporate current trends, events, and factual information relevant to the dataset's topic.
    3. Ensure logical consistency between related fields (e.g., population sizes matching city sizes, dates of events aligning with historical facts).
    4. Provide plausible and varied sources for the data, reflecting real-world information channels.
    
    While generating data, maintain a balance between creativity and realism, ensuring that the augmented data could feasibly exist in the real world.
    """

#**********************************************************************************************************#
#**********************************************************************************************************#
#**********************************************************************************************************#

############################################################################################################
# 不包含对列名的说明，仅仅是现有数据
def create_user_prompt_1(input_data):
    # 构建user prompt，将所有input_data中的信息加入提示
    prompt = "Here is the structure of the dataset with sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"  # 每行数据后增加换行，区分不同行
    prompt += "Please generate more data in the same structure and format."
    return prompt

############################################################################################################
# 对每个列名进行说明的prompt
def create_user_prompt_2(input_data):
    prompt = "Here is the structure of the dataset with sample data and column descriptions:\n\n"
    columns = list(input_data[0].keys())
    for col in columns:
        prompt += f"Column: {col}\n"
        prompt += f"Description: [Add a brief description of what this column represents]\n"
        prompt += f"Example: {input_data[0][col]}\n\n"
    prompt += "Please generate more data in the same structure and format, ensuring each column contains appropriate data."
    return prompt

############################################################################################################
# 综合create_user_prompt_1 and create_user_prompt_2
from table_structure_manager import TableStructureManager

manager = TableStructureManager()

def create_user_prompt_3(input_data, main_category, sub_category):
    prompt = f"Here is the structure of the dataset '{sub_category}' under '{main_category}' with column descriptions and sample data:\n\n"
    
    # 列描述和示例
    columns = list(input_data[0].keys())
    for col in columns:
        prompt += f"Column: {col}\n"
        prompt += f"Description: {manager.get_column_description(main_category, sub_category, col)}\n"
        prompt += f"Example: {input_data[0][col]}\n\n"

    # 现有数据
    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"  # 每行数据后增加换行，区分不同行

    prompt += "Please generate more data in the same structure and format, ensuring each column contains appropriate and realistic data. Maintain consistency with the provided examples and descriptions."
    return prompt

############################################################################################################
# create_user_prompt_3的提升版本，增加了生成数据的格式要求 - 问题：json格式不太标准，前后会有额外的输出
def create_user_prompt_4(input_data, main_category, sub_category):
    prompt = f"Here is the structure of the dataset '{sub_category}' under '{main_category}' with column descriptions and sample data:\n\n"
    
    columns = list(input_data[0].keys())
    for col in columns:
        prompt += f"Column: {col}\n"
        prompt += f"Description: {manager.get_column_description(main_category, sub_category, col)}\n"
        prompt += f"Example: {input_data[0][col]}\n\n"

    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"

    prompt += """
    Please generate more data in the same structure and format, ensuring each column contains appropriate and realistic data. Maintain consistency with the provided examples and descriptions.

    Output the generated data in the following JSON format:
    {
        "generated_data": [
            {
                "column1": "value1",
                "column2": "value2",
                ...
            },
            {
                "column1": "value1",
                "column2": "value2",
                ...
            },
            ...
        ]
    }

    Ensure that the JSON is valid and contains at least 5 new entries.
    """
    return prompt

############################################################################################################
# create_user_prompt_5 以及 OutputValidator.py 解决了 create_user_prompt_4 中输出是md格式的json格的问题。并且可以控制新增数据的数量
def create_user_prompt_5(input_data, main_category, sub_category, num_entries=5):
    prompt = f"Here is the structure of the dataset '{sub_category}' under '{main_category}' with column descriptions and sample data:\n\n"
    
    columns = list(input_data[0].keys())
    for col in columns:
        prompt += f"Column: {col}\n"
        prompt += f"Description: {manager.get_column_description(main_category, sub_category, col)}\n"
        prompt += f"Example: {input_data[0][col]}\n\n"

    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"

    prompt += f"""
    Please generate more data in the same structure and format, ensuring each column contains appropriate and realistic data. Maintain consistency with the provided examples and descriptions.

    Output the generated data in the following JSON format. Here's an example of the expected output format:

    {{
        "generated_data": [
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            ...
        ]
    }}

    Please generate exactly {num_entries} new entries following this exact format. Ensure that:
    1. The JSON is valid and can be parsed.
    2. All numeric values are represented as numbers (not strings).
    3. String values are enclosed in double quotes.
    4. Date values are in the format "YYYY-MM-DD".
    5. The structure exactly matches the example provided.
    6. Generate realistic and diverse data for different entries.
    7. Do not include any markdown formatting such as ``` json or ``` in your output.
    8. 采集来源需要填写数据信息来源的平台。
    9. 来源链接必须是真实存在的网址，且与数据内容相关。注意，你不必给出具体文件的链接，只需提供数据来源的大致网站主页即可。但你必须保证其链接是有效的。
    10. Ensure that you generate exactly {num_entries} entries, no more and no less.
    """
    return prompt

############################################################################################################
# create_user_prompt_6 是 create_user_prompt_5 的升级版本，增加了自定义需求的功能
def create_user_prompt_6(input_data, main_category, sub_category, num_entries=5, custom_requirements=""):
    prompt = f"Here is the structure of the dataset '{sub_category}' under '{main_category}' with column descriptions and sample data:\n\n"
    
    columns = list(input_data[0].keys())
    for col in columns:
        prompt += f"Column: {col}\n"
        prompt += f"Description: {manager.get_column_description(main_category, sub_category, col)}\n"
        prompt += f"Example: {input_data[0][col]}\n\n"

    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"

    prompt += f"""
    Please generate more data in the same structure and format, ensuring each column contains appropriate and realistic data. Maintain consistency with the provided examples and descriptions.

    Output the generated data in the following JSON format. Here's an example of the expected output format:

    {{
        "generated_data": [
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            ...
        ]
    }}

    Please generate exactly {num_entries} new entries following this exact format. Ensure that:
    1. The JSON is valid and can be parsed.
    2. All numeric values are represented as numbers (not strings).
    3. String values are enclosed in double quotes.
    4. Date values are in the format "YYYY-MM-DD".
    5. The structure exactly matches the example provided.
    6. Generate realistic and diverse data for different entries.
    7. Do not include any markdown formatting such as ``` json or ``` in your output.
    8. 采集来源需要填写数据信息来源的平台。
    9. 来源链接必须是真实存在的网址，且与数据内容相关。注意，你不必给出具体文件的链接，只需提供数据来源的大致网站主页即可。但你必须保证其链接是有效的。
    10. Ensure that you generate exactly {num_entries} entries, no more and no less.
    """

    # 添加自定义需求
    if custom_requirements:
        prompt += f"\n\nAdditional Requirements:\n{custom_requirements}"

    return prompt

############################################################################################################
# create_user_prompt_7 对 create_user_prompt_6 进行了修改，删除了对列名进行描述的部分
def create_user_prompt_7(input_data, main_category, sub_category, num_entries=5, custom_requirements=""):
    prompt = f"Here is the structure of the dataset '{sub_category}' under '{main_category}' with sample data:\n\n"
    
    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  Column: {col_name}, Value: {value}\n"
        prompt += "\n"

    prompt += f"""
    Please generate more data in the same structure and format, ensuring each column contains appropriate and realistic data. Maintain consistency with the provided examples.

    Output the generated data in the following JSON format. Here's an example of the expected output format:

    {{
        "generated_data": [
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            {{
                "column1": "value1",
                "column2": "value2",
                "column3": "value3",
                "column4": "value4",
                "column5": "value5",
                "column6": "value6",
                ...
            }},
            ...
        ]
    }}

    Please generate exactly {num_entries} new entries following this exact format. Ensure that:
    1. The JSON is valid and can be parsed.
    2. All numeric values are represented as numbers (not strings).
    3. String values are enclosed in double quotes.
    4. Date values are in the format "YYYY-MM-DD".
    5. The structure exactly matches the example provided.
    6. Generate realistic and diverse data for different entries.
    7. Do not include any markdown formatting such as ``` json or ``` in your output.
    8. 采集来源需要填写数据信息来源的平台。
    9. 来源链接必须是真实存在的网址，且与数据内容相关。注意，你不必给出具体文件的链接，只需提供数据来源的大致网站主页即可。但你必须保证其链接是有效的。
    10. Ensure that you generate exactly {num_entries} entries, no more and no less.
    """

    # 添加自定义需求
    if custom_requirements:
        prompt += f"\n\nAdditional Requirements:\n{custom_requirements}"

    return prompt

############################################################################################################
# create_user_prompt_8 是 create_user_prompt_7 的升级版本，强调了生成数据的多样性和真实性
def create_user_prompt_8(input_data, main_category, sub_category, num_entries=5, custom_requirements=""):
    prompt = f"You are augmenting a dataset about '{sub_category}' under the category of '{main_category}'. Here's a sample of the existing data:\n\n"
    
    prompt += "Sample data:\n\n"
    for row_idx, row in enumerate(input_data):
        prompt += f"Row {row_idx + 1}:\n"
        for col_name, value in row.items():
            prompt += f"  {col_name}: {value}\n"
        prompt += "\n"

    prompt += f"""
    Based on this sample, generate {num_entries} new entries that are diverse and realistic. Use your knowledge to:
    
    1. Vary the data realistically across different regions, time periods, or scenarios relevant to {sub_category}.
    2. Incorporate plausible trends or patterns that might exist in this type of data.
    3. Ensure numeric values are within realistic ranges for each field.
    4. Provide varied but credible sources for the data.
    5. If applicable, reflect recent developments or future projections in this field.

    Output the generated data in the following JSON format:

    {{
        "generated_data": [
            {{
                "column1": "value1",
                "column2": value2,
                "column3": "value3",
                ...
            }},
            ...
        ]
    }}

    Ensure that:
    1. The JSON is valid and can be parsed.
    2. Numeric values are represented as numbers, not strings.
    3. String values are enclosed in double quotes.
    4. Date values are in the format "YYYY-MM-DD".
    5. The structure exactly matches the example provided.
    6. '采集来源' contains plausible data sources or platforms.
    7. '来源链接' are real, existing website URLs related to the data content. Use general website homepages, not specific file links.
    8. Generate exactly {num_entries} entries, no more and no less.
    9. Do not include any markdown formatting in your output.
    """

    if custom_requirements:
        prompt += f"\n\nAdditional Requirements:\n{custom_requirements}"

    return prompt