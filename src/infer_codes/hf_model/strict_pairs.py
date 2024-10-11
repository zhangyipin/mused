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
    strict_key = []
    # if s1["right_step"] < 0.5:
    #     return False

    if s1["result_right"] < s2["result_right"]:
        is_valid = False
    elif s1["result_right"] > s2["result_right"]:
        strict_key.append("result_right")
    if s1["right_step"] < s2["right_step"]:
        is_valid = False
    elif s1["right_step"] > s2["right_step"]:
        strict_key.append("right_step")
    if s1["extra_step"] > s2["extra_step"]:
        is_valid = False
    elif s1["extra_step"] < s2["extra_step"]:
        strict_key.append("extra_step")
    if s1["noise_step"] > s2["noise_step"]:
        is_valid = False
    elif s1["noise_step"] < s2["noise_step"]:
        strict_key.append("noise_step")
    if s1["wrong_step"] > s2["wrong_step"]:
        is_valid = False
    elif s1["wrong_step"] < s2["wrong_step"]:
        strict_key.append("wrong_step")
    return is_valid, strict_key

def get_pair(one_data, task_type, pair_keys, right_dic):
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
            is_valid, keys = check_pair(res[i][0]["score_dict"], res[j][0]["score_dict"])
            if is_valid:
                level = res[0][0]["level"]
                if level not in right_dic:
                    right_dic[level] = {
                        "right_small_equ": 0,
                        "right_small_not_equ": 0,
                        "right_large_equ": 0,
                        "right_large_not_equ": 0
                    }
                if res[i][0]["score_dict"]["right_step"] * 1.0 / res[i][0]["score_dict"]["global_right_count"] < 0.5:
                    if res[i][0]["score_dict"]["right_step"] > res[j][0]["score_dict"]["right_step"]:
                        right_dic[level]["right_small_not_equ"] += 1
                    else:
                        right_dic[level]["right_small_equ"] += 1
                else:
                    if res[i][0]["score_dict"]["right_step"] > res[j][0]["score_dict"]["right_step"]:
                        right_dic[level]["right_large_not_equ"] += 1
                    else:
                        right_dic[level]["right_large_equ"] += 1
                
                for key in keys:
                    if level not in pair_keys:
                        pair_keys[level] = {"total_pair": 0}
                    pair_keys[level]["total_pair"] += 1
                    if key not in pair_keys[level]:
                        pair_keys[level][key] = 0
                    pair_keys[level][key] += 1
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

    pair_keys = {}
    right_dic = {}
    pair_data = []
    for k, v in prompt_dic.items():
        res = get_pair(v, task_type, pair_keys, right_dic)
        pair_data.extend(res)
    print("all count:", len(pair_data))
    print("keys:", pair_keys)
    print("right count:", right_dic)
    # save_jsonl(pair_data, args.output_path)
