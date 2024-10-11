from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import random
import glob
import sys
import os
import math

import argparse
from template import prove_instructions, check_instructions, input_template

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, required=True)
parser.add_argument("--output-path", type=str, required=True)
parser.add_argument("--model-path", type=str, required=True)
parser.add_argument("--task-type", type=str, default='json')
args = parser.parse_args()


def get_query(row, task_type):
    if task_type == 'nature':
        return row["prompt"]
    if row["response_type"] == 0:
        query = prove_instructions + input_template.format(row["prompt"])
    else:
        query = check_instructions + input_template.format(row["prompt"])
    return query.strip()

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

# model_path='/data2/rlhf/liufeng/checkpoint/actor_model/llama3_8b'
model_path=args.model_path

# 1: 加载模型、分词器
model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype=torch.bfloat16)
tokenizer = AutoTokenizer.from_pretrained(model_path, use_fast=False, trust_remote_code=True, padding_side='left')
tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = model.config.eos_token_id

data = read_jsonl(args.input_path)
output_path = args.output_path

if output_path and os.path.exists(output_path):
    exist_data = read_jsonl(output_path)
    if len(exist_data) > 0:
        #exist_prompts = set([str(item["messages"][0]["content"]) for item in exist_data])
        exist_prompts = set([str(item["prompt"]) for item in exist_data])
        print("已处理： ",len(exist_prompts))
        new_data = []
        for item in data:
            if "prompt" in item:
                prompt = item["prompt"]
            else:
                prompt = item["conversations"][0]["value"]
            if prompt not in exist_prompts:
                new_data.append(item)
        print("待处理： ",len(new_data))
        data = new_data

batch_size = 32
with open(output_path, 'a') as w_f:
    batch_count = math.ceil(1.0*len(data) / batch_size)
    for i in range(batch_count):
        batch = data[i*batch_size: (i + 1)*batch_size]
        chat_list = []
        for d in batch:
            if "prompt" in d:
                prompt = d["prompt"]
            else:
                prompt = d["conversations"][0]["value"]

            chat = [
                {
                    "role": "user",
                    "content": get_query(d, args.task_type)
                }
            ]
            chat_list.append(chat)

        # 2: 使用对话模板
        formatted_chat = tokenizer.apply_chat_template(chat_list, tokenize=False, add_generation_prompt=True, padding=True)
        # print("formatted_chat:", formatted_chat)

        # 3: 将对话内容转为token (也可以在上一步直接开启tokenize=True)
        inputs = tokenizer(formatted_chat, return_tensors="pt", padding=True, truncation=True)
        # inputs = tokenizer(chat, return_tensors="pt", add_special_tokens=False)

        # 把tokens转移到GPU或者CPU上
        # print("Tokenized inputs:\n", inputs)
        #'''
        inputs = {key: tensor.to(model.device) for key, tensor in inputs.items()}
        # print("Tokenized inputs:\n", inputs)

        # 4: 使用模型生成一段文本
        outputs = model.generate(**inputs, max_new_tokens=2048, do_sample=True, temperature=0.3, top_k=50, top_p=0.85)
        # print("Generated tokens:\n", outputs)


        # 5: 把生成结果从离散token变为文本
        decoded_output = tokenizer.batch_decode(outputs, skip_special_tokens=True)
        # decoded_output = tokenizer.decode(outputs[0][inputs['input_ids'].size(1):], skip_special_tokens=True)
        # print("Decoded output:\n", decoded_output)
        #'''
        for j in range(len(batch)):
            d = batch[j]
            curr_prompt = get_query(d, args.task_type)
            '''
            print('-------------------------')
            print('decoded_output[j]:', decoded_output[j])
            print('-------------------------')
            print('curr_prompt:', curr_prompt)
            print('-------------------------')
            print('find_res:', decoded_output[j].find(curr_prompt))
            print('-------------------------')
            '''
            #d['gen'] = decoded_output[j].removeprefix("user\n\n" + curr_prompt + "assistant\n\n")
            d['gen'] = decoded_output[j].split('assistant\n\n')[1]
            w_f.write(json.dumps(d, ensure_ascii=False) + '\n')
            w_f.flush()
        #break
