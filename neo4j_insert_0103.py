from neo4j import GraphDatabase
import json


class Neo4jDatabase:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self.driver = GraphDatabase.driver(self._uri, auth=(self._user, self._password))
        self.session = self.driver.session()

    def insert_relationship(self, node1, node2, relationship_type):
        # Remove spaces from labels and relationship types
        node1_label = node1['label'].replace(" ", "")
        node2_label = node2['label'].replace(" ", "")
        relationship_type = relationship_type.replace(" ", "_")

        # Cypher query with formatted labels and relationship type
        query = (
            "MERGE (a:`{}` {{name: $name1}}) "
            "MERGE (b:`{}` {{name: $name2}}) "
            "MERGE (a)-[:`{}`]->(b)"
        ).format(node1_label, node2_label, relationship_type)

        # Run the query with parameters
        self.session.run(query, name1=node1['name'], name2=node2['name'])

    def close(self):
        self.session.close()
        self.driver.close()


def read_relationships_from_json(file_path):
    # Read the JSON file and extract the relationships
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data['relationships']  # Access the relationships array


# Read relationships from the JSON file
relationships = read_relationships_from_json('../代码知识抽取/unstructured_parser/json/spring-core/unstructured_knowledge_graph_94-103.json')

# Create an instance of Neo4jDatabase
neo4j_db = Neo4jDatabase(uri="bolt://localhost:7687", user="neo4j", password="a12345678")

# Insert nodes and relationships based on the data
for entry in relationships:
    try:
        # node1 = {"name": entry['head'], "label": entry['headType']}
        # node2 = {"name": entry['tail'], "label": entry['tailType']}
        node1 = {"name": entry['head'], "label": entry['head_type']}
        node2 = {"name": entry['tail'], "label": entry['tail_type']}
        neo4j_db.insert_relationship(node1, node2, entry['relation'])

    except KeyError as e:
        # 明确捕获键缺失错误
        print(f"❌ 跳过无效三元组: 缺失关键键 {e}，数据: {entry}")
    except Exception as e:
        # 保留其他异常处理（如数据库插入失败）
        print(f"❌ 插入关系失败: {entry}，错误: {e}")

# Close the connection
neo4j_db.close()
