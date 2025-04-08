import json

# 读取 .jsonl 结果文件
input_jsonl = "./batch/spring-core/batch_results.jsonl"  # 你的 .jsonl 结果文件
all_relationships = {"relationships": []}  # 用于存储所有 relationships

with open(input_jsonl, "r", encoding="utf-8") as f:
    for line in f:
        try:
            # 解析 JSON 行
            data = json.loads(line.strip())

            # 获取 response -> body -> choices -> message -> content
            content_str = data["response"]["body"]["choices"][0]["message"]["content"].strip()

            # 解析 content 为 JSON
            content_json = json.loads(content_str)
            # 提取 relationships
            try:
                relationships = content_json.get("relationships", [])
                all_relationships["relationships"].extend(relationships)
            except Exception as e:
                all_relationships["relationships"].extend(content_json)

        except json.JSONDecodeError as e:
            print(f"JSON 解析错误: {e}")
        except KeyError as e:
            print(f"缺少关键字段: {e}")

# 输出解析的 relationships
print(json.dumps(all_relationships, indent=2, ensure_ascii=False))

# 可选：将结果保存为新的 JSON 文件
output_json = "./batch/spring-core/parsed_relationships.json"
with open(output_json, "w", encoding="utf-8") as f:
    json.dump(all_relationships, f, indent=2, ensure_ascii=False)

print(f"✅ 解析完成，已保存到 {output_json}")
