from flask import request, url_for
from werkzeug.contrib.atom import AtomFeed

from application.service import get_shouts, the_shouts


def feed_shouts():
    shouts = get_shouts()
    feed = AtomFeed(
        author='monitor {}'.format(the_shouts),
        feed_url=request.url,
        logo=url_for('logo', _external=True),
        subtitle='Die letzten {}'.format(the_shouts),
        title='monitor - {}'.format(the_shouts),
        title_type='html',
        url=url_for('index', _external=True, _anchor=the_shouts)
    )

    for shout in shouts.get_data().all():
        feed.add(
            content=shout.value,
            content_type='html',
            title=shout.value,
            title_type='html',
            updated=shout.time,
            url=url_for('index', _anchor='{}_{}'.format(the_shouts, shout.ms()), _external=True)
        )
    return feed.get_response()
