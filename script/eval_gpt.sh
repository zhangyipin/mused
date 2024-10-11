LOGITS_INPUT_PATH="../data/test/test_prompt.jsonl"

BASE_RES_PATH="../eval_res"



gpt_key="sk-xxxxx"
model_name="gpt-4o"
#model_name="o1-preview"
#model_name="o1-mini"

OUTPUT_PATH="${BASE_RES_PATH}/${model_name}"

mkdir -p $OUTPUT_PATH

res_path="${OUTPUT_PATH}/final_prompts.jsonl"
python ../src/infer_codes/gpt/gpt4_eval.py --model $model_name --input-path $LOGITS_INPUT_PATH --output-path "${res_path}" --gpt-key $gpt_key

python ../src/codes/scores.py ${res_path} ${res_path}.score_res ${res_path}.report_res ${res_path}.report_res.xlsx

