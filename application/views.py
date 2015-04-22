from flask import render_template, request, send_from_directory
from random import choice

from application import app
from application.forms import ShoutForm
from application.service import handle_shout, handle_variation, jump_to_conclusions_mat


@app.route('/', methods=['GET', 'POST'])
def index():
    shout_form = ShoutForm()

    if request.method == 'POST' and shout_form.validate():
        handle_shout(shout_form)

    return render_template(
        'index.html',
        title='index',
        shout_form=shout_form
    )


@app.route('/%')
@app.route('/<float:cc>%')
@app.route('/<float:cc>')
@app.route('/<int:cc>%')
@app.route('/<int:cc>')
def conc(cc=0.0):
    conclusions = jump_to_conclusions_mat()

    if cc != conclusions[0]:
        handle_variation(cc, conclusions[0])

    return render_template(
        'conc.html',
        title='{}%'.format(conclusions[0]),
        conclusions=conclusions
    )


@app.route('/api/')
@app.route('/api')
def api():
    return render_template(
        'api.html',
        title='api'
    )


@app.errorhandler(404)
@app.errorhandler(500)
def page_error(error):
    return render_template(
        'error.html',
        title='kaputt',
        error=error
    )


@app.route('/favicon.ico')
@app.route('/favicon.png')
@app.route('/logo.png')
def logo():
    return send_from_directory(
        app.static_folder,
        choice([
            'evil_man.png',
            'plug.png'
        ]),
        mimetype='image/png'
    )
