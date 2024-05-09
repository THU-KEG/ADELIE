JSON_BASE = "Please give the answer in json format."

OPTIONS = {
    "temporal_event_relation": "before, overlap, contains, simultaneous, begins-on, ends-on",
    "causal_relation": "cause, precondition",
    "coreference_relation": "coreference",
    "subevent_relation": "subevent",
}

R_Inst = {
    "temporal_event_relation": "ERE-Temporal",
    "causal_relation": "ERE-Causal",
    "subevent_relation": "ERE-Subevent",
    "coreference_relation": "ERE-Coref",
}

BTYPES = [
    "temporal_event_relation",
    "causal_relation",
    "subevent_relation",
    "coreference_relation",
]

REL = {
    "before": ["@ is earlier than $. ", "temporal_event_relation"],  # A..B
    "overlap": [
        "the time range of @ overlaps with the time range of $. ",  # A..B
        "temporal_event_relation",
    ],
    "contains": [
        "the time range of @ contains the time range of $. ",
        "temporal_event_relation",
    ],
    "simultaneous": [
        "the time range of @ is the same as the time range of $. ",
        "temporal_event_relation",
    ],
    "begins-on": ["@ begins at the time of $. ", "temporal_event_relation"],
    "ends-on": ["@ terminates at the time of $. ", "temporal_event_relation"],
    "cause": ["@ causes $. ", "causal_relation"],
    "precondition": [
        "@ is a necessary condition of $. But @ itself, without other conditions, might not cause $. ",
        "causal_relation",
    ],
    "subevent": [
        "$ is a component part of @ and is spatiotemporally contained by @. ",
        "subevent_relation",
    ],
    "coreference": ["@ and $ refer to the same event. ", "coreference_relation"],
}

rel2id = {
    "before": "A(Event/Timex) is earlier than B(Event/Timex).",
    "overlap": "the time range of A(Event/Timex) overlaps with the time range of B(Event/Timex).",
    "contains": "the time range of A(Event/Timex) contains the time range of B(Event/Timex).",
    "simultaneous": "the time range of A(Event/Timex) is the same as the time range of B(Event/Timex).",
    "begins-on": "A(Event/Timex) begins at the time of B(Event/Timex).",
    "ends-on": "A(Event/Timex) terminates at the time of B(Event/Timex).",
    "cause": "A(Event) causes B(Event).",
    "precondition": "A(Event) is a necessary condition of B(Event). But A itself, without other conditions, might not cause B.",
    "subevent": "B(Event) is a component part of A(Event) and is spatiotemporally contained by A.",
    "coreference": "A(Event) and B(Event) refer to the same event.",
}

