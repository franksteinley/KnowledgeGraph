from flask import Flask, request, jsonify, render_template
from query_parser import parse_question
from neo4j_connector import Neo4jConnector

app = Flask(__name__)

# 初始化Neo4j连接
neo4j = Neo4jConnector(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678"
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({'error': '问题不能为空'})
        
        # 解析问题生成Cypher
        cypher_query = parse_question(question)
        
        if not cypher_query:
            return jsonify({'error': '暂不支持该类型的问题'})
        
        # 执行查询
        results = neo4j.run_query(cypher_query)
        
        if not results:
            return jsonify({'result': '未找到相关信息'})
        
        return jsonify({'result': results})
    
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)