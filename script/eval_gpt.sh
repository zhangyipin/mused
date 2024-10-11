LOGITS_INPUT_PATH="../data/test/test_prompt.jsonl"

BASE_RES_PATH="../eval_res"

model_name="gpt-4o"
OUTPUT_PATH="${BASE_RES_PATH}/${model_name}"

gpt_key="sk-M9FGh6L84mlefKKgAa88B0882c0f4a85B7352dD38602225e"

mkdir -p $OUTPUT_PATH

res_path="${OUTPUT_PATH}/final_prompts.jsonl"
python ../eval_codes/gpt4-o1/gpt4_eval.py --model $model_name --input-path $LOGITS_INPUT_PATH --output-path "${res_path}" --gpt-key $gpt_key

python ../codes/scores.py ${res_path} ${res_path}.score_res ${res_path}.report_res ${res_path}.report_res.xlsx

