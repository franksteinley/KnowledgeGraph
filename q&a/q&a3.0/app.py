from flask import Flask, request, jsonify, render_template
from query_parser import parse_question
from neo4j_connector import Neo4jConnector
import threading
import time

app = Flask(__name__)

# 初始化Neo4j连接
neo4j = Neo4jConnector(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="12345678"
)

# 用于存储并行结果的线程类
class QueryThread(threading.Thread):
    def __init__(self, method, question):
        threading.Thread.__init__(self)
        self.method = method
        self.question = question
        self.result = None
        self.cypher = None
        self.error = None
    
    def run(self):
        try:
            if self.method == "original":
                self.cypher = parse_question(self.question)
                if self.cypher:
                    self.result = neo4j.run_query(self.cypher)
                else:
                    self.error = "原有规则无法解析该问题"
            else:  # llm 方法
                from query_parser import generate_cypher_with_api
                self.cypher = generate_cypher_with_api(self.question)
                if self.cypher:
                    self.result = neo4j.run_query(self.cypher)
                else:
                    self.error = "大模型无法生成有效的Cypher查询"
        except Exception as e:
            self.error = f"{self.method}方法出错: {str(e)}"

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
        
        # 创建两个线程并行处理
        start_time = time.time()
        original_thread = QueryThread("original", question)
        llm_thread = QueryThread("llm", question)
        
        original_thread.start()
        llm_thread.start()
        
        # 等待线程完成
        original_thread.join()
        llm_thread.join()
        
        end_time = time.time()
        process_time = round((end_time - start_time) * 1000)  # 毫秒
        
        # 构建结果对象
        response = {
            "processing_time": f"{process_time}ms",
            "original": format_query_result(original_thread, question),
            "llm": format_query_result(llm_thread, question)
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': f'服务器错误: {str(e)}'})

def format_query_result(thread, question):
    """格式化查询结果"""
    result = {}
    
    if thread.error:
        result['error'] = thread.error
    elif not thread.cypher:
        result['message'] = "未生成Cypher查询"
    elif not thread.result:
        result['message'] = "未找到相关信息"
    else:
        result['cypher'] = thread.cypher
        # 提取简洁的文本结果
        answers = [item['result'] for item in thread.result if 'result' in item]
        
        if not answers:
            result['message'] = "未解析到有效结果"
        else:
            # 如果是列表类查询，转换成简单列表
            if any(keyword in question.lower() for keyword in ['有哪些', '哪些']):
                result['answer'] = '\n'.join(f"- {item}" for item in answers)
            else:
                result['answer'] = answers[0] if isinstance(answers, list) else answers
    
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)