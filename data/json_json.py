import json
import os
import glob
import re

def extract_triples(input_path, output_path):
    # 确保输出目录存在
    os.makedirs(output_path, exist_ok=True)
    
    # 定义匹配三元组的正则表达式模式
    pattern = r'\[\s*"([^"]+)"\s*,\s*"([^"]+)"\s*,\s*"([^"]+)"\s*\]'
    
    # 遍历输入目录所有JSON文件
    for input_file in glob.glob(os.path.join(input_path, '*.json')):
        try:
            print(f"开始处理: {input_file}")
            
            # 读取文件内容为纯文本
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 使用正则表达式查找所有三元组
            triples = []
            matches = re.finditer(pattern, content)
            
            for match in matches:
                start_node, relations, end_node = match.groups()
                triples.append({
                    "start_node": start_node,
                    "relations": relations,
                    "end_node": end_node
                })
            
            print(f"发现 {len(triples)} 个三元组")
            
            # 构建输出文件路径
            filename = os.path.basename(input_file)
            output_file = os.path.join(output_path, filename)
            
            # 写入输出文件
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(triples, f, ensure_ascii=False, indent=2)
            
            print(f"成功写入: {output_file}")
            
        except Exception as e:
            print(f"处理文件 {input_file} 时出错: {str(e)}")
            continue

if __name__ == "__main__":
    input_folder = "input"
    output_folder = "output"
    
    extract_triples(input_folder, output_folder)
    print("\n所有文件处理完成!")