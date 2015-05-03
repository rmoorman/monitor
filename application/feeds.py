from flask import url_for
from werkzeug.contrib.atom import AtomFeed

from application.service import get_shouts, the_shouts


def feed_shouts():
    shouts = get_shouts()
    feed = AtomFeed(
        title='monitor - {}'.format(the_shouts),
        title_type='text',
        url=url_for('index', _external=True),
        feed_url=url_for('atom_feed', _external=True),
        subtitle='Die letzten {}'.format(the_shouts),
        author='monitor {}'.format(the_shouts)
    )

    for shout in shouts.get_data().all():
        feed.add(
            title=shout.value,
            title_type='text',
            content=shout.value,
            content_type='text',
            url=url_for('index', _anchor='{}_{}'.format(the_shouts, shout.ms()), _external=True),
            updated=shout.time
        )
    return feed.get_response()
