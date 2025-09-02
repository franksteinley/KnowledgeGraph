def parse_question(question):
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

# 改进的辅助函数
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