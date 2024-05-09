# you need 8 GPUs for full finetuning
export CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7

NUM_GPUS=8
BATCH_SIZE_PER_GPU=1
TOTAL_BATCH_SIZE=32
GRADIENT_ACC_STEPS=$(($TOTAL_BATCH_SIZE/$NUM_GPUS/$BATCH_SIZE_PER_GPU))
echo "Training model using $NUM_GPUS GPUs, $BATCH_SIZE_PER_GPU batch size per GPU, $GRADIENT_ACC_STEPS gradient accumulation steps"

# accelerate launch \
#     --mixed_precision bf16 \
#     --num_machines 1 \
#     --num_processes $NUM_GPUS \
#     --use_deepspeed \
#     --deepspeed_config_file ds_configs/stage2.conf \
#     --main_process_port=8888 \
#     open_instruct/dpo_tune.py \
#     --model_name_or_path output/llama-base-7b/full/v20 \
#     --use_flash_attn \
#     --gradient_checkpointing \
#     --tokenizer_name output/llama-base-7b/full/v20 \
#     --use_slow_tokenizer \
#     --dataset_name HuggingFaceH4/ultrafeedback_binarized \
#     --max_seq_length 2048 \
#     --preprocessing_num_workers 16 \
#     --per_device_train_batch_size $BATCH_SIZE_PER_GPU \
#     --gradient_accumulation_steps $GRADIENT_ACC_STEPS \
#     --learning_rate 5e-7 \
#     --lr_scheduler_type linear \
#     --warmup_ratio 0.1 \
#     --weight_decay 0. \
#     --num_train_epochs 3 \
#     --output_dir output/llama-base-7b/full/v20_dpo_ultrafeedback \
#     --with_tracking \
#     --report_to tensorboard \
#     --logging_steps 1

accelerate launch \
    --mixed_precision bf16 \
    --num_machines 1 \
    --num_processes $NUM_GPUS \
    --use_deepspeed \
    --deepspeed_config_file ds_configs/stage2.conf \
    --main_process_port=8888 \
    open_instruct/dpo_tune.py \
    --model_name_or_path /data2/ph/Alignment_on_IE_Models/rate_0.2_plus_2 \
    --use_flash_attn \
    --gradient_checkpointing \
    --tokenizer_name /data2/ph/Alignment_on_IE_Models/rate_0.2_plus_2 \
    --use_slow_tokenizer \
    --dataset_name HuggingFaceH4/ultrafeedback_binarized \
    --max_seq_length 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size $BATCH_SIZE_PER_GPU \
    --gradient_accumulation_steps $GRADIENT_ACC_STEPS \
    --learning_rate 5e-7 \
    --lr_scheduler_type linear \
    --warmup_ratio 0.1 \
    --weight_decay 0. \
    --num_train_epochs 3 \
    --output_dir output/llama-base-7b/full/rate_0.2_plus_2.dpo_ultrafeedback \
    --with_tracking \
    --report_to tensorboard \
    --logging_steps 1

    # --train_file /data1/qyj/Alignment_on_IE_tasks/unified_data/train_mixture/mix_vDPO_bleu_4train_mix_._plus_0.7_4f_0.1_5k.json \