from random import choice

from flask import flash, render_template, request, send_from_directory

from application import app
from application.conc import jump_to_conclusions
from application.feeds import feed_shouts
from application.forms import ShoutForm, handle_shout
from application.service import handle_variation


@app.route('/', methods=['GET', 'POST'])
def index():
    shout_form = ShoutForm()

    if request.method == 'POST' and shout_form.validate():
        handle_shout(shout_form)

    return render_template(
        'index.html',
        title='monitor',
        shout_form=shout_form
    )


@app.route('/%')
@app.route('/<float:cc>')
@app.route('/<int:cc>')
def conc(cc=0.0):
    conclusions = jump_to_conclusions()

    if cc and cc != conclusions:
        handle_variation(cc, conclusions)

    if conclusions > 9000.0:
        flash('over 9000!!!')

    return render_template(
        'conc.html',
        title='status',
        conclusions=conclusions
    )


@app.route('/api/')
@app.route('/api')
def api():
    return render_template(
        'api.html',
        title='api'
    )


@app.route('/feed.atom')
def atom_feed():
    return feed_shouts()


@app.errorhandler(404)
@app.errorhandler(500)
def page_error(error):
    return render_template(
        'error.html',
        title='kaputt',
        error=error
    ), error.code


@app.route('/favicon.ico')
@app.route('/favicon.png')
@app.route('/logo.png')
def logo():
    return send_from_directory(
        app.static_folder,
        choice(app.config['LOGOS']),
        mimetype='image/png'
    )


@app.route('/bg.png')
def background():
    return send_from_directory(
        app.static_folder,
        'bg{}.png'.format(choice(range(1, 9))),
        mimetype='image/png'
    )
