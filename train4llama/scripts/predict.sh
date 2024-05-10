for p in {1..5}
do
    CUDA_VISIBLE_DEVICES=0 python ../eval/predict.py \
    --model_name_or_path ../../models/ADELIE-SFT \
    --input_files ../../unified_data/train_mixture/mix_vDPO.jsonl \
    --output_file ../../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_$p/mix_vDPO.jsonl \
    --batch_size 4 \
    --use_vllm \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
    --temperature 1.0 \
    --do_sample
done