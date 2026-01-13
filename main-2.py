from flask import Flask, render_template, request, redirect, url_for, flash
from articles_structure import db, Publication, Article, Tag
from sqlalchemy import text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///articles.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret_key_here'

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/add_article', methods=['GET', 'POST'])
def add_article():
    if request.method == 'POST':
        href = request.form['href']
        title = request.form['title']
        full_text = request.form['full_text']
        tag_name = request.form['tag']
        pub_day = request.form['pub_day']

        # Проверка на существование статьи с таким href (потому что у href не повторяются)
        existing_article = Article.query.filter_by(href=href).first()
        tag = Tag.query.filter_by(name=tag_name).first()

        if existing_article:
            # Если статья уже существует
            if tag:
                if tag in existing_article.tags:
                    return 'Статья с таким URL уже существует и тег уже добавлен! Выбери или другую статью, или другой тэг!'
                else:
                    # Если тег существует, но не связан с этой статьей
                    existing_article.tags.append(tag)
                    db.session.commit()
                    return 'Статья уже существует, но с другим тэгом. Этот тег был добавлен к ней!'
            else:
                # Если тег не существует, создаем новый тег
                new_tag = Tag(name=tag_name)
                db.session.add(new_tag)
                existing_article.tags.append(new_tag)
                db.session.commit()
                return 'Статья уже существует, новый тег был добавлен к ней! Такой тэг еще не встречался в нашей базе данных! Молодец!'
        else:
            # Создаем новую статью, если такой не существует
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)

            publication = Publication.query.filter_by(pub_day=pub_day).first()

            if not publication:
                publication = Publication(pub_day=pub_day)
                db.session.add(publication)

            # Создаем статью
            article = Article(href=href, title=title, full_text=full_text)
            article.publications.append(publication)
            article.tags.append(tag)

            db.session.add(article)
            db.session.commit()

            return 'Спасибо, что пополнили нашу базу данных. Статья добавлена!'

    return render_template('add_article.html')


# Нахождение всех статей с определенным тэгом
@app.route('/article_by_tag', methods=['GET', 'POST'])
def article_by_tag():
    if request.method == 'POST':
        tag_name = request.form.get('tag')
        tags = Tag.query.filter_by(name=tag_name).all()

        if tags:
            articles_t = Article.query.filter(Article.tags.any(
                Tag.tag_id.in_([tg.tag_id for tg in tags]))).all()
        else:
            articles_t = []

        return render_template('article_by_tag.html', articles=articles_t, tag_name=tag_name)

    return render_template('article_by_tag.html', articles=[], tag_name=None)


# Нахождение всех статей по дате публикации
@app.route('/article_by_date', methods=['GET', 'POST'])
def article_by_date():
    if request.method == 'POST':
        pub_day = request.form.get('pub_day')
        publications = Publication.query.filter_by(pub_day=pub_day).all()

        if publications:
            articles = Article.query.filter(Article.publications.any(
                Publication.publication_id.in_([pub.publication_id for pub in publications]))).all()
        else:
            articles = []

        return render_template('article_by_date.html', articles=articles, pub_day=pub_day)

    return render_template('article_by_date.html', articles=[], pub_day=None)


@app.route('/statistics', methods=['GET'])
def statistics():
    # Общее количество статей
    total_articles_query = text("SELECT COUNT(*) FROM articles")
    total_articles = db.session.execute(total_articles_query).scalar()

    # Общее число тэгов
    total_tags_query = text("SELECT COUNT(*) FROM tags")
    total_tags = db.session.execute(total_tags_query).scalar()

    # Общее число дат
    total_days_query = text("SELECT COUNT(*) FROM publication")
    total_days = db.session.execute(total_days_query).scalar()

    # Дата с наибольшим количеством статей
    most_articles_date_query = text("""
        SELECT pub_day, COUNT(*) as article_count
        FROM publication
        JOIN article_publication ON publication.publication_id = article_publication.publication_id
        GROUP BY pub_day
        ORDER BY article_count DESC
        LIMIT 1
    """)
    most_articles_date = db.session.execute(most_articles_date_query).fetchone()

    # Топ-5 самых частотных тегов
    top_tags_query = text("""
        SELECT t.name, COUNT(*) as tag_count
        FROM tags t
        JOIN article_tags at ON t.tag_id = at.tag_id
        GROUP BY t.name
        ORDER BY tag_count DESC
        LIMIT 5
    """)
    top_tags = db.session.execute(top_tags_query).fetchall()

    return render_template('statistics.html', total_articles=total_articles, total_tags=total_tags, total_days=total_days,
                           most_articles_date=most_articles_date,
                           top_tags=top_tags)


if __name__ == "__main__":
    app.run(debug=True)
