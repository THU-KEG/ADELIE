## Runing

### 数据准备

sh generate_unified_data.sh

sh generate_mixtural_train_data.sh

### 训练

详情看 Train4Llama 中的 README_ours.md

### 评估数据生成

sh generate_test_set.sh

## Details

数据集处理参数（diverse的方式）：

```json
config={
    #sample：在NER/ED/EAE任务中，对于每个选项的举例：比如：'Person'：such as 'Bob', 'Amy'...
    "SAMPLE_RATE":0.5, #在生成的数据中，总共有SAMPLE_RATE比例的数据，instruction里面含有sample
    "EACH_SAMPLE_NUM":5, #一个option含有EACH_SAMPLE_NUM个samples
    "LIMIT_SAMPLE":8, #由于context length的限制，至多有LIMIT_SAMPLE个option有samples

    #output_json：输出格式为json
    "JSON_RATE":0.1,

    #desc：对于tacred/fewrel..数据集
    "DESC_RATE":0.3, #在生成的数据中，总共有DESC_RATE比例的数据，instruction里面含有option的description
    "LIMIT_DESC":8,
    "ISALL":0.67,#在所有数据中，(SAMPLE_RATE+DESC_RATE)*ISALL比例的数据，它们的每个option都有samples/description

    #b-s type：对于ace等数据集含有大分类和小分类，进行大分类的概率
    "BIG_TYPE":0.2,

    #args
    "CLASS_DROPOUT_RATE":0.1,
    "UNCOMPELETE_OPTION":True, #对于option本身的diverse

    #explain相关
    "EXPLAIN_RATE":0.5,

    #few-shot相关
    "NUM_FEWSHOT_Limit":8,
    "WORD_Limit":1200,
    "EXAM_NA_RATE":0.0
}
```

generate_unified_data.sh 之后生成的数据格式
（load_data_fs后生成的数据格式）

```json
{
    "id": int, 
    "instruction": "", 
    "query": [bool, ""],  # [0]:是否有explanation，[1]:指定何种格式回答
    "examples": [
        ["",""], #[input, output]，其中input为text，output为按照指定格式回答的输出
        ...
    ]
    "input": "", #query_text 
    "reference": "", #标准格式下的答案，进行后续evaluate使用
    "output": "" #指定格式下的答案
}
```

generate_mixtural_train_data.sh 之后生成的数据格式

```json
[
    {
        "instruction": "", 
        "input": "", 
        "system": "", #ondemand ie 
        "history":[]
    }
]
```