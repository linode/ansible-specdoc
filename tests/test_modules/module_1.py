"""Module for testing docs generation functionality"""

from ansible_specdoc.objects import SpecDocMeta, SpecField, FieldType, SpecReturnValue, DeprecationInfo

DOCUMENTATION = '''
really cool non-empty docstring
'''

RETURN = '''
really cool non-empty return string
'''

EXAMPLES = '''
really cool non-empty examples'''

MY_MODULE_DICT_SPEC = {
    'my-int': SpecField(
        type=FieldType.integer,
        required=True,
        editable=True,
        conflicts_with=['my-bool'],
        description=['A really cool required int']
    ),
    'my-bool': SpecField(
        type=FieldType.bool,
        conflicts_with=['my-int'],
        description=[
            'A really cool bool that does stuff',
            'Here\'s another line :)'
        ]
    ),
    'my-hidden-var': SpecField(
        type=FieldType.bool,
        description=[
            'dont show this!!!'
        ],
        doc_hide=True
    )
}

MY_MODULE_SPEC = {
    'my-string': SpecField(
        type=FieldType.string,
        required=True,
        description=['A really cool string that does stuff!'],
    ),
    'my-list': SpecField(
        type=FieldType.list,
        element_type=FieldType.string,
        description=['A really cool list of strings']
    ),
    'my-dict': SpecField(
        type=FieldType.dict,
        suboptions=MY_MODULE_DICT_SPEC,
        description=['A really cool dict']
    )
}

SPECDOC_META = SpecDocMeta(
    description=[
        'My really cool Ansible module!'
    ],
    requirements=[
        'python >= 3.8'
    ],
    author=[
        'Lena Garber'
    ],
    examples=[
        'blah'
    ],
    deprecated=DeprecationInfo(
        why='cuz',
        removed_in='1.0.0',
        alternative='use something else'
    ),
    return_values={
        'cool': SpecReturnValue(
            description='COOL',
            docs_url='http://localhost',
            type=FieldType.list,
            elements=FieldType.string,
            sample=['["COOL"]'],
        )
    },
    options=MY_MODULE_SPEC
)
