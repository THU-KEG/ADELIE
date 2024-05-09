import os
import json
import random
from pathlib import Path
import copy
import argparse

OUTPUT_BASE=[
    ('Please give the answer in the tuple form "[Answer]: ({subject}; {relation}; {object})\n".','({head}; {type}; {tail})\n',1),
    ('Please tell me what the subject is, what the object is, and what is the relationship between them? ','subject is "{head}", object is "{tail}", the relation is "{type}". \n',1),
    ('Please give the answer in the tuple form "[Answer]: (subject: {subject}; relation: {type}; object: {object})\n".','(subject: {head}; relation: {type}; object: {tail})\n ',1),
    ('Please give the answer in the tuple form "[Answer]: (head: {subject}; relation: {type}; tail: {object})\n".','(head: {head}; relation: {type}; tail: {tail})\n ',1),
    ('Please tell me what the head is, what the tail is, and what is the relationship between them? ','the head entity is "{head}", the tail entity is "{tail}", and the relation between them is "{type}".\n',1)
]
#(prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base 
# {entity1}, {entity2}, {head},{type},{tail}
OUTPUT_EXPLAN=[
    'In the provided text, two entities need relationship classification:"{entity1}" and "{entity2}".\nThe established relationship, based on the text and predefined relationships, is "{type}". So "{head}" is the subject and "{tail}" is the object.\nTo sum up, ',
    'Within the given text, two entities requiring relationship classification are "{entity1}" and "{entity2}". The determined relationship, derived from the text and predefined relationships, is denoted as "{type}". Consequently, "{head}" assumes the role of the subject, while "{tail}" serves as the object. In conclusion, ',
    'In the provided text, there are two entities in need of relationship classification: "{entity1}" and "{entity2}". The established relationship, derived from the text and predefined relationships, is identified as ["{type}"]. Thus, "{head}" takes on the role of the subject, with "{tail}" as the object. To summarize, ',
    'Within the presented text, two entities demand relationship classification: "{entity1}" and "{entity2}". The determined relationship, based on the text and predefined relationships, is labeled as ["{type}"]. Consequently, "{head}" assumes the subject position, while "{tail}" assumes the object position. In summary, ',
    'In the given text, two entities, "{entity1}" and "{entity2}", require relationship classification. The established relationship, as derived from the text and predefined relationships, is recognized as ["{type}"]. Accordingly, "{head}" is identified as the subject, and "{tail}" is identified as the object. In conclusion, '
]

def diverse_options(x,flag):
    if flag==0:
        return x.lower()
    if flag==1:
        return x.replace("-","_")
    if flag==2:
        return x.replace("-","_").lower()
    if flag==3:
        e1=x.split("-")[0]
        e2=x.split("-")[1].split("(")[0]
        if "(e1,e2)" in x:
            return e1+" and "+e2
        else:
            return e2+" and "+e1
    if flag==4:
        e1=x.split("-")[0]
        e2=x.split("-")[1].split("(")[0]
        if "(e1,e2)" in x:
            return e1+"_and_"+e2
        else:
            return e2+"_and_"+e1
    if flag==5:
        e1=x.split("-")[0].lower()
        e2=x.split("-")[1].split("(")[0].lower()
        if "(e1,e2)" in x:
            return "is_"+e1+"_and_"+e2+"_is"
        else:
            return "is_"+e2+"_and_"+e1+"_is"
    return x


def get_instruction(inst):
    instruction_list= random.sample(inst, 1)
    return instruction_list[0][0],instruction_list[0][1]

def mark_entity(tokens, h_pos, t_pos, markers=["<entity>", "</entity>"]):
    text = ""
    for i, token in enumerate(tokens):
        if i == h_pos[0]:
            text += "<entity>" + " "
        if i == t_pos[0]:
            text += "<entity>" + " "
        text += token + " "
        if i == h_pos[1] - 1:
            text += "</entity>" + " "
        if i == t_pos[1] - 1:
            text += "</entity>" + " "
    text = text.strip()
    return text

def swap(a,b):
    return b,a

def get_initdataset(data,config):
    init_dataset=[]
    for i,instance in enumerate(data):
        text = mark_entity(instance["token"], instance["h"]["pos"], instance["t"]["pos"])

        init_data={
            "input":text,
            "head":instance["h"]["name"],
            "tail":instance["t"]["name"],
            "explain_arg":[]
        }
        if instance["relation"] != "Other":
            if instance["h"]["pos"][0]<instance["t"]["pos"][0]:
                init_data["explain_arg"].append([instance["h"]["name"],instance["t"]["name"],instance["h"]["name"],instance["relation"],instance["t"]["name"]])
            else:
                init_data["explain_arg"].append([instance["t"]["name"],instance["h"]["name"],instance["h"]["name"],instance["relation"],instance["t"]["name"]])
        init_dataset.append(init_data)
    return init_dataset

