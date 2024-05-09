CUDA_VISIBLE_DEVICES=3 python eval/predict.py \
    --model_name_or_path /data2/ph/Alignment_on_IE_Models/rate_0.2 \
    --input_files /data1/qyj/Alignment_on_IE_tasks/unified_data/train_mixture/mix_vDPO.jsonl \
    --output_file results/llama-base-7b/full/rate_0.2/mix_vDPO.jsonl \
    --batch_size 4 \
    --use_vllm \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
   --temperature 0

CUDA_VISIBLE_DEVICES=3 python eval/predict.py \
    --model_name_or_path /data2/ph/Alignment_on_IE_Models/rate_0.2 \
    --input_files /data1/qyj/Alignment_on_IE_tasks/unified_data/train_mixture/mix_vDPO.jsonl \
    --output_file results/llama-base-7b/full/rate_0.2/T_1.0/mix_vDPO.jsonl \
    --batch_size 4 \
    --use_vllm \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
   --temperature 1.0 \
   --do_sample

CUDA_VISIBLE_DEVICES=3 python eval/predict.py \
    --model_name_or_path /data2/ph/Alignment_on_IE_Models/rate_0.2 \
    --input_files /data1/qyj/Alignment_on_IE_tasks/unified_data/train_mixture/mix_vDPO.jsonl \
    --output_file results/llama-base-7b/full/rate_0.2/T_1.0_new/mix_vDPO.jsonl \
    --batch_size 4 \
    --use_vllm \
    --use_chat_format \
    --chat_formatting_function eval.templates.create_prompt_with_tulu_chat_format \
   --temperature 1.0 \
   --do_sample