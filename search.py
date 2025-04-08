from neo4j import GraphDatabase
import json

class Neo4jConnector:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_connected_subgraph_by_name(self, node_name, id_property="name"):
        """
        根据节点名称获取全关系类型连通子图

        参数：
            node_name: 目标节点的名称值
            id_property: 名称对应的属性名（默认为'name'）

        返回：
            nodes: 连通子图中的所有节点列表
            relationships: 连通子图中的所有关系列表
        """
        cypher_query = """
        MATCH (startNode {%(prop)s: $node_name})
        CALL apoc.path.subgraphAll(startNode, {
            labelFilter: null,    // 允许所有节点标签
            minLevel: 0,          // 包含起始节点
            maxLevel: 2          // 无限深度
        })
        YIELD nodes, relationships
        RETURN nodes, relationships
        """ % {'prop': id_property}

        with self.driver.session() as session:
            result = session.run(cypher_query, node_name=node_name)
            record = result.single()

            if not record:
                return [], []

            # 提取节点和关系
            nodes = []
            for node in record["nodes"]:
                node_data = dict(node.items())
                node_data["labels"] = list(node.labels)  # 保留标签
                nodes.append(node_data)

            relationships = [{
                "type": rel.type,
                "start": rel.start_node[id_property],
                "end": rel.end_node[id_property],
                "properties": dict(rel.items())
            } for rel in record["relationships"]]

            return nodes, relationships


# 使用示例
if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "a12345678"

    connector = Neo4jConnector(uri, user, password)

    # 查询名为"Server01"的节点连通子图
    target_name = "org.springframework.core.log.LogDelegateFactory#getCompositeLog(Log,Log,Log)"
    #target_name =  "fallback mechanism"
    nodes, rels = connector.get_connected_subgraph_by_name(target_name)

    print(f"找到 {len(nodes)} 个节点和 {len(rels)} 条关系（包含所有关系类型）")

    # 打印所有节点（前3个展示详情）
    print("\n==== 节点列表 ====")
    print(f"共 {len(nodes)} 个节点:")
    for i, node in enumerate(nodes[:]):
        print(f"[节点{i + 1}] 名称: {node['name']}, 标签: {node['labels']}, 属性: {node}")
    # if len(nodes) > 3:
    #     print(f"（其余 {len(nodes) - 3} 个节点省略详情）")

    # 打印所有关系（完整列表）
    print("\n==== 关系列表 ====")
    if len(rels) == 0:
        print("未找到任何关系")
    else:
        for rel in rels:
            print(f"· 关系类型: {rel['type']}")
            print(f"  起点: {rel['start']}")
            print(f"  终点: {rel['end']}")
            if rel['properties']:
                print(f"  属性: {rel['properties']}")
            print("-" * 30)

    # ========== 新增JSON导出功能 ==========
    # 构建节点名称到首标签的映射
    node_type_map = {
        node['name']: node['labels'][0] if node['labels'] else 'Unlabeled'
        for node in nodes
    }

    # 转换关系为指定格式
    formatted_relationships = []
    for rel in rels:
        entry = {
            "head": rel['start'],
            "head_type": node_type_map.get(rel['start'], 'Unknown'),
            "relation": rel['type'],
            "tail": rel['end'],
            "tail_type": node_type_map.get(rel['end'], 'Unknown')
        }
        formatted_relationships.append(entry)

    # 保存为JSON文件
    output_file = "relationships.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_relationships, f, ensure_ascii=False, indent=2)

    print(f"\n已导出 {len(formatted_relationships)} 条关系到 {output_file}")

    connector.close()