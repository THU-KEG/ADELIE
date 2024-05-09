
python utils/DPO/generate_dpo_data_TuluFormat.py \
    --unified_data_dir ../unified_data \
    --hold_in_datasets conll-2003 ace2005-ner ontonote5 fewrel tacred ace2005-ed maven-ed ace2005-eae RAMS-eae maven-eae MAVEN-ERE openie4\
    --ondemandIE_dir ../unified_data/ondemandIE \
    --ondemand_cot_rate 0.3 \
    --Limit_total_data 90000 \
    --Limit_dataset 4000 \
    --version "DPO" \
    --reserve_all_gptdata 1 \
    --WORD_Limit 1200 \


