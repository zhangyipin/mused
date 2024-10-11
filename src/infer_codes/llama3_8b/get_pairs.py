import numpy as np
import random
import glob
import json
import argparse
from template import prove_instructions, check_instructions, input_template

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, required=True)
parser.add_argument("--output-path", type=str, required=True)
parser.add_argument("--response-key", type=str, default="gen")
parser.add_argument("--task-type", type=str, default="natural")

args = parser.parse_args()


def read_jsonl(file_name):
    json_data = []
    with open(file_name, 'r', encoding='utf-8') as f:
        for line in f:
            e_d = json.loads(line)
            json_data.append(e_d)
    return json_data

def save_jsonl(data, file_name):
    with open(file_name, "w") as file:
        for d in data:
            json_data = json.dumps(d, ensure_ascii=False)
            file.write(json_data + "\n")

def get_query(row, task_type=None):
    if task_type == 'nature':
        return row["prompt"]
    if task_type == 'json':
        if row["response_type"] == 0:
            query = prove_instructions + input_template.format(row["prompt"])
        else:
            query = check_instructions + input_template.format(row["prompt"])
        return query.strip()
    raise ValueError("wrong task type:", task_type)

def check_pair(s1, s2):
    is_valid = True
    if s1["result_right"] < s2["result_right"]:
        is_valid = False
    if s1["right_step"] < s2["right_step"]:
        is_valid = False
    if s1["extra_step"] > s2["extra_step"]:
        is_valid = False
    if s1["noise_step"] > s2["noise_step"]:
        is_valid = False
    if s1["wrong_step"] > s2["wrong_step"]:
        is_valid = False
    return is_valid

def get_pair(one_data, task_type):
    pairs = []

    res = []
    for d in one_data.values():
        scores = d["score_dict"]
        if not scores["is_valid"]:
            scores["wrong_step"] = 100
            scores["extra_step"] = 100
            scores["noise_step"] = 100
        all_score = scores["result_right"] + scores["right_step"] - scores["extra_step"] - scores["noise_step"] - scores["wrong_step"]
        res.append((d, all_score))
    res.sort(key=lambda x: x[1], reverse=True)
    for i in range(len(res)-1):
        for j in range(i+1, len(res)):
            if res[i][1] == res[j][1]:
                continue
            is_valid = check_pair(res[i][0]["score_dict"], res[j][0]["score_dict"])
            if is_valid:
                nd = {
                    "conversations": [
                        {
                            "from": "human",
                            "value": res[i][0]["prompt"]
                        }
                    ],
                    "chosen": res[i][0][args.response_key],
                    "rejected": res[j][0][args.response_key],
                    "能力": "逻辑推理",
                    "领域": "演绎推理",
                    "属性": task_type
                }
                pairs.append(nd)

    count = len(pairs)
    for d in pairs:
        d["count"] = count
    return pairs

if __name__ == "__main__":
    input_path = args.input_path
    output_path = args.output_path
    task_type = args.task_type

    prompt_dic = {}
    for f in glob.glob(input_path):
        print(f)
        data = read_jsonl(f)
        for d in data:
            prompt = d["prompt"]
            if task_type != 'natural':
                d["orignal_prompt"] = prompt
                d["prompt"] = get_query(d, task_type)

            if prompt not in prompt_dic:
                prompt_dic[prompt] = {}
            response = d["gen"]
            if response not in prompt_dic[prompt]:
                prompt_dic[prompt][response] = d

    pair_data = []
    for k, v in prompt_dic.items():
        pair_data.extend(get_pair(v, task_type))
    save_jsonl(pair_data, args.output_path)
