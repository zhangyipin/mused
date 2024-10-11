import json
import sys
import numpy as np
import pandas as pd


def convert_model_generate_res_to_struct_json(generate_str, start_id = 0):
    if start_id >= len(generate_str):
        return None, ''
    generate_str = generate_str[start_id:]
    start = generate_str.find('{')
    stack = ['{']

    for i in range(start + 1, len(generate_str)):
        if generate_str[i] == '{':
            stack.append('{')
        elif generate_str[i] == '}':
            stack.pop()
            if not stack:
                end = i + 1  
                break

    json_str = generate_str[start:end]
    data = json.loads(json_str)
    return data, json_str

def cal_score(model_json_res, reference_answer, j_d):
    '''
    if this step decay new node add one score
    '''
    response_type = j_d['response_type']
    all_noise_node_list = j_d['all_noise_node_list']
    # print('response_type:', response_type)
    #target = j_d['target']
    #reverse_target = j_d['reverse_target']
    middle_decay = []
    all_reach_set = set()

    noise_step = 0
    extra_step = 0
    right_step = 0
    wrong_step = 0
    result_right = 0
    global_right_count = 0
    for each_step in model_json_res['steps']:
        subject = each_step['format_conclusion']['Subject']
        predicate = each_step['format_conclusion']['Predicate']
        type_s = each_step['format_conclusion']['type']
        # print('each_step:', each_step)
        search_key = 'error'
        try:
            search_key = ','.join([subject, predicate])
        except Exception as e:
            pass
        if search_key not in reference_answer:
            if subject in all_noise_node_list or predicate in all_noise_node_list:
                noise_step += 1
            else:
                wrong_step += 1
            continue
        else:
            if reference_answer[search_key]['type'] == type_s:
                if len(reference_answer[search_key]['middle_decay']) == 0:
                    continue
                middle_decay.append(set(reference_answer[search_key]['middle_decay']))
                all_reach_set.add(','.join([subject, predicate, type_s]))
            else:
                wrong_step += 1
    middle_decay.sort(key=lambda x: len(x))
    all_decay_set = set()
    for each_decay_set in middle_decay:
        new_nodes = each_decay_set - all_decay_set
        if len(new_nodes) == 0:
            extra_step += 1
        else:
            right_step += 1
            all_decay_set = all_decay_set | each_decay_set

    root_node = j_d['syllogistic_idx_dic']["1"]
    r_s = root_node['Subject']
    r_p = root_node['Predicate']
    r_type = root_node['type']
    if ','.join([r_s, r_p]) in reference_answer:
        global_right_count = len(reference_answer[','.join([r_s, r_p])]['middle_decay'])
    else:
        global_right_count = len(reference_answer[','.join([r_p, r_s])]['middle_decay'])
    if response_type == 0:
        r_s_p_k = ','.join([r_s, r_p, r_type])
        if r_s_p_k in all_reach_set:
            result_right = 1
    elif response_type == 1:
        if model_json_res['result'] == 'Correct':
            result_right = 1
    elif response_type == 2:
        if model_json_res['result'] == 'Wrong':
            result_right = 1

    if global_right_count == 0:
        print(j_d)

    return {'right_step': right_step, 'extra_step': extra_step, 'noise_step': noise_step, 'wrong_step': wrong_step, 'result_right': result_right, 'global_right_count': global_right_count}

def is_valid_response_json(model_json_res):
    is_valid = True
    try:
        for each_step in model_json_res['steps']:
            subject = each_step['format_conclusion']['Subject']
            predicate = each_step['format_conclusion']['Predicate']
            type_s = each_step['format_conclusion']['type']
        #result = model_json_res['result'] 
    except Exception as e:
        # print(e)
        is_valid = False
    return is_valid

def merge_to_excel_dict(target_dict, key_list, value_list=None, none_str=''):
    
    if value_list is None:
        value_list = ['' for i in range(len(key_list))]     
        value_list[0] = none_str
    for key_s, value_s in zip(key_list, value_list):
        if key_s not in target_dict:
            target_dict[key_s] = []
        try:
            value_s = float(value_s)
        except Exception as e:
            print(e)
        target_dict[key_s].append(value_s)
    return target_dict