#处理NA数据,注意这是第一次处理，在后面option dropout后仍然有可能为NA
def get_valid_datasets(example_dataset,config):
    sum_valid_data=0
    valid_data=[]
    NA_data=[]
    for vert in example_dataset:
        if vert["explain_arg"]==[]:
            NA_data.append(vert)
        else:
            valid_data.append(vert)
    sum_valid_data=len(valid_data)
    num_NA_data=int((sum_valid_data/(1.0-config["EXAM_NA_RATE"]))*config["EXAM_NA_RATE"])
    
    print(sum_valid_data,len(NA_data),num_NA_data)
    if num_NA_data<len(NA_data):
        NA_data=random.sample(NA_data,num_NA_data)
    valid_data=valid_data+NA_data
    random.shuffle(valid_data)
    
    print("sample NA:",len(NA_data))
    print("sum:",len(valid_data))

    return valid_data

def get_response(ExFlag,base_tem,vert,new_options,na,OPT_Flag):
    explain_tem=random.sample(OUTPUT_EXPLAN, 1)[0]
    response="[Explanation]: "
    response_base="[Answer]: "
    ref=""
    new_args=[]
    for args in vert["explain_arg"]:
        type=diverse_options(args[3],OPT_Flag)
        if type in new_options:
            new_args.append(copy.deepcopy(args))
            new_args[-1][3]=type
    if len(new_args)==0:
        response+=na
        response_base+="NA"
    else:
        for args in new_args:
            response+=explain_tem.format(entity1=args[0],entity2=args[1],head=args[2],type=args[3],tail=args[4])
            response_base+=base_tem[1].format(head=args[2],type=args[3],tail=args[4])
            ref+=OUTPUT_BASE[0][1].format(head=args[2],type=args[3],tail=args[4])
    response+=response_base

    if ExFlag:
        return ref,response
    else:
        return ref,response_base

