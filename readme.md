# 知识工程大作业：人工智能知识图谱构建与问答系统

本项目是《知识工程》课程的期末大作业，旨在构建一个基于《人工智能知识体系》电子书的知识图谱，并实现知识问答和推理功能。项目包括知识图谱Schema设计、实体关系抽取、数据处理、Neo4j可视化及问答系统开发。

## 目录结构
```bash
.
├── UsageGuide/                  # 实验流程和指南文档，请务必阅读
├── schema/                      # 本体和关系设计模式
├── ReferenceDocuments/          # 知识来源文档
├── import/                      # 用于导入Neo4j的CSV文件
│   ├── entity/                  # 实体CSV文件
│   └── relation/                # 关系CSV文件
├── data/                        # 原始数据与自动化脚本
│   ├── data (csv)/               # 关系数据（CSV格式）
│   ├── data (json)/              # 关系数据（JSON格式）
│   └── 自动化数据处理脚本/        # Python数据处理脚本
├── q&a/                         # 知识图谱问答系统代码
│   ├── frontend/                # 前端代码
│   └── backend/                 # 后端代码
├── 知识工程大作业.pptx            # 展示汇报PPT
└── README.md                    # 本文件
```

## 📁 UsageGuide - 实验流程指南
**必须阅读**这些文档以了解完整构建流程：
- `知识图谱构建及可视化功能使用指南.pdf`：详细步骤包括数据抽取、图谱构建和neo4j可视化
- `知识图谱问答系统使用说明.pdf`：构建的基于前后端的双反馈的知识图谱问答系统
- `基于RAGFlow的推理问答功能使用指南.pdf`：基于RAGFlow的推理问答功能构建和使用说明
**我们实现了两种方式的知识问答模式，基于RAGFlow的更是包含了我们的无数心血**



## 📁 schema - 本体设计模式
以下文件理解知识图谱结构：
- `本体设计模式.xlsx`：包含实体类型定义（如`AdaptiveRepresentation`、`CognitiveControl`）
- `关系类型设计.xlsx`：包含关系类型（如`isTypeOf`、`relatedTo`）

实体类型表示例：
| name:ID | type | 
|---------|------|
| SUS得分 | AdaptiveRepresentation |
| 丘脑后部 | AdaptiveRepresentation |
| 个体认知 | AdaptiveRepresentation |

## 📁 ReferenceDocuments - 知识来源
存放知识抽取的原始文档（理解数据基础）：
- 20篇核心文档（30万字），包括：
  - 《人工智能知识体系》电子书章节
  - 知网学术论文（如《人工智能的适应性表征认知理论》）
  - 学科书籍节选（如《脑科学导论》）
  - 等


## 📁 import - 导入数据
包含处理后的可直接导入Neo4j的文件：
- **entity目录**：实体CSV文件（按类型分类）
  - `AdaptiveRepresentation.csv`
  - `CognitivePsychology.csv`
  - `ArtificialIntelligence.csv`
- **relation目录**：关系CSV文件
  - `relation.csv`（包含start_id, relation, end_node字段）

关系表示例：
| start | relations | end node |
|-------|-----------|----------|
| 注意吸 | isTypeOf | 认知加工程 |
| 识别聚焦 | isTypeOf | 信息决策程 |
| 关联推理 | isTypeOf | 语文班解程 |

## 📁 data - 原始数据与脚本
包含原始数据和自动化处理脚本：
```bash
data/
├── data (csv)/     # CSV格式关系数据
├── data (json)/    # JSON格式关系数据
└── 自动化数据处理脚本/
    ├── json_csv.py      # JSON转CSV
    ├── json_json.py       # 数据规范化提取
    └── apitry.py     # 缺失实体补全
```




## 📁 q&a - 问答系统
完整问答系统代码：
```bash
q&a/
├── q&a1.0           # 初代版本
└── q&a3.0           # 最终版本
```


## 使用流程
1. **数据准备**：阅读`ReferenceDocuments`中的文档
2. **数据处理**：运行data目录中的脚本
   ```bash
   python data/自动化数据处理脚本/json_to_csv.py --input data(json)/9-1.json --output data(csv)/9-1.csv
   ```
3. **图谱构建**：将import目录文件导入Neo4j
4. **问答系统**：启动q&a后端服务
   ```bash
   cd q&a3.0
   python app.py
   ```

## 注意事项
1. **必须阅读**UsageGuide中的指南文档，包含：
   - OneKE部署的血泪教训（服务器配置等）
   - 数据处理常见错误解决方案
   - 问答系统调优技巧

2. **数据处理脚本**：
   - 先运行JSON→CSV转换
   - 再执行实体关系校验
   - 最后进行数据标准化

3. **问答系统依赖**：
   - Ollama本地模型服务运行在端口11434
   - Neo4j数据库需保持运行（默认端口7687）

## 常见问题
**Q: 实体导入Neo4j失败？**
> A: 检查entity文件中ID是否唯一，确保relation文件中引用的ID存在

**Q: 大模型API调用失败？**
> A: 1. 确认Ollama服务已启动 
>    2. 检查`http://host.docker.internal:11434`可访问
>    3. 查看RAGFlow模型配置

**Q: 如何扩展知识库？**
> A: 1. 在ReferenceDocuments添加新文档
>    2. 重新运行数据处理脚本
>    3. 更新import目录文件
>    4. 重新导入Neo4j

**项目组成员**：
>   蒋茜 3023244322
>   马佳一 3023244328
>   邵玺冉 3023244327
>   张婉毓 3023244338  
**最后更新**：2025年6月30日