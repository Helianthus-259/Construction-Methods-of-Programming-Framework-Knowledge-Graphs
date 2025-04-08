import json
import os


def split_json_by_chunks(input_file, chunk_size=1000):
    """
    纯切分JSON文件工具（适用于内存足够的情况）

    :param input_file: 输入的JSON文件路径
    :param chunk_size: 每个分块的大小，默认1000
    """
    # 读取源文件
    with open(input_file, 'r', encoding='utf-8') as f:
        full_data = json.load(f)  # 整个JSON加载到内存

    if not isinstance(full_data, list):
        raise ValueError("输入文件必须是JSON数组格式")

    # 准备输出路径
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(os.path.dirname(input_file), f"{base_name}_split")
    os.makedirs(output_dir, exist_ok=True)

    class_chunk = []
    method_chunk = []
    for info in full_data:
        entity_type = info.get('entityType', '')
        if entity_type == "class":
            class_chunk.append(info)
        else:
            method_chunk.append(info)
    output_path = os.path.join(output_dir, f"{base_name}_class.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(class_chunk, f, indent=2, ensure_ascii=False)
    output_path = os.path.join(output_dir, f"{base_name}_method.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(method_chunk, f, indent=2, ensure_ascii=False)
    # 计算分块数量
    # total = len(full_data)
    # chunks = range(0, total, chunk_size)
    # print(f"总记录数: {total} | 分块数: {len(chunks)}")
    #
    # # 执行切分
    # for i, start in enumerate(chunks, 1):
    #     end = start + chunk_size
    #     chunk = full_data[start:end]
    #
    #     # 生成文件名（自动补零）
    #     output_path = os.path.join(output_dir, f"{base_name}_{i:02d}.json")
    #
    #     # 写入分块文件
    #     with open(output_path, 'w', encoding='utf-8') as f:
    #         json.dump(chunk, f, indent=2, ensure_ascii=False)
    #
    #     print(f"生成分块: {output_path} ({len(chunk)}条记录)")


if __name__ == "__main__":
    # 使用示例
    split_json_by_chunks(
        input_file="E:/Desktop_Documents/课程/毕业设计/代码知识抽取/javaParser/jjson/unstructured/spring-boot-main_unstructured_prompts.json",
        chunk_size=100
    )