def construct_response(input_folder,output_folder,inst_file,split,config):
    if "test" in split:
        config["CLASS_DROPOUT_RATE"]=0
        config["ALL_DESC"]=0
        config["BIG_TYPE"]=0
        #?
        config["DESC_RATE"]=0
        config["EXPLAIN_RATE"]=0
        # config["UNCOMPELETE_OPTION"]=False


    input_path=os.path.join(input_folder,split+".txt")
    data = []
    with open(input_path) as f:
        for line in f.readlines():
            instance = json.loads(line.strip())
            data.append(instance)
    
    rel2id = json.load(open(os.path.join(input_folder,"rel2id.json")))
    options = [rel for rel in list(rel2id.keys())]
    assert len(set(options)) == len(rel2id)
    if "Other" in options:
        options.remove("Other")
    if "Others" in options:
        options.remove("Others")

    #instruction
    with open(inst_file, "r", encoding='utf-8') as reader:
        inst=json.load(reader)
        reader.close()
    inst=inst["RC"]

    #获得原始数据
    init_dataset=get_initdataset(data,config)
    example_dataset=[]
    if "test" in split:
        input_path=os.path.join(input_folder,"train.txt")
        train_data = []
        with open(input_path) as f:
            for line in f.readlines():
                instance = json.loads(line.strip())
                train_data.append(instance)
            f.close()
        example_dataset=get_initdataset(train_data,config)
    else:
        example_dataset=copy.deepcopy(init_dataset)
    example_dataset=get_valid_datasets(example_dataset,config)

    #处理init-data
    na_data=0
    out_file = open(os.path.join(output_folder,split+".jsonl"), "w")
    for i,vert in enumerate(init_dataset):
         # instruction & options
        instruction,na=get_instruction(inst)
        REP_Flag=(int)(random.random()<0.7)###################
        if REP_Flag:
            if "<entity1>" in instruction:
                instruction=instruction.replace("<entity1>",'"'+vert["head"]+'"')
            if "<entity2>" in instruction:
                instruction=instruction.replace("<entity2>",'"'+vert["tail"]+'"') 
            if "<head>" in instruction:
                instruction=instruction.replace("<head>",'"'+vert["head"]+'"')
            if "<tail>" in instruction:
                instruction=instruction.replace("<tail>",'"'+vert["tail"]+'"') 
        new_options=[]
        for op in options:
            flag=(int)(random.random()>config["CLASS_DROPOUT_RATE"])
            if flag==1:
                new_options.append(op)
        random.shuffle(new_options)

        # deverse option
        OPT_Flag=-1
        if config["UNCOMPELETE_OPTION"]==True:
            # OPT_Flag=random.randint(0, 10)
            OPT_Flag=3
        dnew_options=[diverse_options(op,OPT_Flag) for op in new_options]

        if "<options>" in instruction:
            instruction=instruction.replace("<options>","["+", ".join(dnew_options)+"]",1)
        else:
            instruction+="\nOptions: ["+", ".join(dnew_options)+"]\n"

        ############################ issue ###########################
        # instruction='Please classify relationships between the two entities (marked with <entity> and </entity>).\n If the two entities have no relationships, please answer NA.\n The set of relationships is as follows:[[Effect_and_Cause, Destination_and_Entity, Container_and_Content, Product_and_Producer, Message_and_Topic, Agency_and_Instrument, Instrument_and_Agency, Producer_and_Product, Cause_and_Effect, Whole_and_Component, Topic_and_Message, Entity_and_Destination, Collection_and_Member, Member_and_Collection, Content_and_Container, Origin_and_Entity, Component_and_Whole, Entity_and_Origin]]. Please give the answer in the tuple form \"[Answer]: ({subject}; {relation}; {object})\n\".'

        #definition
        unified_instance = {
            "id":i,
            "instruction":instruction,
            "query":[],
            "examples":[],
            "input":vert["input"],
            "reference":"",
            "output":"",
        }

        ExFlag=(int)(random.random()<config["EXPLAIN_RATE"])
        explain_tem=random.sample(OUTPUT_EXPLAN, 1)[0]
        if "test" in split: 
            base_tem=OUTPUT_BASE[0]
        else: 
            base_tem=random.sample(OUTPUT_BASE,1)[0]
        
        #query
        unified_instance["query"].append(ExFlag)
        unified_instance["query"].append(base_tem[0])

        #ref & output
        unified_instance["reference"],unified_instance["output"]=get_response(ExFlag,base_tem,vert,dnew_options,na,OPT_Flag)

        #examples
        HistoryData=random.sample(example_dataset,config["NUM_FEWSHOT_Limit"])
        for hd in HistoryData:
            if hd ==vert:
                continue
            _,hdout=get_response(ExFlag,base_tem,hd,dnew_options,na,OPT_Flag)
            unified_instance["examples"].append([hd["input"],hdout])
        

        out_file.write(json.dumps(unified_instance) + "\n")
        if unified_instance["reference"]=="":
            na_data+=1
        # out_file.write(json.dumps(unified_instance) + "\n")
    print("na_num:",na_data)
    print("valid_num",len(data)-na_data)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="conll-2003")
    # I/O
    parser.add_argument("--input_dir", type=str, default="../../../data/Relation Extraction/semeval")
    parser.add_argument("--output_dir", type=str, default="../../../unified_data/semeval")
    parser.add_argument("--instruction_file", type=str, default="../instruction.json")

    # parameters
    parser.add_argument("--sample_rate", type=float, default=0.5)
    parser.add_argument("--each_sample_num", type=int, default=5)
    parser.add_argument("--limit_sample", type=int, default=15)

    parser.add_argument("--desc_rate", type=float, default=0.3)
    parser.add_argument("--limit_desc", type=int, default=8)
    parser.add_argument("--isall", type=float, default=0.9)

    parser.add_argument("--json_rate", type=float, default=0.1)

    parser.add_argument("--big_type_rate", type=float, default=0.2)

    parser.add_argument("--class_dropout_rate", type=float, default=0.1)
    parser.add_argument("--diverse_options", type=bool, default=True)
    parser.add_argument("--explain_rate", type=float, default=0.5)

    parser.add_argument("--num_fewshot_limit", type=int, default=8)
    parser.add_argument("--WORD_Limit", type=int, default=1200)
    parser.add_argument("--fewshot_na_rate", type=float, default=0.2)

    args = parser.parse_args()

    input_folder=Path(args.input_dir)
    output_folder = Path(args.output_dir)
    inst_file=args.instruction_file
    # args
    config={
        #sample
        "SAMPLE_RATE":args.sample_rate,
        "EACH_SAMPLE_NUM":args.each_sample_num,
        "LIMIT_SAMPLE":args.limit_sample,
        #desc
        "DESC_RATE":args.desc_rate,
        "LIMIT_DESC":args.limit_desc,
        "ISALL":args.isall, #for sample & desc
        #output_json
        "JSON_RATE":args.json_rate,
        #b-s type
        "BIG_TYPE":args.big_type_rate,
        #args
        "CLASS_DROPOUT_RATE":args.class_dropout_rate,
        "UNCOMPELETE_OPTION":args.diverse_options,
        #explain相关
        "EXPLAIN_RATE":args.explain_rate,
        #few-shot相关
        "NUM_FEWSHOT_Limit":args.num_fewshot_limit,
        "WORD_Limit":args.WORD_Limit,
        "EXAM_NA_RATE":args.fewshot_na_rate
    }

    output_folder.mkdir(exist_ok=True, parents=True)
    # construct_response(input_folder, output_folder, "train",config)
    construct_response(input_folder, output_folder,inst_file, "test",config)
    # 