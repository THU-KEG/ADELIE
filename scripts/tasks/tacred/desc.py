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
        "Identify the relationship between the two entities mentioned in the text, including the roles of subject and object.",
        'The subject "{head}" and the object "{tail}" are linked by the relation "{type}".\n',
    ),
    (
        "What is the connection between the entities mentioned? Please specify who or what plays the subject and object roles.",
        'Connection: "{head}" (Subject) -> "{type}" (Relation) -> "{tail}" (Object).\n',
    ),
    (
        "Can you extract and describe the relationship between the mentioned entities, including their roles as subject and object?",
        'Between "{head}" and "{tail}", the relationship is "{type}".\n',
    ),
    (
        "Detail the type of relationship existing between the entities, specifying their roles.",
        'In this relationship, "{head}" acts as the subject, while "{tail}" takes the role of the object, through the "{type}" relation.\n',
    ),
    (
        "What is the nature of the relationship between the specified entities, and what roles do they play?",
        '"{head}" is the subject and "{tail}" is the object in the "{type}" relationship.\n',
    ),
    (
        "Explain the connection between the entities mentioned, including their respective roles.",
        'The connection between "{head}" and "{tail}" is defined by the "{type}" relationship, with "{head}" as the subject and "{tail}" as the object.\n',
    ),
    (
        "Could you determine the relationship type between the highlighted entities and their roles?",
        'The relationship "{type}" exists between "{head}", the subject, and "{tail}", the object.\n',
    ),
    (
        "Describe the linkage between the given entities, specifying their roles within the relationship.",
        'Linkage: "{head}" (subject) to "{tail}" (object) via "{type}" relationship.\n',
    ),
    (
        "Can you extract and describe the type of connection existing between the highlighted entities, including their respective roles?",
        'In the "{type}" connection, "{head}" acts as the subject, while "{tail}" takes on the role of the object.\n',
    ),
    (
        "Please clarify the relationship and roles of the entities under discussion.",
        'Between "{head}" and "{tail}", a "{type}" relationship is established, with "{head}" being the subject and "{tail}" the object.\n',
    ),
]
# (prefix,to_type,summary): prefix+ (multi) to_type+summary+[Answer]:+output_base
# {entity1},{etype1},{entity2},{etype2},{head},{type},{tail}
OUTPUT_EXPLAN = [
    'In the provided text, two entities need relationship classification:"{entity1}" (classified as "{etype1}") and "{entity2}" (classified as "{etype2}").\nThe established relationship, based on the text and predefined relationships, is "{type}". So "{head}" is the subject and "{tail}" is the object.\nTo sum up, ',
    'Within the given text, two entities requiring relationship classification are "{entity1}" (designated as "{etype1}") and "{entity2}" (designated as "{etype2}"). The determined relationship, derived from the text and predefined relationships, is denoted as "{type}". Consequently, "{head}" assumes the role of the subject, while "{tail}" serves as the object. In conclusion, ',
    'In the provided text, there are two entities in need of relationship classification: "{entity1}" (categorized as "{etype1}") and "{entity2}" (categorized as "{etype2}"). The established relationship, derived from the text and predefined relationships, is identified as ["{type}"]. Thus, "{head}" takes on the role of the subject, with "{tail}" as the object. To summarize, ',
    'Within the presented text, two entities demand relationship classification: "{entity1}" (classified as "{etype1}") and "{entity2}" (classified as "{etype2}"). The determined relationship, based on the text and predefined relationships, is labeled as ["{type}"]. Consequently, "{head}" assumes the subject position, while "{tail}" assumes the object position. In summary, ',
    'In the given text, two entities, "{entity1}" (categorized as "{etype1}") and "{entity2}" (categorized as "{etype2}"), require relationship classification. The established relationship, as derived from the text and predefined relationships, is recognized as ["{type}"]. Accordingly, "{head}" is identified as the subject, and "{tail}" is identified as the object. In conclusion, ',
    'Upon analyzing the text, it becomes clear that the entities "{entity1}" (as "{etype1}") and "{entity2}" (as "{etype2}") are involved in a specific relationship. This relationship is categorized as "{type}". Accordingly, "{head}" is identified as the subject and "{tail}" as the object. In essence, ',
    'The text highlights a connection between "{entity1}" (identified as "{etype1}") and "{entity2}" (identified as "{etype2}"). This connection is defined by the relationship "{type}", placing "{head}" in the subject role and "{tail}" in the object role. Essentially, ',
    'The narrative provided introduces two entities, "{entity1}" (described as "{etype1}") and "{entity2}" (described as "{etype2}"), that share a relationship. This relationship is precisely "{type}", with "{head}" serving as the subject and "{tail}" as the object. Briefly, ',
    'The discourse introduces two entities, "{entity1}" (tagged as "{etype1}") and "{entity2}" (tagged as "{etype2}"), linked by a specific type of relationship. This relationship is denoted as "{type}", with "{head}" playing the role of the subject and "{tail}" that of the object. In brief, ',
    'The text highlights two entities that require relationship identification: "{entity1}" (identified as "{etype1}") and "{entity2}" (identified as "{etype2}"). The relationship, as inferred from the text and predefined relationships, is "{type}". Thus, "{head}" is identified as the subject and "{tail}" as the object. To encapsulate, ',
    'The narrative provides two entities in need of relationship elucidation: "{entity1}" (tagged as "{etype1}") and "{entity2}" (tagged as "{etype2}"). The relationship, as deduced from the text and predefined relationships, is "{type}". Therefore, "{head}" is the subject and "{tail}" is the object. To summarize, ',
    'The text introduces two entities for relationship determination: "{entity1}" (noted as "{etype1}") and "{entity2}" (noted as "{etype2}"). The relationship, as derived from the text and predefined relationships, is "{type}". Hence, "{head}" is the subject and "{tail}" is the object. Briefly, ',
    'The discourse presents two entities that necessitate relationship specification: "{entity1}" (referred to as "{etype1}") and "{entity2}" (referred to as "{etype2}"). The relationship, as extrapolated from the text and predefined relationships, is "{type}". As a result, "{head}" is the subject and "{tail}" is the object. In brief, ',
    'The text highlights two entities, "{entity1}" (identified as "{etype1}") and "{entity2}" (identified as "{etype2}"), which are connected by a certain type of relationship. This relationship is classified as "{type}", positioning "{head}" in the role of the subject and "{tail}" as the object. Summarizing, ',
    'In the discussion, two entities, "{entity1}" (categorized as "{etype1}") and "{entity2}" (categorized as "{etype2}"), are presented for analysis. The relationship connecting them is identified as "{type}", which assigns "{head}" as the subject and "{tail}" as the object. In essence, ',
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
