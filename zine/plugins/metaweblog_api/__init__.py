# -*- coding: utf-8 -*-
"""
    zine.plugins.metaweblog_api
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Adds support for the MetaWeblog API.

    :copyright: (c) 2009 by the Zine Team, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
"""
from zine.api import get_request, url_for, db
from zine.utils.xml import XMLRPC, Fault
from zine.models import User, Post


def authenticated(f):
    def proxy(some_id, username, password, *args):
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            raise Fault(403, 'Bad login/pass combination.')

        # store the user on the request object so that the functions
        # inside Zine work on the request of this user.
        request = get_request()
        request.user = user
        return f(request, some_id, *args)
    proxy.__name__ = f.__name__
    return proxy


def dump_post(post):
    """Dumps a post into a structure for the MetaWeblog API."""
    text = post.body.to_html()
    if post.intro:
        text = u'<div class="intro">%s</div>%s' % (post.intro.to_html(), text)

    return dict(
        pubDate=post.pub_date,
        title=post.title,
        link=url_for(post, _external=True),
        description=text,
        author=post.author.email,
        categories=sorted(set([x.name for x in post.tags] +
                              [x.name for x in post.categories]),
                          key=lambda x: x.lower()),
        postid=post.id
    )


def extract_text(struct):
    text = struct.get('description', '')
    excerpt = struct.get('post_excerpt')
    if excerpt:
        text = u'<intro>%s</intro>\n%s' % (excerpt, text)
    return text


def select_parser(app, struct):
    parser = struct.get('parser')
    if parser is None:
        return 'html'
    if parser not in app.parsers:
        raise Fault(500, 'unknown parser')
    return parser


@authenticated
def metaweblog_new_post(request, blog_id, struct, publish):
    text = extract_text(struct)
    post = Post(struct['title'], request.user, text,
                parser=select_parser(request.app, struct))
    link = url_for(post, _external=True)
    db.commit()
    return dump_post(post)


@authenticated
def metaweblog_edit_post(request, post_id, struct, publish):
    post = Post.query.get(post_id)
    if post is None:
        raise Fault(404, "No such post")
    post.parser = select_parser(request.app, struct)
    post.title = struct['title']
    post.text = extract_text(struct)
    db.commit()
    return dump_post(post)


@authenticated
def metaweblog_get_post(request, post_id):
    post = Post.query.get(post_id)
    if post is None:
        raise Fault(404, "No such post")
    if not post.can_read():
        raise Fault(403, "You don't have access to this post")
    return dump_post(post)


@authenticated
def metaweblog_get_recent_posts(request, blog_id, number_of_posts):
    number_of_posts = min(50, number_of_posts)
    # XXX: filter the ones you can't read (could this be the case?)
    return map(dump_post, Post.query.limit(number_of_posts).all())


service = XMLRPC()

# MetaWeblog
service.register_function(metaweblog_new_post, 'metaWeblog.newPost')
service.register_function(metaweblog_edit_post, 'metaWeblog.editPost')
service.register_function(metaweblog_get_post, 'metaWeblog.getPost')
service.register_function(metaweblog_get_recent_posts, 'metaWeblog.getRecentPosts')


def setup(app, plugin):
    app.add_api('MetaWeblog', True, service)