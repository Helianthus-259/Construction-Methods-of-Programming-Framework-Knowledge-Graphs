import os

from zhipuai import ZhipuAI
import json
import time
from tqdm import tqdm

from json_repair import repair_json


# 处理待提取的非结构化信息
def process_prompts(input_path,file_number,batch_requests):
        with open(input_path, 'r', encoding='utf-8') as f:
            unstructured_infos = json.load(f)

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

            try:
                batch_json = create_batch_json(prompt,file_number,idx+1)
                batch_requests.append(batch_json)
            except Exception as e:
                print(f"Error processing prompt: {e}")


def create_batch_json(prompt, file_number,idx):
    request = {
        "custom_id": f"request-{file_number}-{idx}",
        "method": "POST",
        "url": "/v4/chat/completions",
        "body": {
            #"model": "glm-4-plus",
            "model": "glm-4-air-0111",
            "messages": [
                {"role": "system",
                 "content": "You are an expert in extracting knowledge triples."},
                {"role": "user", "content": prompt}
            ],
            "do_sample": False,
            "stream": False,
            "response_format": {'type': 'json_object'},
            "max_tokens": 4095
        }
    }
    return request

if __name__ == "__main__":
    base_dir = "E:/Desktop_Documents/课程/毕业设计/代码知识抽取/javaParser/jjson/unstructured/spring-core_unstructured_prompts_split/"
    batch_requests = []
    begin_number = 94
    end_number = 104
    for i in range(begin_number,end_number):
        # 构造文件名编号，补零两位（01-99），三位（100-133）
        file_number = f"{i:02d}" if i <= 99 else str(i)
        file_name = f"spring-core_unstructured_prompts_{file_number}.json"
        input_path = os.path.join(base_dir, file_name)
        print("处理文件"+file_name)
        process_prompts(input_path, file_number,batch_requests)

    begin_file_number = f"{begin_number:02d}" if begin_number <= 99 else str(begin_number)
    end_file_number = f"{end_number-1:02d}" if end_number-1 <= 99 else str(end_number-1)
    # 确保输出目录存在
    knowledge_name = f"unstructured_knowledge_batch_requests_{begin_file_number}-{end_file_number}.jsonl"
    output_path = os.path.join('./batch/spring-core/', knowledge_name)
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)  # 自动创建目录
    # 将处理后的非结构化信息关系保存到 JSON 文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for request in batch_requests:
            json.dump(request, f, ensure_ascii=False)
            f.write("\n")  # 确保每个 JSON 对象占一行
    print("Batch文件生成完成！")