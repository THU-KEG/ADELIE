JSON_BASE = "Please give the answer in json format."

OUTPUT_BASE = [
    (
        'Please give the answer in the form "[Answer]: {content}: {role}; ".',
        "{word}: {type}; ",
    ),
    (
        'Please give the answer in the form "[Answer]: (content: {word}, role: {type}); ".',
        "(content: {word}, role: {type}); ",
    ),
    (
        "Please give the answer in natural language.",
        'the event role "{type}" is "{word}"; ',
    ),
    (
        "Please give the answer in natural language.",
        '"{word}" is the role of "{type}"; ',
    ),
    (
        'Please give the answer in the form "[Answer]: ({content}, {role}); ".',
        "({word}, {type}); ",
    ),
    (
        "What is the role of each word in the described event?",
        'Role of "{word}" is "{type}". ',
    ),
    (
        "Identify the roles and words associated with the event.",
        '"{word}" plays the role of "{type}". ',
    ),
    (
        "Can you extract the event arguments and their roles?",
        '"{word}" is identified as "{type}". ',
    ),
    (
        "Highlight the key elements and their roles within the {event} context.",
        "Element: {word}, Role: {type}; ",
    ),
    (
        "Can you dissect the {event} and label each component with its respective function?",
        "Component: {word}, Function: {type}; ",
    ),
    (
        "Identify and describe the roles of different elements in the {event}.",
        "Element Identified: {word}, Described Role: {type}; ",
    ),
    (
        "Break down the {event} into its essential parts and explain their significance.",
        "Essential Part: {word}, Significance: {type}; ",
    ),
    (
        "Identify the key elements and their functions within the given event.",
        "Element: {word}, Function: {type}. ",
    ),
    (
        "What are the components and their categories in this event?",
        "Component: {word} falls under the category: {type}. ",
    ),
    (
        "Break down the event into its constituents and describe their roles.",
        "Constituent: {word} plays the role of: {type}. ",
    ),
]
# EXPLAN较为奇怪，因此去除EAE部分的output_explain
OUTPUT_EXPLAN = [
    'In the given context, the event "{event}" is associated with the event type "{etype}".',
    'Within the provided context, the event "{event}" is linked to the event type "{etype}".',
    'In the given context, the event "{event}" is connected to the event type "{etype}".',
    'According to the context, the event "{event}" is correlated with the event type "{etype}".',
    'In the provided context, the event "{event}" is aligned with the event type "{etype}".',
    'In the scenario described, the event "{event}" falls under the category of "{etype}".',
    'The narrative provided outlines an event, specifically "{event}", which pertains to the event type "{etype}".',
    'Reflecting on the details, it\'s evident that the event "{event}" is linked to the event type "{etype}".',
    'The analysis reveals that the "{event}" pertains to the "{etype}" category.',
    'Within the context of "{event}", it is evident that it falls under the "{etype}" classification.',
    'Upon dissecting the "{event}", it becomes clear that its nature is best described as "{etype}".',
    'Upon examining the "{event}", it becomes clear that this event is categorized under the "{etype}" type.',
    'Analyzing the "{event}" reveals that it falls under the "{etype}" category, showcasing its diverse elements and their roles.',
    'Delving into the "{event}", it\'s apparent that this event is a manifestation of the "{etype}" type, with each part holding specific significance.',
    'Upon examining the "{event}", it becomes clear that this scenario typifies the "{etype}" category, highlighting the roles and significance of its components.',
    'The detailed analysis of "{event}" reveals its classification as a "{etype}", emphasizing the categorization of its integral parts.',
    'Scrutinizing the event "{event}", it is evident that it exemplifies the "{etype}" genre, delineating the roles of its various constituents.',
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
