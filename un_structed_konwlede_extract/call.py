import os

from zhipuai import ZhipuAI
import json
import time
from tqdm import tqdm

from json_repair import repair_json

# 调用智谱AI接口获取非结构化信息
def call_zhipu_ai(prompt, model='glm-4-air-0111'):
    for _ in range(3):  # 最多重试3次
        try:
            client = ZhipuAI(api_key="")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system",
                     "content": "You are an expert in extracting knowledge triples."},
                    {"role": "user", "content": prompt},
                ],
                do_sample=False,  # 关闭随机采样，确保稳定性
                stream=False,
                temperature=0.7,
                top_p=0.7,
                response_format={
                    'type': 'json_object'
                },
                max_tokens=4095
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"请求异常: {e}，重试中...")
            time.sleep(2)  # 等待2秒后重试
    return None

# 追加数据到JSON文件
def append_to_json_file(new_data, filename='unstructured_knowledge_graph.json'):
    if not new_data:
        return

    # 如果文件已存在，则读取旧数据并追加
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            if not isinstance(existing_data, dict) or "relationships" not in existing_data:
                existing_data = {"relationships": []}  # 如果结构不对，重新初始化
        except (json.JSONDecodeError, FileNotFoundError):
            existing_data = {"relationships": []}  # 解析失败则重新初始化
    else:
        existing_data = {"relationships": []}  # 如果文件不存在，初始化为空

    # 追加新数据
    existing_data["relationships"].extend(new_data["relationships"])

    # 写回文件
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)
    print(f"加入 {len(new_data['relationships'])} 条关系到 {filename}")

def clean_json_response(raw_response):
    # """清理智普AI返回的JSON字符串"""
    # # 去除Markdown代码块标记
    # cleaned = raw_response.strip().strip('`').lstrip('json').strip()
    # # 处理可能的转义字符（针对包含代码示例的特殊情况）
    # #cleaned = cleaned.replace('\\"', '"').replace('\\\\', '\\')
    # return cleaned

    """清理智普AI返回的JSON字符串（仅去除头尾的 ```json 和 ``` 标记）"""
    # 去除首尾空白字符
    cleaned = raw_response.strip()

    # 精准去除开头的 ```json（含大小写兼容）
    if cleaned.lower().startswith('```json'):
        # 计算标记长度（避免大小写不一致问题）
        prefix_len = len('```json')
        cleaned = cleaned[prefix_len:].lstrip()  # 同时清理标记后的换行或空格

    # 精准去除结尾的 ```
    if cleaned.endswith('```'):
        cleaned = cleaned[:-3].rstrip()  # 直接截断最后3个字符

    return cleaned


