PROMPT = """
You need to follow the template list to come up with a set of diverse templates. 
The task indicated by this template is the “Open Information Extraction” task.

We need to write the instruction, input format and corresponding output format template for it.
Instruction is an introduction to OpenIE tasks.
The instruction template content should include the following strings to facilitate subsequent replacement of the content: {text}.
The output contains two parts, one is "explanation" and the other is "answer".
The explanation template content should include the following strings to facilitate subsequent replacement of the content: {subject}, {predicate
}, {object}, {time}, {location}.
The answer template content should include the following strings to facilitate subsequent replacement of the content: {subject}, {predicate
}, {object}, {time}, {location}.

Here are the requirements:
1. Try not to repeat the verb for each template to maximize diversity.
2. The language used for the template also should be diverse. For example, use interrogative sentences, imperative sentences, etc.
3. Input and output templates ([Answer]: ..) should also be as diverse as possible.
4. Do not repeat the format of the answer template, nor repeat the examples given.
5. Input and output must correspond to each other.
6. The templates should be in English.

"""

Template = {
    "Instruction": "",
    "Fail output": "",
    "Input": "",
    "Output": "",
    "Explanation": "",
}


INST = {
    "OPENIE": [
        [
            'Open information extraction requires the extraction of all relations in the sentence, i.e., predicates, the subjects and objects corresponding to these relations, and the possible time and place thesis elements. Please extract all the relational tuples in the following sentence: <text>. If there are no relations in the text, please answer "NA".',
            "NA",
        ],
        [
            'Open Information Extraction (OpenIE) aims to extract n-ary knowledge tuples {(a1, p, a2, ..., an)} consisting of n arguments and one predicate from the natural text in a domain-independent manner. Please extract all the relational tuples in the following sentence, i.e., predicates, the subjects and objects corresponding to these relations, and the possible time and place thesis elements. Text: <text>. There may be no tuples in the text, if not, output "No tuples".',
            "No tuples.",
        ],
        [
            'To perform open information extraction effectively, one must identify and extract all relations within the sentence. This includes recognizing predicates, determining subjects and objects linked to these relations, and identifying potential temporal and spatial elements. Can you help me extract possible relation tuples from the Text: <text> ? If there is no answer, answer "There are no possible relational tuples.".',
            "There are no possible relational tuples.",
        ],
        [
            'Could you perform Open Information Extraction on the provided text? Your task is to extract all the relational tuples from the text, including predicates, subjects, objects, and any associated time and location elements. Text: <text>. If there are no tuples present in the text, please output "No tuples".',
            "No tuples.",
        ],
        [
            "In the realm of Open Information Extraction, the objective is to uncover relational tuples from natural language text, encapsulating subjects, predicates, objects, as well as potential temporal and spatial attributes. Could you delve into the provided text and extract any relational tuples? If no tuples exist, kindly respond with 'No tuples found.'",
            "No tuples found.",
        ],
        [
            "Engage in the process of Open Information Extraction by identifying and extracting relational tuples from the specified text. These tuples should include subjects, predicates, objects, and, if applicable, any time or location information. If the text does not contain any relational tuples, please indicate by stating 'No tuples found.'",
            "No tuples found.",
        ],
        [
            "Your mission is to dissect the given text and extract any relational tuples it may contain, focusing on the subjects, predicates, objects, and noting any temporal or spatial details present. If the text lacks relational tuples, simply report back with 'No relational tuples identified.'",
            "No relational tuples identified.",
        ],
        [
            "Dive into the provided text and unearth any relational tuples, paying close attention to subjects, predicates, objects, and any elements of time or location. Should the text be devoid of such tuples, kindly report 'No tuples to report.'",
            "No tuples to report.",
        ],
        [
            "In the task of Open Information Extraction, your goal is to dissect the given text to unearth the underlying relationships. This involves pinpointing the subjects, predicates, and objects, as well as noting any relevant temporal or spatial details. Should the text lack relational tuples, kindly respond with 'No relationships identified.'",
            "No relationships identified.",
        ],
        [
            "Dive into the Open Information Extraction task by extracting relational tuples from the provided text, which include subjects, predicates, objects, and possibly, time and location details. If no relational tuples are present, simply state 'Relationships not found.'",
            "Relationships not found.",
        ],
        [
            "Your task in Open Information Extraction is to analyze the text and extract the relational tuples it contains, focusing on subjects, predicates, objects, and any identifiable temporal or spatial information. If the text does not yield any relational tuples, please reply with 'Extracted tuples not available.'",
            "Extracted tuples not available.",
        ],
        [
            " In the task of Open Information Extraction, your objective is to sift through the provided text and distill the essential relational tuples it harbors. These tuples should encapsulate subjects, predicates, objects, and when discernible, elements of time and location. Should the text prove barren of such tuples, kindly respond with 'Tuples cannot be extracted.'",
            "Tuples cannot be extracted.",
        ],
        [
            "Your mission in Open Information Extraction is to delve into the provided text and unearth the relational tuples it conceals. These tuples are to include subjects, predicates, objects, and, where applicable, any temporal or spatial markers. In the event that the text is devoid of such tuples, please report back with 'Unable to extract tuples.'",
            "Unable to extract tuples.",
        ],
        [
            "The essence of Open Information Extraction involves parsing the given text to identify and extract relational tuples, which include subjects, predicates, objects, and potentially, temporal and spatial information. If no such tuples are present in the text, your response should be 'Extraction of tuples is not possible.'",
            "Extraction of tuples is not possible.",
        ],
        [
            "In the realm of Open Information Extraction, your task is to parse the provided text and identify any relational tuples it contains. These should include subjects, predicates, objects, and when present, any temporal or spatial information. Should the text not contain any identifiable tuples, your response should be 'Tuples not found.'",
            "Tuples not found.",
        ],
        [
            " Your objective in this Open Information Extraction task is to scrutinize the text and extract relational tuples, focusing on subjects, predicates, objects, and noting any relevant temporal or spatial contexts. If the text does not yield any tuples, your report should state 'No identifiable tuples.'",
            "No identifiable tuples.",
        ],
        [
            "Dive into the text provided and extract any relational tuples, paying close attention to subjects, predicates, objects, and any temporal or spatial details. If no tuples can be extracted, please respond with 'Extraction failed.'",
            "Extraction failed.",
        ],
    ]
}

