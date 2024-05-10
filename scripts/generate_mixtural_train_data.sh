
#过滤训练数据中的NA，比例为 valid:na=0.8:0.2
python utils/filter_train_NA_data.py


#生成 tuluv2 数据
python utils/reformat_tuluv2.py

#生成 ondemandie 数据
python tasks/ondemandie/load_data_fs.py


#生成 IEInstruct 数据, output_path: /ADELIE/unified_data/train_mixture
python utils/mixture_task_fs_tuluformat.py \
    --unified_data_dir ../unified_data \
    --hold_in_datasets conll-2003 ace2005-ner ontonote5 fewrel tacred ace2005-ed maven-ed ace2005-eae RAMS-eae MAVEN-ERE maven-eae ee other_ner other_rc re openie4\
    --ondemandIE_dir ../unified_data/ondemandIE \
    --ondemand_cot_rate 0.2 \
    --general_training_file ../unified_data/tuluv2/train.jsonl \
    --Limit_total_data 400000 \
    --General_rate 0.8 \
    --Limit_dataset 5000 \
    --version "IEInstruct" \
    --general_filter 0 \
    --reserve_all_gptdata 0

