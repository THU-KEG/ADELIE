# 生成 fewshot 和 zeroshot 测试数据
python utils/fewshot_testdatasets.py \
    --input_dir ../unified_data_longshot \
    --output_dir ../unified_data/test_format_32shot \
    --hold_out_datasets few-nerd-supervised semeval RichERE-ed RichERE-eae MATRES ROBUST \
    --num_shot 4
