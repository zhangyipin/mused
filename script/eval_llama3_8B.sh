
LOGITS_INPUT_PATH="../data/test/test_prompt.jsonl"

BASE_RES_PATH="../eval_res"

NAME="llama8B_instruct_res_eval_sets"
OUTPUT_PATH="${BASE_RES_PATH}/${NAME}"
model_path="MODEL_PATH"

mkdir -p $OUTPUT_PATH
python ../src/infer_codes/llama3_8b/uf_sample_batch.py --input-path $LOGITS_INPUT_PATH --output-path "${OUTPUT_PATH}/final_prompts.jsonl" --model-path $model_path
res_path="${OUTPUT_PATH}/final_prompts.jsonl"
python ../src/codes/scores.py ${res_path} ${res_path}.score_res ${res_path}.report_res ${res_path}.report_res.xlsx


