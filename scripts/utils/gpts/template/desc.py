DATASETS=["ace2005-eae","maven-arg","rams","ace2005-ed","maven-ed","ace2005-ner","conll-2003","ontonotes5","fewrel","tacred","maven-ere"]
# 更新 task and elements
PROMPT='''
You need to follow the template list to come up with a set of diverse templates. 
The task indicated by this template is the "Event Relation Extraction" task. We need to write the input format and corresponding output format template for it.
The output contains two parts, one is "explanation" and the other is "answer".
The explanation template content should include the following strings to facilitate subsequent replacement of the content: {e1}, {e2}, {entitytype1}, {entitytype2}.
The answer template content should include the following strings to facilitate subsequent replacement of the content: {head}, {type}, {tail}.

Here are the requirements:
1. Try not to repeat the verb for each template to maximize diversity.
2. The language used for the template also should be diverse. For example, use interrogative sentences, imperative sentences, etc.
3. Do not repeat the format of the answer template, nor repeat the examples given.
4. The templates should be in English.

'''
OUTPUT_BASE=[
    ('Please give the answer in the tuple form "[Answer]: ({first event}; {relation}; {second event});".','({head}; {type}; {tail}); '),
    ('Please tell me what is the relationship between the two events? ','first event is "{head}", second event is "{tail}", the relation is "{type}". '),
    ('Please give the answer in the tuple form "[Answer]: (first event: {head}; relation: {type}; second event: {tail}); ".','(first event: {head}; relation: {type}; second event: {tail}); '),
    ('Please give the answer in the tuple form "[Answer]: (head: {head}; relation: {type}; tail: {tail}); ".','(head: {head}; relation: {type}; tail: {tail}); '),
    ('Please give the answer in natural language.','the head event is "{head}", the tail event is "{tail}", and the relation between them is "{type}".'),
    ('Identify the relationship between the following events and present your findings in the format "[Answer]: {head} is related to {tail} by {type}."', '{head} is related to {tail} by {type}.'),
    ('How do these events connect? Please format your response as "[Answer]: The connection between {head} and {tail} is described as {type}."', 'The connection between {head} and {tail} is described as {type}.'),
    ('Can you determine the link between these occurrences? Respond in the structure "[Answer]: Linking {head} to {tail} through {type}."', 'Linking {head} to {tail} through {type}.'),
    ('What\'s the relation between the given events? Use the format "[Answer]: Between {head} and {tail}, the relation is {type}." for your answer.', 'Between {head} and {tail}, the relation is {type}.'),
    ('What is the connection between these two events? Please format your response as "[Answer]: The bond between {head} and {tail} is {type}."', 'The bond between {head} and {tail} is {type}.'),
    ('How do these events relate to each other? Frame your answer like this: "[Answer]: {head} and {tail} are intertwined by {type}."', '{head} and {tail} are intertwined by {type}.'),
    ('Explain the relationship between the given events in the format "[Answer]: A {type} relationship exists between {head} and {tail}."', 'A {type} relationship exists between {head} and {tail}.'),
    ('Identify the relationship between the following events.', 'Between the events, {head} acts as the initiator and {tail} as the receiver, establishing a {type} relationship.'),
    ('What binds these two events together? Elaborate in your response.', 'The bond that unites {head} with {tail} is fundamentally a {type} connection.'),
    ('Can you determine the type of interaction between these events?', 'The interaction type between {head} and {tail} is classified as {type}.')
]
OUTPUT_EXPLAN=[
    'The two events are "{e1}" (classified as "{entitytype1}") and "{e2}" (classified as "{entitytype2}"). ',
    'Two events, "{e1}" (classified as "{entitytype1}") and "{e2}" (classified as "{entitytype2}"), are recognized. ',
    'The identified events are "{e1}" (classified as "{entitytype1}") and "{e2}" (classified as "{entitytype2}"). ',
    'In the context of event relation extraction, the two events are identified as "{e1}" (classified as "{entitytype1}") and "{e2}" (classified as "{entitytype2}"). ',
    'The events "{e1}" (classified as "{entitytype1}") and "{e2}" (classified as "{entitytype2}") have been distinguished. ',
    'Upon analysis, it\'s found that the events "{e1}" (categorized under "{entitytype1}") and "{e2}" (categorized under "{entitytype2}") are interconnected. ',
    'The connection is between "{e1}", which is an instance of "{entitytype1}", and "{e2}", which falls under the category of "{entitytype2}". ',
    'The linkage is discerned between the occurrences "{e1}" (identified as "{entitytype1}") and "{e2}" (identified as "{entitytype2}"). ',
    'The relationship involves "{e1}", a "{entitytype1}" event, and "{e2}", a "{entitytype2}" event. ',
    'The investigation reveals a connection between the events "{e1}" (identified as "{entitytype1}") and "{e2}" (identified as "{entitytype2}"). ',
    'The analysis indicates that the events "{e1}" (belonging to the category "{entitytype1}") and "{e2}" (belonging to the category "{entitytype2}") have a relationship. ',
    'After thorough examination, it is evident that there is a "{type}" relationship between "{e1}", which is a type of "{entitytype1}", and "{e2}", which is a type of "{entitytype2}". ',
    'An analysis indicates a relationship where "{e1}" (categorized under "{entitytype1}") initiates an action affecting "{e2}" (categorized under "{entitytype2}"). ',
    'Upon examination, the bond linking "{e1}" (termed as "{entitytype1}") with "{e2}" (termed as "{entitytype2}") is uncovered. ',
    'The interaction between the events "{e1}" (designated as "{entitytype1}") and "{e2}" (designated as "{entitytype2}") is scrutinized. '
]