import requests
import json

# 通义千问API配置
API_KEY = "sk-39c6026f9ad74ce29cd5c60a0b0452e0"
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 可用关系类型列表
RELATIONSHIPS = [
    "hasPart", "isTypeOf", "simulates", "relatedTo", "studies", "basedOn", 
    "influences", "isBasisFor", "hasFunction", "aimsTo", "isOriginOf", "differsFrom",
    "focusesOn", "appliedIn", "provides", "preparesFor", "playsRoleIn", "characterizedBy",
    "hasRelationship", "involves", "abstracts", "researches", "targets", "isResultOf",
    "foundedIn", "catalyzed", "includes", "examines", "controls", "enables", "integrates",
    "describes", "emergedFrom", "isDefinedAs", "isCoreOf", "isSuperiorityBasis", "contrastsWith",
    "requires", "appliesTo", "influencedBy", "hasResearchScope", "formsBasis", "creates",
    # 这里只列出部分关系作为示例，实际应包含全部提供的关系类型
]

def parse_question(question):
    """原有规则解析方法"""
    return parse_with_original_rules(question)

def generate_cypher_with_api(question):
    """调用大模型API生成Cypher查询"""
    try:
        # 构建提示词
        relationships_str = "\n".join(RELATIONSHIPS[:20])  # 只显示部分避免过长
        prompt = f"""
        你是一个Neo4j知识图谱查询生成器。用户的问题是：{question}
        
        请根据问题生成合适的Cypher查询语句，并遵守以下规则：
        1. 只能使用以下关系类型：
        {relationships_str}
        （完整列表包含{len(RELATIONSHIPS)}种关系）
        2. 只返回Cypher语句，不要包含其他任何内容
        3. 所有节点都有'name'属性用于匹配
        4. 结果使用'result'作为返回值的别名
        
        现在请为以下问题生成Cypher查询:
        {question}
        """
        
        # 调用API
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-turbo",
            "input": {
                "messages": [
                    {"role": "system", "content": "你是一个专业的Cypher查询生成器"},
                    {"role": "user", "content": prompt}
                ]
            },
            "parameters": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }
        
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        
        # 提取生成的Cypher语句
        data = response.json()
        cypher = data["output"]["text"].strip()
        
        # 验证生成的Cypher是否安全
        if "MATCH" in cypher and "RETURN" in cypher and "AS result" in cypher:
            return cypher
        
        return None
        
    except Exception as e:
        print(f"API调用错误: {str(e)}")
        return None

def parse_with_original_rules(question):
    question_lower = question.lower()
    
    # 实体属性查询 (示例: "人工智能是什么?")
    if any(keyword in question_lower for keyword in ['是什么', '是谁', '定义', '含义']):
        entity = extract_entity(question)
        if entity:
            return f"MATCH (n) WHERE n.name = '{entity}' RETURN n.定义 AS result"
    
    # 直接关系查询 (示例: "人工智能和技术科学有什么关系?")
    if any(keyword in question_lower for keyword in ['关系', '关联', '联系']):
        entities = extract_two_entities(question)
        if len(entities) == 2:
            return f"""
            MATCH (a)-[r]->(b)
            WHERE a.name = '{entities[0]}' AND b.name = '{entities[1]}'
            RETURN type(r) AS result
            """
    
    # 路径查询 (示例: "基于贝叶斯决策的分类方法是哪种?")
    if any(keyword in question_lower for keyword in ['基于', '通过', '使用']):
        print('ok')
        entity = extract_entity(question)
        if entity:
            # 修复关系方向：方法基于理论
            return f"""
            MATCH (method)-[basedOn]->(theory)
            WHERE theory.name = '{entity}'
            RETURN method.name AS result
            UNION
            MATCH (method)-[basedOn*..2]->(theory)
            WHERE theory.name = '{entity}'
            RETURN method.name AS result
            """
    
    # 列表类查询 (示例: 神经网络有哪些应用)
    if any(keyword in question_lower for keyword in ['有哪些', '哪些']):
        category = extract_entity(question)
        if category:
            # 修复错误：使用category而非entity
            return f"MATCH (n)-[basedOn]-(application) WHERE n.name = '{category}' RETURN application.name AS result"
    
    return None

# 辅助函数保持不变
def extract_entity(question):
    """简化的实体提取逻辑（移除非相关部分）"""
    # 移除标点和常见问题关键词
    stop_phrases = ['是什么', '有什么关系', '有哪些', '定义', '基于', '哪种', '的技术','的方法','的实体','应用']
    cleaned = question
    for phrase in stop_phrases:
        cleaned = cleaned.replace(phrase, '')
    
    # 移除"的"字开头的部分
    if cleaned.startswith('的'):
        cleaned = cleaned[1:]
    
    return cleaned.replace('?', '').replace('？', '').strip()

def extract_two_entities(question):
    """提取两个实体（改进版）"""
    cleaned = extract_entity(question)
    
    if '和' in cleaned:
        parts = [part.strip() for part in cleaned.split('和')]
        if len(parts) >= 2:
            second_entity = parts[1].replace('关系', '').replace('关联', '').strip()
            return [parts[0], second_entity]
    elif '与' in cleaned:
        parts = [part.strip() for part in cleaned.split('与')]
        if len(parts) >= 2:
            second_entity = parts[1].replace('关系', '').replace('关联', '').strip()
            return [parts[0], second_entity]
    
    return []