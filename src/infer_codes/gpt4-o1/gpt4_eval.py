
import requests
import time
import json
import glob
import random
import threading
import queue
import os
import re
from diskcache import Cache
import tqdm
MAX_API_RETRY=10
import openai
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import traceback

from template import *
import argparse

from openai import OpenAI

parser = argparse.ArgumentParser()
parser.add_argument("--input-path", type=str, required=True)
parser.add_argument("--output-path", type=str, required=True)
parser.add_argument("--model", type=str, default="gpt-4o")
parser.add_argument("--gpt-key", type=str, default="")
args = parser.parse_args()

TNUM = 10
LIMIT = 200000
EVAL_LOOP_PER_CASE = 1

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

input_path = args.input_path
data = read_jsonl(input_path)

threads = []
lock = threading.Lock()
buffer = queue.Queue(maxsize=TNUM * 100000)
results = []

class OpenAIApiException(Exception):
    def __init__(self, msg, error_code):
        self.msg = msg
        self.error_code = error_code

class OpenAIApiProxy():
    def __init__(self, api_key="sk-xxxxxx", model='gpt-4o'):

        self.client = OpenAI(api_key=api_key)

    def call(self, model_name, messages, headers={}, max_tokens=2048):
        print('---messages:', messages)
        if 'o1' in model_name:
            response = self.client.chat.completions.create(
              #model="gpt-4o-mini",
              model=model_name,
              messages=messages
            )
        else:
            response = self.client.chat.completions.create(
              #model="gpt-4o-mini",
              model=model_name,
              max_tokens = max_tokens,
              temperature = 0.001
              messages=messages
            )

        print('-----response:', response)
        return response.choices[0].message.content

cache = Cache('./cache')
if args.gpt_key != "":
    proxy = OpenAIApiProxy(api_key=args.gpt_key)
else:
    proxy = OpenAIApiProxy()

def get_query(row):
    if row["response_type"] == 0:
        query = prove_instructions + input_template.format(row["prompt"])
    else:
        query = check_instructions + input_template.format(row["prompt"])
    return query

def get_prompt(query):
    messages = [
        {"role": "user", "content": query}
    ]
    return messages

def gpt_eval(query, loop, model="gpt-4o", max_tokens=2048, debug=False, try_count=3, use_cache=True):
    try:
        messages = get_prompt(query)
        cache_key = '{}\t{}\t{}'.format(model, query, loop)
        if use_cache and cache_key in cache:
            score = cache[cache_key]
            return score
        resp = proxy.call(model, messages, max_tokens=max_tokens)
        cache[cache_key] = resp 

        return resp
    except:
        try_count += 1
        if try_count >= 1:
            raise
        print("try_count ", try_count)
        #time.sleep(1 * try_count)
        return gpt_eval(query, loop, model, max_tokens, debug, try_count)

def query_eval(query, loop=2, use_cache=True):
    #request
    for i in range(loop):
        eval_res = gpt_eval(query, loop, model=args.model)
        return eval_res
    return None

def producer():
    size = 0
    
    pbar = tqdm.tqdm(size, desc=f'producer {threading.current_thread().name}')
    idx = 0

    for each in data:
        buffer.put((idx, each, pbar))
        idx += 1

def consumer():
    while not buffer.empty():
        index, each, pbar = buffer.get()
        try:
            query = get_query(each)
            res = query_eval(query, loop=EVAL_LOOP_PER_CASE)
            if res is None:
                each["gen"] = None
                continue
            else:
                each["gen"] = res
            with lock:
                global results
                results.append(each)
        except Exception as e:
            traceback.print_exc()
            print("expectation", e)
            print(f'{threading.current_thread().name} Error {each}')
        finally:
            buffer.task_done()
            pbar.update(1)

if 1:
    producer()
    for i in range(TNUM):
        threads.append(threading.Thread(target=consumer))
    for c_thread in threads:
        c_thread.start()

    for c_thread in threads:
        c_thread.join()

    output_path = args.output_path
    with open(output_path, "w") as file:
        for d in results:
            json_data = json.dumps(d, ensure_ascii=False)
            file.write(json_data + "\n")
    print("write file: ", args.output_path)
