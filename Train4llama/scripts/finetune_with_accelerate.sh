export CUDA_VISIBLE_DEVICES=4,5,6,7

MODEL_SIZE=7B
NUM_GPUS=4
BATCH_SIZE_PER_GPU=2
TOTAL_BATCH_SIZE=128
GRADIENT_ACC_STEPS=$(($TOTAL_BATCH_SIZE/$NUM_GPUS/$BATCH_SIZE_PER_GPU))
echo "Training llama model ${MODEL_SIZE} using $NUM_GPUS GPUs, $BATCH_SIZE_PER_GPU batch size per GPU, $GRADIENT_ACC_STEPS gradient accumulation steps"

accelerate launch \
    --mixed_precision bf16 \
    --num_machines 1 \
    --num_processes $NUM_GPUS \
    --use_deepspeed \
    --deepspeed_config_file ds_configs/stage2.conf \
    open_instruct/finetune.py \
    --model_name_or_path /data2/MODELS/llama-2-7b \
    --use_flash_attn \
    --tokenizer_name /data2/MODELS/llama-2-7b \
    --use_slow_tokenizer \
    --train_file /data1/qyj/Alignment_on_IE_tasks/unified_data/train_mixture/tuluv2_unified_TuluFormat.jsonl \
    --max_seq_length 2048 \
    --preprocessing_num_workers 16 \
    --per_device_train_batch_size $BATCH_SIZE_PER_GPU \
    --gradient_accumulation_steps $GRADIENT_ACC_STEPS \
    --learning_rate 2e-5 \
    --lr_scheduler_type cosine \
    --warmup_ratio 0.03 \
    --weight_decay 0. \
    --num_train_epochs 2 \
    --output_dir output/llama-base-7b/full/only_tulu_corpus/ \
    --with_tracking \
    --report_to wandb \
    --logging_steps 10 \
    --max_train_steps 6248