# 处理待提取的非结构化信息
def process_prompts(input_path,file_number):
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            unstructured_infos = json.load(f)

        merged_result = {"relationships": []}
        new_results = []
        # tqdm 进度条，显示当前处理的文件名
        for idx, info in enumerate(tqdm(unstructured_infos, desc=f"Processing {file_number}", unit="item")):
            entity_id = info.get('entityId', '')
            entity_type = info.get('entityType', '')
            code = info.get('code', '')
            comment = info.get('comment', '')

            if not entity_id or not entity_type:
                print("缺少必要字段，跳过该条数据")
                continue

            prompt = (
                f"You are a top-tier algorithm designed to extract structured information from code and comments to build a knowledge graph.\n\n"
                f"#### **Knowledge Graph Schema**\n"
                f"This knowledge graph follows the structure below:\n\n"
                f"##### **Entity Types**\n"
                f"1. **API Semantic Knowledge**:\n"
                f"   - **apiFunction**: The functionality a class or method may be associated with (e.g., lazy loading).\n"
                f"   - **useConstraint**: Constraints on using the `apiFunction` (e.g., circular aliases are prohibited).\n"
                f"   - **useScenario**: The usage scenario of the `apiFunction` (e.g., multiple aliases for a single name).\n"
                f"   - **useSampleCode**: The complete sample code for using the `apiFunction` (a full example must be generated, e.g., `package com.healthMgr.common.email; import java.xxxx; public class OneClass {{ // specific code }}`).\n"
                f"   - **class**: A class potentially associated with the given class or method (e.g., `org.springframework.core.SimpleAliasRegistryTests`).\n"
                f"   - **relatedConceptInterpretation**: An explanation of related concepts.\n"
                f"   - **designPrincipleInterpretation**: An explanation of the design principles of the class or method.\n\n"
                f"##### **Relationship Types**\n"
                f"1. **API Semantic Knowledge**:\n"
                f"   - **haveFuntion**: Links a **class/method** to an **apiFunction**.\n"
                f"   - **constrained_by**: Links a **class/method** to a **useConstraint**.\n"
                f"   - **applied_to**: Links a **class/method** to a **useScenario**.\n"
                f"   - **have**: Links a **class/method** to a **useScenario/useSampleCode/relatedConceptInterpretation/designPrincipleInterpretation**.\n"
                f"   - **associated_with**: Links a **class/method** to another **class/method**.\n\n"
                f"#### **Task Instructions**\n"
                f"1. Parse the input JSON and extract all possible entities, including `entityId` itself and its associated `apiFunction`, `useConstraint`, `useScenario`, `useSampleCode`, `relatedConceptInterpretation`, and `designPrincipleInterpretation`.\n"
                f"2. Ensure the extraction of **as many valid entities as possible** based on the provided input.\n"
                f"3. Construct relationships strictly following the **defined relationship types** and **ensuring correct directionality**.\n"
                f"4. Return only the `relationships` result without any additional explanations or intermediate outputs.\n"
                f"5. Explore as many apiFunctions as possible, allowing for errors but being comprehensive.\n"
                f"6. Associate as many possible classes as possible, allowing for errors but being comprehensive.\n"
                f"7. RelatedConceptInterpretation and designPrincipleInterpretation need detailed descriptions as soon as possible.\n"
                #f"8. Generate a complete useSampleCode for each apiFunction whenever possible.\n"
                f"8. UseSampleCode must be complete, do not copy my sample directly to me.\n"
                f"9. Create an additional entity based on the input (Its name = entityId, its type = entityType).\n\n"
                f"#### **Output Format**\n"
                f"Return a JSON object with the key `relationships`, containing a list of extracted relationships, each with the following structure:\n"
                f"```json\n"
                f"{{\n"
                f"  \"head\": \"HEAD_ENTITY_NAME\",\n"
                f"  \"head_type\": \"HEAD_ENTITY_TYPE\",\n"
                f"  \"relation\": \"RELATION_TYPE\",\n"
                f"  \"tail\": \"TAIL_ENTITY_NAME\",\n"
                f"  \"tail_type\": \"TAIL_ENTITY_TYPE\"\n"
                f"}}\n"
                f"```\n\n"
                f"#### **Input Example**\n"
                f"```json\n"
                f"{{\n"
                f"    \"entityId\": \"{entity_id}\",\n"
                f"    \"entityType\": \"{entity_type}\",\n"
                f"    \"code\": \"{code}\",\n"
                f"    \"comment\": \"{comment}\"\n"
                f"}}\n"
                f"```\n\n"
                f"Follow the rules above and provide only the `relationships` output."
            )

            model_result = call_zhipu_ai(prompt)
            if model_result:
                #print(model_result)
                # 解析 JSON
                cleaned_json = clean_json_response(model_result)
                repaired_json = repair_json(cleaned_json)
                #print(repaired_json)
                parsed_result = json.loads(repaired_json)
                #print(parsed_result)
                if "relationships" in parsed_result and isinstance(parsed_result["relationships"], list):
                    merged_result["relationships"].extend(parsed_result["relationships"])

            #print(merged_result)
        print(merged_result)
        # 确保输出目录存在
        knowledge_name = f"unstructured_knowledge_graph_{file_number}.json"
        output_path = os.path.join('./json/spring-core/', knowledge_name)
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)  # 自动创建目录
        # 将处理后的非结构化信息关系保存到 JSON 文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_result, f, ensure_ascii=False, indent=4)
        print(knowledge_name+"的非结构化知识图谱生成完成！")
    except FileNotFoundError:
        print("未找到 unstructured_prompts.json 文件，请先运行 Java 代码生成该文件。")
    except json.JSONDecodeError:
        print("JSON 文件解析错误，请检查文件格式。")
    except Exception as e:
        print(f"发生未知错误: {e}")

if __name__ == "__main__":
    base_dir = "../structed_konwlede_extract/javaParser/json/unstructured/spring-core_unstructured_prompts_split/"
    for i in range(1,134):
        # 构造文件名编号，补零两位（01-99），三位（100-133）
        file_number = f"{i:02d}" if i <= 99 else str(i)
        file_name = f"spring-core_unstructured_prompts_{file_number}.json"
        input_path = os.path.join(base_dir, file_name)
        print("处理文件"+file_name)
        process_prompts(input_path, file_number)