OUTPUT_BASE = [
    (
        'Please give the answer in the tuple form "[Answer]: ({first event}; {relation}; {second event});".',
        "({head}; {type}; {tail}); ",
    ),
    (
        "Please tell me what is the relationship between the two events? ",
        'first event is "{head}", second event is "{tail}", the relation is "{type}". ',
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (first event: {head}; relation: {type}; second event: {tail}); ".',
        "(first event: {head}; relation: {type}; second event: {tail}); ",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (head: {head}; relation: {type}; tail: {tail}); ".',
        "(head: {head}; relation: {type}; tail: {tail}); ",
    ),
    (
        "Please give the answer in natural language.",
        'the head event is "{head}", the tail event is "{tail}", and the relation between them is "{type}".',
    ),
    (
        'Identify the relationship between the following events and present your findings in the format "[Answer]: {head} is related to {tail} by {type}."',
        '"{head}" is related to "{tail}" by "{type}".',
    ),
    (
        'How do these events connect? Please format your response as "[Answer]: The connection between {head} and {tail} is described as {type}."',
        'The connection between "{head}" and "{tail}" is described as "{type}".',
    ),
    (
        'Can you determine the link between these occurrences? Respond in the structure "[Answer]: Linking {head} to {tail} through {type}."',
        'Linking "{head}" to "{tail}" through "{type}".',
    ),
    (
        'What\'s the relation between the given events? Use the format "[Answer]: Between {head} and {tail}, the relation is {type}." for your answer.',
        'Between "{head}" and "{tail}", the relation is "{type}".',
    ),
    (
        'What is the connection between these two events? Please format your response as "[Answer]: The bond between {head} and {tail} is {type}."',
        'The bond between "{head}" and "{tail}" is "{type}".',
    ),
    (
        'How do these events relate to each other? Frame your answer like this: "[Answer]: {head} and {tail} are intertwined by {type}."',
        '"{head}" and "{tail}" are intertwined by "{type}".',
    ),
    (
        'Explain the relationship between the given events in the format "[Answer]: A {type} relationship exists between {head} and {tail}."',
        'A "{type}" relationship exists between "{head}" and "{tail}".',
    ),
    (
        "Identify the relationship between the following events.",
        'Between the events, "{head}" acts as the initiator and "{tail}" as the receiver, establishing a "{type}" relationship.',
    ),
    (
        "What binds these two events together? Elaborate in your response.",
        'The bond that unites "{head}" with "{tail}" is fundamentally a "{type}" connection.',
    ),
    (
        "Can you determine the type of interaction between these events?",
        'The interaction type between "{head}" and "{tail}" is classified as "{type}".',
    ),
]
OUTPUT_EXPLAN = [
    'The two events are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'Two events, "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"), are recognized. ',
    'The identified events are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'In the context of event relation extraction, the two events are identified as "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'The events "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}") have been distinguished. ',
    'Upon analysis, it\'s found that the events "{e1}" (categorized under "{t1}") and "{e2}" (categorized under "{t2}") are interconnected. ',
    'The connection is between "{e1}", which is an instance of "{t1}", and "{e2}", which falls under the category of "{t2}". ',
    'The linkage is discerned between the occurrences "{e1}" (identified as "{t1}") and "{e2}" (identified as "{t2}"). ',
    'The relationship involves "{e1}", a "{t1}" event, and "{e2}", a "{t2}" event. ',
    'The investigation reveals a connection between the events "{e1}" (identified as "{t1}") and "{e2}" (identified as "{t2}"). ',
    'The analysis indicates that the events "{e1}" (belonging to the category "{t1}") and "{e2}" (belonging to the category "{t2}") have a relationship. ',
    'After thorough examination, it is evident that there is a relationship between "{e1}", which is a type of "{t1}", and "{e2}", which is a type of "{t2}". ',
    'An analysis indicates a relationship where "{e1}" (categorized under "{t1}") initiates an action affecting "{e2}" (categorized under "{t2}"). ',
    'Upon examination, the bond linking "{e1}" (termed as "{t1}") with "{e2}" (termed as "{t2}") is uncovered. ',
    'The interaction between the events "{e1}" (designated as "{t1}") and "{e2}" (designated as "{t2}") is scrutinized. ',
]
OUTPUT_EXPLAN_T = [
    'The two specific time points are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'Two specific time points, "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"), are recognized. ',
    'The identified specific time points are "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'In the context of time point relation extraction, the two specific time points are identified as "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}"). ',
    'The specific time points "{e1}" (classified as "{t1}") and "{e2}" (classified as "{t2}") have been distinguished. '
    'Upon analysis, it\'s found that the specific time points "{e1}" (categorized under "{t1}") and "{e2}" (categorized under "{t2}") are interconnected. ',
    'The connection is between "{e1}", which is an instance of "{t1}", and "{e2}", which falls under the category of "{t2}". ',
    'The linkage is discerned between the occurrences "{e1}" (identified as "{t1}") and "{e2}" (identified as "{t2}"). ',
    'The relationship involves "{e1}", a "{t1}" event, and "{e2}", a "{t2}" event. ',
    'The investigation reveals a connection between the specific time points "{e1}" (identified as "{t1}") and "{e2}" (identified as "{t2}"). ',
    'The analysis indicates that the specific time points "{e1}" (belonging to the category "{t1}") and "{e2}" (belonging to the category "{t2}") have a relationship. ',
    'After thorough examination, it is evident that there is a relationship between "{e1}", which is a type of "{t1}", and "{e2}", which is a type of "{t2}". ',
    'An analysis indicates a relationship where "{e1}" (categorized under "{t1}") initiates an action affecting "{e2}" (categorized under "{t2}"). ',
    'Upon examination, the bond linking "{e1}" (termed as "{t1}") with "{e2}" (termed as "{t2}") is uncovered. ',
    'The interaction between the specific time points "{e1}" (designated as "{t1}") and "{e2}" (designated as "{t2}") is scrutinized. ',
]

RANDOM_SYMBOLS = [
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "LABEL_1",
    "LABEL_2",
    "LABEL_3",
    "LABEL_4",
    "LABEL_5",
    "LABEL_6",
]