OUTPUT_BASE = [
    (
        'Please give the answer in the tuple form "[Answer]: ({predicate}; {subject}; {object}; {time}; {location})\n".',
        "({predicate}; {subject}; {object}; {time}; {location})\n",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (predicate: {predicate}; subject: {subject}; object: {object}; time: {time}; location: {location})\n".',
        "(predicate: {predicate}; subject: {subject}; object: {object}; time: {time}; location: {location})\n",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: ({subject}; {relation}; {object}; {time}; {location})\n".',
        "({subject}; {predicate}; {object}; {time}; {location})\n",
    ),
    (
        "Please tell me what the subject is, what the object is, and what is the relationship between them? If there are possible elements of time or place, please let me know as well.",
        'subject is "{subject}", object is "{object}", the relation is "{predicate}", time is "{time}", location is "{location}".\n',
    ),
    (
        "Kindly provide the extracted information in the following format: '[Answer]: ({predicate}; {subject}; {object}; {time}; {location})\n'.",
        "Extracted tuple: ({predicate}; {subject}; {object}; {time}; {location})\n",
    ),
    (
        "Identify and describe the relationship between the subject and object in the text, including any relevant time or location details.",
        'The relationship involves "{subject}" and "{object}", with "{predicate}" acting as the link. Time: "{time}", Location: "{location}".\n',
    ),
    (
        "What connections can you draw from the text, especially concerning subjects, objects, and their interactions? Include time and place if mentioned.",
        'Connection: "{subject}" interacts with "{object}" through "{predicate}". Noted Time: "{time}", Noted Place: "{location}".\n',
    ),
    (
        "Extract the essence of the relationships depicted in the text, including the roles of subjects, objects, and the nature of their relationships, along with any time or location specifics.",
        'In essence, "{subject}" and "{object}" are bound by "{predicate}", occurring at "{time}" within "{location}".\n',
    ),
    (
        "Your response should be formatted as follows: '[Answer]: ({subject}; {predicate}; {object}; if applicable, {time}; if applicable, {location})\n'.",
        "Identified relationship: ({subject}; {predicate}; {object}; {time}; {location})\n",
    ),
    (
        "Format your findings as: '[Answer]: ({object}; {predicate}; {subject}; {location}; {time})\n'.",
        "Discovered tuple: ({object}; {predicate}; {subject}; {location}; {time})\n",
    ),
    (
        "Please present the extracted tuples in the format: '[Answer]: ({subject}; {predicate}; {object}; optionally, {time}; optionally, {location})\n'.",
        "Tuple extracted: ({subject}; {predicate}; {object}; {time}; {location})\n",
    ),
    (
        "What connections can you draw between the subject and object, including any pertinent temporal or spatial details?",
        'Between "{subject}" and "{object}", the connection "{predicate}" is established, occurring at "{time}" and within "{location}".\n',
    ),
    (
        "Can you elucidate the relationship between the subject and object, noting any significant time or place markers?",
        ' In this scenario, "{subject}" and "{object}" are linked through "{predicate}", with the event taking place at "{time}" and located at "{location}".\n',
    ),
    (
        "Please analyze the relationship between the subject and object, including any relevant time or location information.",
        'The dynamic between "{subject}" and "{object}" is characterized by "{predicate}", occurring during "{time}" and at "{location}".\n',
    ),
    (
        "Extract the core relationship from the text, highlighting the subject, predicate, and object, along with any pertinent time or location information.",
        'Core relationship extracted: "{subject}" is connected to "{object}" by "{predicate}". Occurred at "{time}" in "{location}".\n',
    ),
    (
        "Detail the relationship extracted from the text, including the subject, predicate, object, and any significant time or location details.",
        'Extracted relationship: Involving "{subject}" and "{object}", connected through "{predicate}". Noted time: "{time}", and location: "{location}".\n',
    ),
    (
        "Analyze and present the relationship depicted in the text, ensuring to include the subject, predicate, object, and any relevant time or location details.",
        'Depicted relationship: "{subject}" and "{object}" are bound by "{predicate}". Time noted: "{time}", Location: "{location}".\n',
    ),
    # 可省略的
    (
        "Please give the answer in the tuple form. In these tuples, we always put the predicate first, the second is the subject corresponding to the predicate, the third is the object corresponding to the predicate (if there is none, it is not labeled), and the last two are time and place in that order, which can be omitted if there is none.",
        "",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: ({predicate}; {subject}; {object}; {time}; {location})\n". If one or more of the last three elements does not exist, it can be omitted.',
        "",
    ),
]

