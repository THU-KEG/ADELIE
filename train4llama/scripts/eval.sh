# Model_Path="../models/ADELIE-SFT"
Model_Path="/data1/qyj/ADELIE-DPO"
SCRIPTS_Path="/data1/qyj/ADELIE/scripts"
Output_DIR="saves/llama_v2_7B/full/ADELIE-DPO"
TEST_DIR="../unified_data/test_format/"
CUDA=7
    

CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/few-nerd-supervised.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/few-nerd-supervised.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample

python ${SCRIPTS_Path}/tasks/fewnerd/open_evaluate.py \
    --input_dir ${Output_DIR}/predict/fewshot/few-nerd-supervised.jsonl \
    >  ${Output_DIR}/predict/few-nerd-supervised_result.txt


CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/semeval.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/semeval.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample

python ${SCRIPTS_Path}/tasks/semeval/open_evaluate.py \
    --input_dir ${Output_DIR}/predict/fewshot/semeval.jsonl \
    >  ${Output_DIR}/predict/semeval_result.txt


CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/RichERE-eae.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/RichERE-eae.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample

python ${SCRIPTS_Path}/tasks/richere-eae/open_evaluation.py \
    --input_dir ${Output_DIR}/predict/fewshot/RichERE-eae.jsonl \
    >  ${Output_DIR}/predict/RichERE-eae_result.txt

CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/RichERE-ed.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/RichERE-ed.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample

python ${SCRIPTS_Path}/tasks/richere-ed/open_eval.py \
    --input_dir ${Output_DIR}/predict/fewshot/RichERE-ed.jsonl \
    >  ${Output_DIR}/predict/RichERE-ed_result.txt


CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/MATRES.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/MATRES.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample \

python ${SCRIPTS_Path}/tasks/matres/open_eval.py \
    --output_file ${Output_DIR}/predict/fewshot/MATRES.jsonl \
    >  ${Output_DIR}/predict/MATRES_result.txt

#================= OPEN IE =====================

CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/fewshot_test_history/ROBUST.jsonl \
    --output_file ${Output_DIR}/predict/fewshot/ROBUST.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample

python ${SCRIPTS_Path}/tasks/ROBUST/reformat_results_open.py \
    --input_dir ${Output_DIR}/predict/fewshot/ROBUST.jsonl

python ${SCRIPTS_Path}/tasks/ROBUST/src/robust_scorer.py \
    --pred_file ${SCRIPTS_Path}/tasks/ROBUST/result.json \
    >  ${Output_DIR}/predict/ROBUST_result.txt


#================= ondemand IE =====================
CUDA_VISIBLE_DEVICES=${CUDA} python eval/predict.py \
    --model_name_or_path ${Model_Path} \
    --input_files ${TEST_DIR}/zeroshot/ondemand.jsonl \
    --output_file ${Output_DIR}/predict/zeroshot/ondemand.jsonl \
    --batch_size 4 \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 0.01 \
    --do_sample \

python ${SCRIPTS_Path}/tasks/ondemandie/o_generate_evaluatefile.py \
    --input_dir ${Output_DIR}/predict/zeroshot/ondemand.jsonl \

python ${SCRIPTS_Path}/tasks/ondemandie/evaluation/rougel_for_content.py > ${Output_DIR}/predict/ondemand_content.txt

python ${SCRIPTS_Path}/tasks/ondemandie/evaluation/sim_for_header.py > ${Output_DIR}/predict/ondemand_header.txt