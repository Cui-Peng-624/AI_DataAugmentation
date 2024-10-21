import json
import re

class OutputValidator:
    def __init__(self, expected_columns):
        self.expected_columns = expected_columns

    def preprocess_output(self, output):
        # 移除可能的 markdown 格式
        output = re.sub(r'```json\s*', '', output)
        output = re.sub(r'\s*```', '', output)
        return output.strip()

    def is_valid(self, output):
        try:
            # 预处理输出
            preprocessed_output = self.preprocess_output(output)
            
            # 尝试解析JSON
            data = json.loads(preprocessed_output)
            
            # 检查是否包含 "generated_data" 键
            if "generated_data" not in data:
                return False

            generated_data = data["generated_data"]
            
            # 检查是否至少有5个条目
            # if len(generated_data) < 5:
            #     return False

            # 检查每个条目是否包含所有预期的列
            for entry in generated_data:
                if not all(col in entry for col in self.expected_columns):
                    return False

                # 检查数值是否真的是数字类型
                # for col in self.expected_columns:
                #     if col in ["健身房人数", "健身工作室数量", "健身俱乐部数量", "健身渗透率", 
                #                "经常参加体育锻炼的人数", "人均体育场馆面积", "健身休闲产业规模", "马拉松参加人数"]:
                #         if not isinstance(entry[col], (int, float)):
                #             return False

            return True
        except json.JSONDecodeError:
            return False

    def save_invalid_output(self, output, filename):
        with open(filename, 'a', encoding='utf-8') as f:
            f.write("\n--- Invalid Output ---\n")
            f.write(output)
            f.write("\n--- End of Invalid Output ---\n")
    # # 或者选择这个
    # def save_invalid_output(self, output, filename):
    #     with open(filename, 'a', encoding='utf-8') as f:
    #         f.write("\n---\n")  # 添加分割线，表示每次的错误分隔
    #         f.write(output)



