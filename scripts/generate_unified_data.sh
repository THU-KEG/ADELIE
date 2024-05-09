# #================ Training Set ===================
# #================ NER ============

python tasks/conll-2003/load_data_fs.py \
    --input_dir ../data/Named_Entity_Recognition/CoNLL2003/processed \
    --output_dir ../unified_data/conll-2003 \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \


python tasks/ace2005-ner/load_data_fs.py \
    --input_dir  ../data/Named_Entity_Recognition/ace2005-en/processed \
    --output_dir ../unified_data/ace2005-ner \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



python tasks/ontonote5/load_data_fs.py \
    --input_dir  ../data/Named_Entity_Recognition/ontonote5\
    --output_dir ../unified_data/ontonote5 \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



# #=============== RC ===============

python tasks/fewrel/load_data_fs.py \
    --input_dir  ../data/Relation_Extraction/fewrel \
    --output_dir ../unified_data/fewrel \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



python tasks/tacred/load_data_fs.py \
    --input_dir  ../data/Relation_Extraction/tacred \
    --output_dir ../unified_data/tacred \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



# #=============== ED ===============

python tasks/ace2005-ed/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/ace2005-en \
    --output_dir ../unified_data/ace2005-ed \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



python tasks/maven-ed/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/maven \
    --output_dir ../unified_data/maven-ed \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



# #=============== EAE ===============

python tasks/ace2005-eae/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/ace2005-en \
    --output_dir ../unified_data/ace2005-eae \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    




python tasks/rams/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/RAMS_1.0c/data \
    --output_dir ../unified_data/RAMS-eae \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    


python tasks/maven-arg/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/MAVEN-Arg \
    --output_dir ../unified_data/maven-eae \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    


# #=============== ERE ================

python tasks/maven-ere/load_data_fs.py \
    --input_dir  ../data/Event_Relation_Extraction/MAVEN-ERE \
    --output_dir ../unified_data/MAVEN-ERE \
    --instruction_file tasks/instructions.json \
    --infFormat_rate 0.8 \
    --json_rate 0.05 \
    --explain_rate 0.1 \
    



#================ Test Set ===================
#================ NER ============

python tasks/fewnerd/load_data_fs.py \
    --input_dir  ../data/Named_Entity_Recognition/FewNERD/supervised \
    --output_dir ../unified_data/few-nerd-supervised \
    --instruction_file tasks/instructions.json \
    --sample_rate 0.0 \
    --desc_rate 0.0\
    --num_fewshot_limit 4 \


#=============== RC ===============

python tasks/semeval/load_data_fs.py \
    --input_dir  ../data/Relation_Extraction/semeval \
    --output_dir ../unified_data/semeval \
    --instruction_file tasks/instructions.json \
    --sample_rate 0.0 \
    --desc_rate 0.0\
    --num_fewshot_limit 4 \


#=============== ED ===============

python tasks/richere-ed/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/RichERE \
    --output_dir ../unified_data/RichERE-ed \
    --instruction_file tasks/instructions.json \
    --sample_rate 0.0 \
    --desc_rate 0.0\
    --num_fewshot_limit 4 \

#=============== EAE ===============

python tasks/richere-eae/load_data_fs.py \
    --input_dir  ../data/Event_Extraction/RichERE \
    --output_dir ../unified_data/RichERE-eae \
    --instruction_file tasks/instructions.json \
    --sample_rate 0.0 \
    --desc_rate 0.0\
    --num_fewshot_limit 4 \



#=============== ERE ================

python tasks/matres/load_data_fs.py \
    --input_dir  ../data/Event_Relation_Extraction/MATRES \
    --output_dir ../unified_data/MATRES \
    --instruction_file tasks/instructions.json \
    --sample_rate 0.0 \
    --desc_rate 0.0\
    --num_fewshot_limit 4 \

