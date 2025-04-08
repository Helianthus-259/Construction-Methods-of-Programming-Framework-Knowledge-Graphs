from neo4j import GraphDatabase
import json
import os

class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self.driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
        self.session = self.driver.session()

    def insert_relationship(self, node1, node2, relationship_type):
        """
        插入关系到 Neo4j 数据库
        """
        node1_label = node1['label'].replace(" ", "")  # 处理标签中的空格
        node2_label = node2['label'].replace(" ", "")
        relationship_type = relationship_type.replace(" ", "_")  # 关系类型避免空格

        # Cypher 查询
        query = (
            f"MERGE (a:`{node1_label}` {{name: $name1}}) "
            f"MERGE (b:`{node2_label}` {{name: $name2}}) "
            f"MERGE (a)-[:`{relationship_type}`]->(b)"
        )

        # 执行查询
        self.session.run(query, name1=node1['name'], name2=node2['name'])

    def close(self):
        """
        关闭数据库连接
        """
        self.session.close()
        self.driver.close()


def read_relationships_from_json(file_path):
    """
    读取 JSON 文件并返回 relationships 列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data.get('relationships', [])  # 防止 JSON 没有 'relationships' 键时报错
    except Exception as e:
        print(f"❌ 读取文件 {file_path} 失败: {e}")
        return []


def insert_all_relationships_from_folder(folder_path, neo4j_db):
    """
    遍历文件夹中的所有 JSON 文件，并将所有 relationships 插入到 Neo4j
    """
    if not os.path.exists(folder_path):
        print(f"❌ 目录 {folder_path} 不存在！请检查路径是否正确")
        return

    json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
    if not json_files:
        print(f"⚠️ 目录 {folder_path} 中没有找到 JSON 文件")
        return

    print(f"📂 在 {folder_path} 目录中找到 {len(json_files)} 个 JSON 文件，开始处理...")

    for filename in json_files:
        file_path = os.path.join(folder_path, filename)
        print(f"📄 处理文件: {file_path}")

        relationships = read_relationships_from_json(file_path)
        if not relationships:
            print(f"⚠️ 文件 {filename} 没有有效的关系数据，跳过...")
            continue

        print(f"✅ {filename} 包含 {len(relationships)} 条关系数据，开始插入 Neo4j...")

        for entry in relationships:
            try:
                # node1 = {"name": entry['head'], "label": entry['headType']}
                # node2 = {"name": entry['tail'], "label": entry['tailType']}
                # 将键访问和关系插入全部放入 try 块
                node1 = {"name": entry['head'], "label": entry['head_type']}
                node2 = {"name": entry['tail'], "label": entry['tail_type']}
                relation = entry['relation']

                neo4j_db.insert_relationship(node1, node2, relation)
            except KeyError as e:
                # 明确捕获键缺失错误
                print(f"❌ 跳过无效三元组: 缺失关键键 {e}，数据: {entry}")
            except Exception as e:
                # 保留其他异常处理（如数据库插入失败）
                print(f"❌ 插入关系失败: {entry}，错误: {e}")

        print(f"✅ 文件 {filename} 处理完成！\n")

    print("🎉 所有文件处理完成，Neo4j 数据已更新！")


# ✅ 创建 Neo4j 连接
neo4j_db = Neo4jDatabase(uri="bolt://localhost:7687", user="neo4j", password="a12345678")

# ✅ 设置 JSON 文件夹路径
#folder_path = 'E:/Desktop_Documents/课程/毕业设计/代码知识抽取/unstructured_parser/json/spring-core'
folder_path = 'E:/Desktop_Documents/课程/毕业设计/官方教程知识抽取'

# ✅ 遍历文件夹并插入所有 JSON 文件中的数据
insert_all_relationships_from_folder(folder_path, neo4j_db)

# ✅ 关闭数据库连接
neo4j_db.close()
