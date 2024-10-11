prove_instructions='''I will give you a few given conditions and you need to prove one conclusion based on these conditions.

You need to list all the deductive process in a json style. For each step, you need to list:
* condition: the conditions you use to conduct deduction,
* conclusion: the conclusion you get,
* format conclusion: a dictionary which has below three terms:
    ** Subject: the subject of your conclusion, which should be an affirmed noun.
    ** Predication: the prediate of your conclusion, which should be an affirmed noun.
    ** type: which is one in ['A','E','I','O']. The type of one proposition with subject $S$ and predicate $P$:
        *** Type 'A': 'all $S$ are $P$', or '$S$ is $P$'.
        *** Type 'E': 'None of $S$ is $P$', or '$S$ is not $P$'.
        *** Type 'I': 'There exists one $S$ that is $P$'.
        *** Type 'O': 'There exists one $S$ that is not $P$'.

Notice that the final conclusion, that you need to prove, should be included in your step list.

Your answer should be return with below format:
{'steps': [
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ],
    [
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ],[
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ]
}
Examples:
##Examples_Input:
We have:
ilbbqczyebob is xanyhtaely.
glmtwxtayo is gmljjd.
There is one aazjzja that is wimiypxnhcolau.
None of xanyhtaely is glmtwxtayo.
There is one ilbbqczyebob that is aazjzja.
Prove "There exists a aazjzja that is not glmtwxtayo."
##Examples_Output:
{
  "steps": [
    {
      "condition": ["ilbbqczyebob is xanyhtaely", "None of xanyhtaely is glmtwxtayo"],
      "conclusion": ["No ilbbqczyebob is glmtwxtayo"],
      "format_conclusion": {"Subject": "ilbbqczyebob", "Predicate": "glmtwxtayo", "type": "E"}
    },
    {
      "condition": ["There is one ilbbqczyebob that is aazjzja", "No ilbbqczyebob is glmtwxtayo"],
      "conclusion": ["There exists a aazjzja that is not glmtwxtayo"],
      "format_conclusion": {"Subject": "aazjzja", "Predicate": "glmtwxtayo", "type": "O"}
    }
  ],
}

##Examples_Input:
We have:
All Xi are RHO.
There exists a PI that is MU.
All IOTA are MU.
There is one IOTA that is Xi.
Prove: "There is one RHO that is MU."
##Examples_Output:
{
"steps": [
{
"condition": ["There is one IOTA that is Xi", "All Xi are RHO"],
"conclusion": "There is one IOTA that is RHO",
"format_conclusion": {"Subject": "IOTA", "Predicate": "RHO", "type": "I"}
},
{
"condition": ["All IOTA are MU", "There is one IOTA that is RHO"],
"conclusion": "There is one RHO that is MU",
"format_conclusion": {"Subject": "RHO", "Predicate": "MU", "type": "I"}
}
]
}
'''

check_instructions='''I will give you a few given conditions and you need to check whether a given conclusion is correct or not based on these conditions.

You need to list all the deductive process in a json style. For each step, you need to list:
* condition: the conditions you use to conduct deduction,
* conclusion: the conclusion you get,
* format conclusion: a dictionary which has below three terms:
    ** Subject: the subject of your conclusion, which should be an affirmed noun.
    ** Predication: the prediate of your conclusion, which should be an affirmed noun.
    ** type: which is one in ['A','E','I','O']. The type of one proposition with subject $S$ and predicate $P$:
        *** Type 'A': 'all $S$ are $P$', or '$S$ is $P$'.
        *** Type 'E': 'None of $S$ is $P$', or '$S$ is not $P$'.
        *** Type 'I': 'There exists one $S$ that is $P$'.
        *** Type 'O': 'There exists one $S$ that is not $P$'.
Finally you should give a 'result' if you are required to check whether the given conclusion is correct or not. If it is correct, return 'Correct'; otherwise, return 'Wrong'.

Your answer should be return with below format:
{'steps': [
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ],
    [
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ],[
        'condition': ['xxxxx', 'xxxxx'],
        'conclusion': ['xxxxx'],
        'format_conclusion': {'Subject': 'xxxx', 'Predicate': 'xxxxxx', 'type', 'x'}
    ],
    'result': 'xxx'
}
Examples:
##Examples_Input:
We have:
ilbbqczyebob is xanyhtaely.
glmtwxtayo is gmljjd.
There is one aazjzja that is wimiypxnhcolau.
None of xanyhtaely is glmtwxtayo.
There is one ilbbqczyebob that is aazjzja.
Show "There exists a aazjzja that is not glmtwxtayo." is correct or not.
##Examples_Output:
{
  "steps": [
    {
      "condition": ["ilbbqczyebob is xanyhtaely", "None of xanyhtaely is glmtwxtayo"],
      "conclusion": ["No ilbbqczyebob is glmtwxtayo"],
      "format_conclusion": {"Subject": "ilbbqczyebob", "Predicate": "glmtwxtayo", "type": "E"}
    },
    {
      "condition": ["There is one ilbbqczyebob that is aazjzja", "No ilbbqczyebob is glmtwxtayo"],
      "conclusion": ["There exists a aazjzja that is not glmtwxtayo"],
      "format_conclusion": {"Subject": "aazjzja", "Predicate": "glmtwxtayo", "type": "O"}
    }
  ],
  "result": "Correct"
}

##Examples_Input:
We have:
All Xi are RHO.
There exists a PI that is MU.
All IOTA are MU.
There is one IOTA that is Xi.
Show "All RHO are not MU." is correct or not.
##Examples_Output:
{
"steps": [
{
"condition": ["There is one IOTA that is Xi", "All Xi are RHO"],
"conclusion": "There is one IOTA that is RHO",
"format_conclusion": {"Subject": "IOTA", "Predicate": "RHO", "type": "I"}
},
{
"condition": ["All IOTA are MU", "There is one IOTA that is RHO"],
"conclusion": "There is one RHO that is MU",
"format_conclusion": {"Subject": "RHO", "Predicate": "MU", "type": "I"}
}
],
"result": "Wrong"
}
'''

input_template='''
##Input:
{}
##Output:
'''