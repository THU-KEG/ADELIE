
for p in {1..5}
do
    python utils/DPO/compute_metric_4OpenInstruct.py \
        --input_path ../unified_data/train_mixture/sample4dpo_results/ADELIE-SFT/T_1.0_$p/mix_vDPO
done

python utils/DPO/merge.py