OUTPUT_EXPLAN = [
    [
        "According to the given text, the subject is {subject}, the predicate is {predicate}, and their object is {object}.",
        "At the same time, the time attribute contained in this relation tuple is {time}, and the location attribute is {location}.",
    ],
    [
        "Upon analysis of the given text, we find that the subject corresponds to {subject}, the predicate is {predicate}, and the associated object is {object}.",
        "Additionally, there exist temporal attributes denoted by {time}, along with a spatial attribute represented by {location}.",
    ],
    [
        "Upon examination of the text, we identify {subject} as the subject, {predicate} as the predicate, and {object} as the corresponding object.",
        "Furthermore, we observe temporal indications denoted by {time}, as well as a spatial context provided by {location}.",
    ],
    [
        'The analysis reveals that "{subject}" and "{object}" are linked by the predicate "{predicate}".',
        'This relationship is contextualized by the time "{time}" and the location "{location}".',
    ],
    [
        'In the text, "{subject}" is connected to "{object}" via "{predicate}".',
        'This interaction is placed in time and space at "{time}" and "{location}" respectively.',
    ],
    [
        'The core of the text reveals a relationship where "{subject}" is bound to "{object}" by "{predicate}".',
        'This event is timestamped at "{time}" and located at "{location}".',
    ],
    [
        'Upon examination, it\'s observed that "{subject}" is linked to "{object}" through "{predicate}".',
        'The occurrence is marked by the temporal frame "{time}" and the spatial setting "{location}".',
    ],
    [
        'Analysis shows "{subject}" is connected with "{object}" through "{predicate}".',
        'The scenario unfolds at "{location}" during "{time}".',
    ],
    [
        'The text illustrates a connection between "{subject}" and "{object}" via "{predicate}".',
        'This connection is temporally situated at "{time}" and spatially at "{location}".',
    ],
    [
        'The narrative thread between "{subject}" and "{object}" is sewn by "{predicate}".',
        'The fabric of this narrative is further colored by the temporal marker "{time}" and the spatial coordinate "{location}".',
    ],
    [
        'Here, "{subject}" and "{object}" are intertwined by the action "{predicate}".',
        'The occurrence is anchored in time at "{time}" and in space at "{location}".',
    ],
    [
        'The relationship between "{subject}" and "{object}" is mediated by "{predicate}".',
        'This interaction is temporally situated at "{time}" and spatially at "{location}".',
    ],
    [
        'The core of the relationship is that "{subject}" is connected to "{object}" via "{predicate}".',
        'This event took place at "{time}" and in "{location}".',
    ],
    [
        'The relationship extracted shows "{subject}" and "{object}" are linked by "{predicate}".',
        'This was noted to occur at "{time}" and at "{location}".',
    ],
    [
        'It\'s depicted that "{subject}" and "{object}" are bound together by "{predicate}".',
        'The event is noted to have occurred at "{time}" and at "{location}".',
    ],
]
