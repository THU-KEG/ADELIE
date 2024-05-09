JSON_BASE = "Please give the answer in json format."

OUTPUT_BASE = [
    (
        'Please give the answer in the tuple form "[Answer]: ({subject}; {relation}; {object})\n".',
        "({head}; {type}; {tail})\n",
    ),
    (
        "Please tell me what the subject is, what the object is, and what is the relationship between them? ",
        'subject is "{head}", object is "{tail}", the relation is "{type}". \n',
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (subject: {subject}; relation: {type}; object: {object})\n".',
        "(subject: {head}; relation: {type}; object: {tail})\n ",
    ),
    (
        'Please give the answer in the tuple form "[Answer]: (head: {subject}; relation: {type}; tail: {object})\n".',
        "(head: {head}; relation: {type}; tail: {tail})\n ",
    ),
    (
        "Please tell me what the head is, what the tail is, and what is the relationship between them? ",
        'the head entity is "{head}", the tail entity is "{tail}", and the relation between them is "{type}".\n',
    ),
    (
        "Identify the relationship between the two entities mentioned. ",
        'Relationship identified: "{head}" is {type} of {tail}.\n',
    ),
    (
        "What's the link between the specified entities? ",
        "Link established: {head} ({type}) {tail}.\n",
    ),
    (
        "Can you determine the connection type between these entities? ",
        "Connection type: {head} - {type} -> {tail}.\n",
    ),
    (
        "Identify the relationship type between the given entities, please. ",
        "Relationship identified: {head} -> {type} -> {tail}.\n",
    ),
    (
        "How are these two entities related to each other? ",
        'Entities\' relation: "{head}" is "{type}" of "{tail}".\n',
    ),
    (
        "Could you extract the relationship between these entities? ",
        "Extracted relationship: {head} [{type}] {tail}.\n",
    ),
    (
        "What's the connection between the mentioned entities? ",
        "Connection: {head} ({type}) {tail}.\n",
    ),
    (
        "Determine the type of link existing between the two entities. ",
        "Link type: {head} -> {type} -> {tail}.\n",
    ),
    (
        "How are these entities related to each other? ",
        'Relation: "{head}" as "{type}" to "{tail}".\n',
    ),
    (
        "Can you identify the nature of the relationship between the given entities? ",
        "Nature of relationship: {head} - {type} - {tail}.\n",
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {entity1}, {entity2}, {head},{type},{tail}
OUTPUT_EXPLAN = [
    'In the provided text, two entities need relationship classification:"{entity1}" and "{entity2}".\nThe established relationship, based on the text and predefined relationships, is "{type}". So "{head}" is the subject and "{tail}" is the object.\nTo sum up, ',
    'Within the given text, two entities requiring relationship classification are "{entity1}" and "{entity2}". The determined relationship, derived from the text and predefined relationships, is denoted as "{type}". Consequently, "{head}" assumes the role of the subject, while "{tail}" serves as the object. In conclusion, ',
    'In the provided text, there are two entities in need of relationship classification: "{entity1}" and "{entity2}". The established relationship, derived from the text and predefined relationships, is identified as ["{type}"]. Thus, "{head}" takes on the role of the subject, with "{tail}" as the object. To summarize, ',
    'Within the presented text, two entities demand relationship classification: "{entity1}" and "{entity2}". The determined relationship, based on the text and predefined relationships, is labeled as ["{type}"]. Consequently, "{head}" assumes the subject position, while "{tail}" assumes the object position. In summary, ',
    'In the given text, two entities, "{entity1}" and "{entity2}", require relationship classification. The established relationship, as derived from the text and predefined relationships, is recognized as ["{type}"]. Accordingly, "{head}" is identified as the subject, and "{tail}" is identified as the object. In conclusion, ',
    'In the context provided, the entities "{entity1}" and "{entity2}" are highlighted for relationship extraction. The relationship identified, as per the context and predefined categories, is "{type}". This establishes "{head}" in the role of {type} in relation to "{tail}". To encapsulate, ',
    'The text brings into focus two entities, "{entity1}" and "{entity2}", for which a link needs to be established. Upon analysis, the link is determined to be "{type}", positioning "{head}" and "{tail}" in a {type} relationship. To distill, ',
    'Upon examining the text, it becomes clear that the entities "{entity1}" and "{entity2}" are under scrutiny for their connection type. The connection, as defined by the text and existing relationship types, is "{type}". This places "{head}" in a direct connection, as {type}, with "{tail}". In essence, ',
    'Upon examining the text, it becomes clear that the entities "{entity1}" and "{entity2}" are in need of a relationship identification. The analysis reveals that the relationship type is "{type}", with "{head}" serving as the initiator and "{tail}" as the recipient. To encapsulate, ',
    'The narrative provided highlights two entities, "{entity1}" and "{entity2}", whose relationship needs to be deciphered. Through careful examination, it is found that "{head}" is the {type} of "{tail}", establishing a clear {type} relationship between them. To put it succinctly, ',
    'In the context provided, "{entity1}" and "{entity2}" emerge as two entities between whom a relationship needs to be extracted. The relationship, upon extraction, is identified as "{type}", placing "{head}" in a direct relationship with "{tail}". To condense, ',
    'The inquiry revolves around the entities "{entity1}" and "{entity2}", seeking to uncover the nature of their connection. The investigation leads to the discovery that "{head}" and "{tail}" are linked by a "{type}" relationship, positioning "{head}" in a pivotal role. To summarize, ',
    'Focusing on the entities "{entity1}" and "{entity2}", the task is to determine the specific type of link they share. The analysis concludes that the link is of the "{type}" variety, with "{head}" acting as the source and "{tail}" as the destination. In essence, ',
    'The question at hand involves the entities "{entity1}" and "{entity2}", with the goal of understanding their mutual relation. It is determined that "{head}" holds the position of {type} in relation to "{tail}", thereby defining their connection. Briefly, ',
    'The task involves the entities "{entity1}" and "{entity2}", with a focus on identifying the nature of their relationship. The findings reveal that the relationship is characterized by "{type}", with "{head}" and "{tail}" being the key players. To distill, ',
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
