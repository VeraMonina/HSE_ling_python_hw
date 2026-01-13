from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = 'articles'

    article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    href = db.Column(db.Text, nullable=False, unique=True)
    title = db.Column(db.Text, nullable=False)
    full_text = db.Column(db.Text, nullable=False)

    # Связь с таблицей publication через промежуточную таблицу
    publications = db.relationship('Publication', secondary='article_publication', back_populates='articles')

    # Связь с тегами через промежуточную таблицу
    tags = db.relationship('Tag', secondary='article_tags', back_populates='articles')


class Publication(db.Model):
    __tablename__ = 'publication'

    publication_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pub_day = db.Column(db.Text, nullable=False, unique=True)

    # Связь с статьями через промежуточную таблицу
    articles = db.relationship('Article', secondary='article_publication', back_populates='publications')


class ArticlePublication(db.Model):
    __tablename__ = 'article_publication'

    article_id = db.Column(db.Integer, db.ForeignKey('articles.article_id'), primary_key=True)
    publication_id = db.Column(db.Integer, db.ForeignKey('publication.publication_id'), primary_key=True)


class Tag(db.Model):
    __tablename__ = 'tags'

    tag_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    # Связь со статьями через промежуточную таблицу
    articles = db.relationship('Article', secondary='article_tags', back_populates='tags')


class ArticleTag(db.Model):
    __tablename__ = 'article_tags'

    article_id = db.Column(db.Integer, db.ForeignKey('articles.article_id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.tag_id'), primary_key=True)

