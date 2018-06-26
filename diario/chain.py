from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from flask import current_app as app
from diario.auth import login_required, must_be_in_class, must_be_lecturer
from diario.db import get_db
from diario.core import *
from werkzeug.security import generate_password_hash

bp = Blueprint('chain', __name__)


@bp.route('/')
@login_required
def index():
    db = get_db()
    chains = db.execute(
        'SELECT c.id, c.name, c.owner_id, owner.username FROM chain c JOIN user owner ON c.owner_id = owner.id, user_chain uc WHERE c.id = uc.chain_id AND uc.user_id = ?', (g.user['id'],)
    ).fetchall()
    return render_template('chain/index.html', chains=chains)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
@must_be_lecturer
def create():
    """Create a new post for the current user."""
    if request.method == 'POST':
        name = request.form['name']
        lecturer = g.user['username']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            chain = create_chain(chain_name=name, owner=lecturer)
            chain = serialize_chain(chain)

            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                'INSERT INTO chain (owner_id, name, data)'
                ' VALUES (?, ?, ?)',
                (g.user['id'], name, chain)
            )
            db.commit()
            cursor.execute(
                'INSERT INTO user_chain (chain_id, user_id) VALUES (?, ?)',
                (cursor.lastrowid, g.user['id'])
            )
            db.commit()
            cursor.close()
            return redirect(url_for('chain.index'))

    return render_template('chain/create.html')


def load_chain(chain_id):
    dbdata = get_db().execute(
        'SELECT name, data FROM chain WHERE id = ?', (chain_id,)
    ).fetchone()
    return dbdata['name'], deserialize_chain(dbdata['data'])


@bp.route('/<int:chain_id>', methods=('GET', 'POST'))
@login_required
@must_be_in_class
def chain_get(chain_id):
    if request.method == 'POST':
        _, chain = load_chain(chain_id)

        description = request.form['description']

        for grade in request.form:
            if grade.startswith('student-'):
                student = grade[len('student-'):]
                value = int(request.form[grade])
                add_grade(chain, g.user['username'], student, value, description)

        db = get_db()
        db.execute(
            'UPDATE chain SET data = ? WHERE id = ?',
            (serialize_chain(chain), chain_id)
        )
        db.commit()
        return redirect(url_for('chain.chain_get', chain_id=chain_id))

    chain_name, chain = load_chain(chain_id)

    students = validate_chain(chain)
    events, descriptions, matrix = get_history(chain)

    return render_template('chain/details.html', chain={
                                                    'id': chain_id,
                                                    'name': chain_name,
                                                },
                                                students=students,
                                                events=events,
                                                descriptions=descriptions,
                                                matrix=matrix)


@bp.route('/<int:chain_id>/raw')
@login_required
@must_be_in_class
def chain_raw(chain_id):
    _, chain = load_chain(chain_id)
    return app.response_class(
        response=serialize_chain(chain),
        status=200,
        mimetype='application/json'
    )


@bp.route('/<int:chain_id>/new_student', methods=('GET', 'POST'))
@login_required
@must_be_lecturer
@must_be_in_class
def chain_new_student(chain_id):
    if request.method == 'POST':
        name = request.form['name']

        _, chain = load_chain(chain_id)
        add_student(chain, g.user['username'], name)

        db = get_db()
        db.execute(
            'UPDATE chain SET data = ? WHERE id = ?',
            (serialize_chain(chain), chain_id)
        )
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO user (username, password) VALUES (?, ?)',
            (name, generate_password_hash('123'))
        )
        db.commit()
        cursor.execute(
            'INSERT INTO user_chain (user_id, chain_id) VALUES (?, ?)',
            (cursor.lastrowid, chain_id)
        )
        db.commit()
        cursor.close()

        return redirect(url_for('chain.chain_get', chain_id=chain_id))

    return render_template('chain/new_student.html')

