import collections
import hashlib
import itertools
import json
import sys

from datetime import datetime


def hash_obj(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode('utf-8')).hexdigest()


def make_transaction(sender, receiver, value, description):
    assert type(sender) is str
    assert type(receiver) is str
    assert type(value) is int
    assert type(description) is str

    txn = {
        'sender': sender,
        'receiver': receiver,
        'value': value,
        'description': description,
        'utctimestamp': int(datetime.utcnow().timestamp()),
    }

    return txn, hash_obj(txn)


def apply_txn(wallets, txn):
    wallets = wallets.copy()

    if txn['receiver'] in wallets:
        wallets[txn['receiver']] += txn['value']
    else:
        wallets[txn['receiver']] = txn['value']

    return wallets


def create_genesis_block():
    contents = {
        'block_number': 0,
        'parent_hash': '',
        'txn': None,
    }

    return {
        'hash': hash_obj(contents),
        'contents': contents,
    }


def create_chain(chain_name, owner):
    return {
        'name': chain_name,
        'owner': owner,
        'students': {},
        'blocks': [create_genesis_block()],
    }


def serialize_chain(chain):
    return json.dumps(chain)


def deserialize_chain(serialized):
    return json.loads(serialized)


def create_block(chain, txn):
    parent_block = chain['blocks'][-1]
    parent_hash = parent_block['hash']
    block_number = parent_block['contents']['block_number'] + 1

    contents = {
        'block_number': block_number,
        'parent_hash': parent_hash,
        'txn': txn
    }

    return {
        'hash': hash_obj(contents),
        'contents': contents
    }


def add_txn(chain, txn):
    block = create_block(chain, txn)
    chain['blocks'].append(block)
    chain['students'] = apply_txn(chain['students'], txn)


def add_student(chain, lecturer, student):
    reg_txn, _ = make_transaction(lecturer, student, 0, 'Add student')
    add_txn(chain, reg_txn)
    return True


def add_grade(chain, lecturer, student, grade, description):
    if student not in chain['students']:
        return False

    grade_txn, _ = make_transaction(lecturer, student, grade, description)
    add_txn(chain, grade_txn)

    return True


def validate_block(parent, block, students):
    parent_hash = parent['hash']
    parent_number = parent['contents']['block_number']

    block_hash = block['hash']
    block_contents = block['contents']
    block_parent_hash = block_contents['parent_hash']
    block_number = block_contents['block_number']
    block_txn = block_contents['txn']

    expected_hash = hash_obj(block['contents'])
    if expected_hash != block_hash:
        raise Exception('Hash does not match contents of block {}'.format(block_number))

    if block_parent_hash != parent_hash:
        raise Exception('Block {} parent hash {} does not match expected parent hash {}'.format(block_number, block_parent_hash, parent_hash))

    if block_number != parent_number+1:
        raise Exception('Block {} does not increment parent number {} by one'.format(block_number, parent_number))

    students = apply_txn(students, block_txn)
    parent_hash = expected_hash

    return students


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


def validate_chain(chain, starting_from=0, starting_hash=None):
    if starting_hash is None:
        assert starting_from == 0
        starting_hash = create_genesis_block()['hash']

    blocks_to_check = chain['blocks'][starting_from:]
    if blocks_to_check[0]['hash'] != starting_hash:
        raise Exception('Starting block hash {} does not match expected hash {}'.format(blocks_to_check[0]['hash'], starting_hash))

    students = {}

    for parent, block in pairwise(blocks_to_check):
        students = validate_block(parent, block, students)

    return students


def get_history(chain):
    students = validate_chain(chain)
    event_bystudent = {student: [] for student in students.keys()}
    event_byevent = collections.defaultdict(list)
    descriptions = set()

    for block in chain['blocks']:
        txn = block['contents']['txn']
        if txn:
            event_bystudent[txn['receiver']].append(txn)
            event_byevent[txn['description']].append(txn)
            if txn['description'] != 'Add student':
                descriptions.add((txn['utctimestamp'], txn['description']))

    descriptions = [d[1] for d in sorted(list(descriptions))]
    matrix = {student: [None] * len(descriptions) for student in students.keys()}
    for i, event in enumerate(descriptions):
        for txn in event_byevent[event]:
            matrix[txn['receiver']][i] = txn

    return event_bystudent, descriptions, matrix
