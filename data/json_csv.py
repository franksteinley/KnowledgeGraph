import json
import csv
import os
import glob

# 确保end文件夹存在
end_folder = "end"
os.makedirs(end_folder, exist_ok=True)

# 遍历output文件夹中的所有JSON文件
json_files = glob.glob("output/*.json")

for json_file in json_files:
    try:
        # 读取JSON文件
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取文件名（不含路径）
        base_name = os.path.basename(json_file)
        
        # 创建对应的CSV文件名
        csv_file = os.path.join(end_folder, os.path.splitext(base_name)[0] + ".csv")
        
        # 如果是字典对象且需要展开
        if isinstance(data, dict):
            data = [data]
        
        # 只有数组格式可以处理
        if not isinstance(data, list):
            print(f"跳过 {json_file}: 非列表格式")
            continue
        
        # 确保数组中的元素是字典
        if data and not isinstance(data[0], dict):
            print(f"跳过 {json_file}: 数组元素非字典格式")
            continue
        
        # 写入CSV文件
        with open(csv_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # 写入表头（取第一个对象的键）
            writer.writerow(data[0].keys())
            
            # 写入数据行
            for row in data:
                writer.writerow(row.values())
        
        print(f"成功转换: {json_file} -> {csv_file}")
    
    except Exception as e:
        print(f"处理文件 {json_file} 时出错: {str(e)}")

print(f"\n转换完成! 共处理 {len(json_files)} 个文件，结果已保存到 {end_folder} 文件夹")