def summary_all_score(j_d_list, report_file, excel_report_file):

    result_level_res_dict = {}
    step_level_res_dict = {}
    wrong_step_level_res_dict = {}
    noise_step_level_res_dict = {}
    extra_step_level_res_dict = {}
    valid_level_res_dict = {}
    all_level_res_dict = {}



    result_noise_count_res_dict = {}
    step_noise_count_res_dict = {}
    wrong_step_noise_count_res_dict = {}
    noise_step_noise_count_res_dict = {}
    extra_step_noise_count_res_dict = {}
    valid_noise_count_res_dict = {}
    all_noise_count_res_dict = {}

    result_response_type_res_dict = {}
    step_response_type_res_dict = {}
    wrong_step_response_type_res_dict = {}
    noise_step_response_type_res_dict = {}
    extra_step_response_type_res_dict = {}
    valid_response_type_res_dict = {}
    all_response_type_res_dict = {}


    result_entity_type_res_dict = {}
    step_entity_type_res_dict = {}
    wrong_step_entity_type_res_dict = {}
    noise_step_entity_type_res_dict = {}
    extra_step_entity_type_res_dict = {}
    valid_entity_type_res_dict = {}
    all_entity_type_res_dict = {}

    result_res_list = []
    step_res_list = []
    wrong_step_res_list = []
    noise_step_res_list = []
    extra_step_res_list = []
    valid_res_list = []
    all_res_list = []
    to_excel_dict = {}

    for j_d in j_d_list:
        level = j_d['level']
        response_type = j_d['response_type']
        entity_type = j_d['entity_type']
        noise_node_count = j_d['noise_node_count']
        #noise_node_count = 10
        task_type = 'Prove'

        if response_type != 0:
            task_type = 'judgment'
            
            
        score_dict = j_d['score_dict']
        right_step = score_dict['right_step']
        extra_step = score_dict['extra_step']
        noise_step = score_dict['noise_step']
        wrong_step = score_dict['wrong_step']
        result_right = score_dict['result_right']
        is_valid = score_dict['is_valid']
        valid_score = 0
        if is_valid:
            valid_score = 1.0
        global_right_count = score_dict['global_right_count']

        step_score = float(right_step) / float(global_right_count)
        all_score = step_score + result_right
        final_score = result_right

        if level not in result_level_res_dict:
            result_level_res_dict[level] = []
            step_level_res_dict[level] = []
            wrong_step_level_res_dict[level] = []
            noise_step_level_res_dict[level] = []
            extra_step_level_res_dict[level] = []
            valid_level_res_dict[level] = []
            all_level_res_dict[level] = []


        if noise_node_count not in result_noise_count_res_dict:
            result_noise_count_res_dict[noise_node_count] = []
            step_noise_count_res_dict[noise_node_count] = []
            wrong_step_noise_count_res_dict[noise_node_count] = []
            noise_step_noise_count_res_dict[noise_node_count] = []
            extra_step_noise_count_res_dict[noise_node_count] = []
            valid_noise_count_res_dict[noise_node_count] = []
            all_noise_count_res_dict[noise_node_count] = []


        if task_type not in result_response_type_res_dict:
            result_response_type_res_dict[task_type] = []
            step_response_type_res_dict[task_type] = []
            wrong_step_response_type_res_dict[task_type] = []
            noise_step_response_type_res_dict[task_type] = []
            extra_step_response_type_res_dict[task_type] = []
            valid_response_type_res_dict[task_type] = []
            all_response_type_res_dict[task_type] = []


        if entity_type not in result_entity_type_res_dict:
            result_entity_type_res_dict[entity_type] = []
            step_entity_type_res_dict[entity_type] = []
            wrong_step_entity_type_res_dict[entity_type] = []
            noise_step_entity_type_res_dict[entity_type] = []
            extra_step_entity_type_res_dict[entity_type] = []
            valid_entity_type_res_dict[entity_type] = []
            all_entity_type_res_dict[entity_type] = []

        result_level_res_dict[level].append(float(result_right))
        step_level_res_dict[level].append(float(step_score))
        wrong_step_level_res_dict[level].append(float(wrong_step))
        noise_step_level_res_dict[level].append(float(noise_step))
        extra_step_level_res_dict[level].append(float(extra_step))
        valid_level_res_dict[level].append(float(valid_score))
        all_level_res_dict[level].append(float(all_score))

        result_response_type_res_dict[task_type].append(float(result_right))
        step_response_type_res_dict[task_type].append(float(step_score))
        wrong_step_response_type_res_dict[task_type].append(float(wrong_step))
        noise_step_response_type_res_dict[task_type].append(float(noise_step))
        extra_step_response_type_res_dict[task_type].append(float(extra_step))
        valid_response_type_res_dict[task_type].append(float(valid_score))
        all_response_type_res_dict[task_type].append(float(all_score))

        result_entity_type_res_dict[entity_type].append(float(result_right))
        step_entity_type_res_dict[entity_type].append(float(step_score))
        wrong_step_entity_type_res_dict[entity_type].append(float(wrong_step))
        noise_step_entity_type_res_dict[entity_type].append(float(noise_step))
        extra_step_entity_type_res_dict[entity_type].append(float(extra_step))
        valid_entity_type_res_dict[entity_type].append(float(valid_score))
        all_entity_type_res_dict[entity_type].append(float(all_score))

        result_noise_count_res_dict[noise_node_count].append(float(result_right))
        step_noise_count_res_dict[noise_node_count].append(float(step_score))
        wrong_step_noise_count_res_dict[noise_node_count].append(float(wrong_step))
        noise_step_noise_count_res_dict[noise_node_count].append(float(noise_step))
        extra_step_noise_count_res_dict[noise_node_count].append(float(extra_step))
        valid_noise_count_res_dict[noise_node_count].append(float(valid_score))
        all_noise_count_res_dict[noise_node_count].append(float(all_score))
 
        result_res_list.append(float(result_right))
        step_res_list.append(float(step_score))
        wrong_step_res_list.append(float(wrong_step))
        noise_step_res_list.append(float(noise_step))
        extra_step_res_list.append(float(extra_step))
        valid_res_list.append(float(valid_score))
        all_res_list.append(float(all_score))
    excel_head_list = ['Key', 'Count', 'step_score', 'result_score', 'intent_score', 'all_score', '|', 'wrong_step_count', 'noise_step_count', 'extra_step_count'] 
    with open(report_file, 'w') as w_f:

        w_f.write('\t'.join(excel_head_list) + '\n') 
        w_f.write('----Level----\n')
        to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=None, none_str='Level_res')
        for k, v in sorted(result_level_res_dict.items(), key=lambda item: item[0]):
            result_score = np.mean(result_level_res_dict[k])
            step_score = np.mean(step_level_res_dict[k])
            all_score = np.mean(all_level_res_dict[k])
            wrong_step_score = np.mean(wrong_step_level_res_dict[k])
            noise_step_score = np.mean(noise_step_level_res_dict[k])
            extra_step_score = np.mean(extra_step_level_res_dict[k])
            valid_score = np.mean(valid_level_res_dict[k])

            res_list = [str(k), str(len(step_level_res_dict[k])), str(step_score), str(result_score), str(valid_score), str(all_score), '|' , str(wrong_step_score), str(noise_step_score), str(extra_step_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')

        w_f.write('----Question_type-----\n')
        to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=None, none_str='Question_type_res')
        for k, v in sorted(result_response_type_res_dict.items(), key=lambda item: item[0]):

            result_score = np.mean(result_response_type_res_dict[k])
            step_score = np.mean(step_response_type_res_dict[k])
            wrong_step_score = np.mean(wrong_step_response_type_res_dict[k])
            noise_step_score = np.mean(noise_step_response_type_res_dict[k])
            extra_step_score = np.mean(extra_step_response_type_res_dict[k])
            valid_score = np.mean(valid_response_type_res_dict[k])
            all_score = np.mean(all_response_type_res_dict[k])

            res_list = [str(k), str(len(all_response_type_res_dict[k])), str(step_score), str(result_score), str(valid_score), str(all_score), '|' , str(wrong_step_score), str(noise_step_score), str(extra_step_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')


        w_f.write('----Entity_type-----\n')
        to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=None, none_str='Entity_type_res')
        for k, v in sorted(result_entity_type_res_dict.items(), key=lambda item: item[0]):

            result_score = np.mean(result_entity_type_res_dict[k])
            step_score = np.mean(step_entity_type_res_dict[k])
            wrong_step_score = np.mean(wrong_step_entity_type_res_dict[k])
            noise_step_score = np.mean(noise_step_entity_type_res_dict[k])
            extra_step_score = np.mean(extra_step_entity_type_res_dict[k])
            valid_score = np.mean(valid_entity_type_res_dict[k])
            all_score = np.mean(all_entity_type_res_dict[k])

            res_list = [str(k), str(len(all_entity_type_res_dict[k])), str(step_score), str(result_score), str(valid_score), str(all_score), '|' , str(wrong_step_score), str(noise_step_score), str(extra_step_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')


        w_f.write('----Noise_count----\n')
        to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=None, none_str='Noise_count_res')
        for k, v in sorted(result_noise_count_res_dict.items(), key=lambda item: item[0]):
            result_score = np.mean(result_noise_count_res_dict[k])
            step_score = np.mean(step_noise_count_res_dict[k])
            all_score = np.mean(all_noise_count_res_dict[k])
            wrong_step_score = np.mean(wrong_step_noise_count_res_dict[k])
            noise_step_score = np.mean(noise_step_noise_count_res_dict[k])
            extra_step_score = np.mean(extra_step_noise_count_res_dict[k])
            valid_score = np.mean(valid_noise_count_res_dict[k])

            res_list = [str(k), str(len(step_noise_count_res_dict[k])), str(step_score), str(result_score), str(valid_score), str(all_score), '|' , str(wrong_step_score), str(noise_step_score), str(extra_step_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')
        

        w_f.write('----All-----\n')
        to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=None, none_str='ALL_res')
        if 1:
            result_score = np.mean(result_res_list)
            step_score = np.mean(step_res_list)
            wrong_step_score = np.mean(wrong_step_res_list)
            noise_step_score = np.mean(noise_step_res_list)
            extra_step_score = np.mean(extra_step_res_list)
            valid_score = np.mean(valid_res_list)
            all_score = np.mean(all_res_list)

            res_list = [str('ALL'), str(len(step_res_list)), str(step_score), str(result_score), str(valid_score), str(all_score), '|' , str(wrong_step_score), str(noise_step_score), str(extra_step_score)]
            w_f.write('\t'.join(res_list) + '\n')
            to_excel_dict = merge_to_excel_dict(to_excel_dict, excel_head_list, value_list=res_list, none_str='')
    df = pd.DataFrame(to_excel_dict)
    df.to_excel(excel_report_file, index=False)

        

def process(res_file, score_file, report_file, excel_report_file):
    j_d_list = []
    with open(res_file, 'r') as f, open(score_file, 'w') as w_f:
        for line in f:
            j_d = json.loads(line)
            json_str = ''
            try_count = 0
            start_idx = 0
            model_json_res = None
            while not is_valid_response_json(model_json_res) and try_count < 5:
                try:
                    model_json_res, json_str = convert_model_generate_res_to_struct_json(j_d['gen'], start_idx)
                    # print(is_valid_response_json(model_json_res))
                    # print(json_str)
                    start_idx += len(json_str)
                except Exception as e: 
                    pass
                try_count += 1
                if try_count > 5:
                    break
            # print('model_json_res:', model_json_res)
            # print('----------')
            if is_valid_response_json(model_json_res):
                score_dict = cal_score(model_json_res, j_d['reference_answer'], j_d)
                score_dict['is_valid'] = True
                j_d['score_dict'] = score_dict
            else:
                j_d['score_dict'] = {'right_step': 0, 'extra_step': 0, 'noise_step': 0, 'wrong_step': 0, 'result_right': 0, 'is_valid': False, 'global_right_count': 100}

            w_f.write(json.dumps(j_d, ensure_ascii=False) + '\n')            
            j_d_list.append(j_d)
    summary_all_score(j_d_list, report_file, excel_report_file)



if __name__ == '__main__':
    model_res_file = sys.argv[1]
    score_file = sys.argv[2]
    report_file = sys.argv[3]
    excel_report_file = sys.argv[4]
    process(model_res_file, score_file, report_file, excel_report_file)
