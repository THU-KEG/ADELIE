

Prompt='''Please generate a step-by-step explanation for [Answer] based on [Question], and give reasons for each step.
The generated explanation should make use of the content in the [Question] as much as possible, and must be consistent with the [Answer]. 
It will eventually be provided at the front of the answer. 
No more than {words_number} words.'''

Content='''
[Question]: {input}

[Answer]: {output}
[Step-by-Step Explanation]: 
'''

Demo=[]
    