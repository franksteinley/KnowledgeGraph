import csv
import os
import dashscope
import random  # 添加random模块用于随机选择
from http import HTTPStatus
import time

# 设置API密钥
dashscope.api_key = "sk-96e73caaf6fc46bfa34dbab4051fe1b7"

# 预定义的类别列表
CATEGORIES = [
    "Cognition", "Intelligence", "Knowledge", "Memory", "Learning", "Language", 
    "Consciousness", "Attention", "Perception", "Thinking", "CognitivePsychology",
    "CognitiveNeuroscience", "CognitiveLinguistics", "ArtificialIntelligence",
    "CognitiveComputing", "Neurolinguistics", "Psycholinguistics", "Sociolinguistics",
    "SymbolicProcessingModel", "ConnectionistModel", "AdaptiveRepresentation",
    "CognitiveArchitecture", "KnowledgeGraph", "EventGraph", "CognitiveReasoningFramework",
    "CognitiveControl", "ExecutiveFunction", "fMRI", "ERP", "EyeTracking", "EEG",
    "MEG", "PET", "fNIRS", "DeepLearning", "Time", "Figure"
]

def read_entities_from_csv(file_path):
    """从CSV文件中提取唯一的实体"""
    entities = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头
        for row in reader:
            if len(row) > 0:
                entities.add(row[0].strip())  # 第一列实体
            if len(row) > 1:
                entities.add(row[1].strip())  # 第二列实体
    return sorted(entities)  # 返回排序后的唯一实体列表

def classify_entity(entity):
    """使用大模型API对实体进行分类"""
    prompt = f"""
    请将以下术语分类到以下类别之一，只返回类别的英文名称：
    {', '.join(CATEGORIES)}
    
    术语: {entity}
    
    要求:
    1. 只返回类别的英文名称
    2. 名称必须与上述列表中的完全一致
    3. 不要添加任何额外文字或解释
    """
    
    try:
        response = dashscope.Generation.call(
            'qwen1.5-32b-chat',
            messages=[{'role': 'user', 'content': prompt}],
            result_format='message',
        )
        
        if response.status_code == HTTPStatus.OK:
            # 提取并清理模型返回的类别
            raw_category = response.output.choices[0].message.content
            # 移除可能的额外空格和句点
            cleaned_category = raw_category.strip().rstrip('.').strip()
            return cleaned_category
        else:
            print(f"API请求失败: 实体 {entity} - 状态码 {response.status_code}")
            return None
    except Exception as e:
        print(f"API调用异常: 实体 {entity} - {str(e)}")
        return None

def process_entities(entities):
    """处理所有实体并返回分类结果"""
    categorized_entities = {category: [] for category in CATEGORIES}
    categorized_entities["Unknown"] = []  # 未知类别
    
    total = len(entities)
    for i, entity in enumerate(entities, 1):
        print(f"处理实体: {entity} ({i}/{total})")
        
        category = classify_entity(entity)
        if category and category in CATEGORIES:
            categorized_entities[category].append(entity)
        else:
            print(f"未知或无效分类: {entity} -> {category if category else '无响应'}")
            categorized_entities["Unknown"].append(entity)
        
        # API限流控制
        time.sleep(0.5)  # 每秒1次请求
    
    # 将Unknown类别的实体随机分配到其他类别
    if categorized_entities["Unknown"]:
        print(f"将 {len(categorized_entities['Unknown'])} 个未知实体随机分配到其他类别...")
        valid_categories = [cat for cat in CATEGORIES if cat != "Unknown"]
        for entity in categorized_entities["Unknown"]:
            # 随机选择一个有效类别
            random_category = random.choice(valid_categories)
            categorized_entities[random_category].append(entity)
        
        # 清空Unknown类别
        categorized_entities["Unknown"] = []
    
    return categorized_entities

def save_to_csv(categorized_entities, output_dir="outcsv"):
    """将分类结果保存到CSV文件"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for category, entities in categorized_entities.items():
        if not entities:  # 跳过空类别
            continue
            
        # 替换Windows文件名无效字符
        safe_category = category.replace(':', '').replace('/', '_')
        file_path = os.path.join(output_dir, f"{safe_category}.csv")
        
        with open(file_path, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["name:ID"])  # 第一行写表头
            for entity in entities:
                writer.writerow([entity])

def main():
    # 步骤1: 从CSV文件中读取实体
    entities = read_entities_from_csv('relations.csv')
    print(f"发现唯一实体: {len(entities)}个")
    
    # 步骤2: 对实体进行分类
    categorized_entities = process_entities(entities)
    
    # 步骤3: 保存结果到CSV文件
    save_to_csv(categorized_entities)
    print("处理完成! 结果已保存到outcsv目录")

if __name__ == '__main__':
    main()