"""Module for testing docs generation functionality"""

from ansible_specdoc.objects import SpecDocMeta, SpecField, FieldType, SpecReturnValue

DOCUMENTATION = '''
really cool non-empty docstring
'''

MY_MODULE_DICT_SPEC = {
    'my-int': SpecField(
        type=FieldType.Integer,
        required=True,
        editable=True,
        conflicts_with=['my-bool'],
        description=['A really cool required int']
    ),
    'my-bool': SpecField(
        type=FieldType.Bool,
        conflicts_with=['my-int'],
        description=[
            'A really cool bool that does stuff',
            'Here\'s another line :)'
        ]
    ),
    'my-hidden-var': SpecField(
        type=FieldType.Bool,
        description=[
            'dont show this!!!'
        ],
        doc_hide=True
    )
}

MY_MODULE_SPEC = {
    'my-string': SpecField(
        type=FieldType.String,
        required=True,
        description=['A really cool string that does stuff!'],
    ),
    'my-list': SpecField(
        type=FieldType.List,
        element_type=FieldType.String,
        description=['A really cool list of strings']
    ),
    'my-dict': SpecField(
        type=FieldType.Dict,
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
    return_values={
        'cool': SpecReturnValue(
            description='COOL',
            docs_url='http://localhost',
            type=FieldType.List,
            elements=FieldType.String,
            sample=['["COOL"]'],
        )
    },
    options=MY_MODULE_SPEC
)
