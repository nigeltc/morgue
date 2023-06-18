"""MORGUE - A simple corpus manager"""
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///corpora.db'
db = SQLAlchemy(app)

class Corpus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)

    def __repr__(self):
        return f'Corpus({self.name})'

class Story(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(50), unique=True, nullable=False)
    corpus_id = db.Column(db.Integer, db.ForeignKey('corpus.id'), nullable=False)

    def __repr__(self):
        return f'Story({self.headline})'

@app.route('/')
def home():
    corpora = Corpus.query.all()
    return render_template('home.html', corpora=corpora)

@app.route('/corpus/create', methods=['GET', 'POST'])
def create_corpus():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        corpus = Corpus(name=name, description=description)
        db.session.add(corpus)
        db.session.commit()
        return redirect('/')
    return render_template('create_corpus.html')

@app.route('/corpus/<int:corpus_id>')
def view_corpus(corpus_id):
    corpus = Corpus.query.get_or_404(corpus_id)
    stories = Story.query.filter_by(corpus_id=corpus.id).all()
    return render_template('view_corpus.html', corpus=corpus, stories=stories)

@app.route('/corpus/<int:corpus_id>/story/create', methods=['GET', 'POST'])
def create_story(corpus_id):
    corpus = Corpus.query.get_or_404(corpus_id)
    if request.method == 'POST':
        headline = request.form['headline']
        body = request.form['body']
        file = request.files['file']
        filename = file.filename
        story = Story(headline=headline, body=body, filename=filename, corpus_id=corpus.id)
        db.session.add(story)
        db.session.commit()
        file.save(os.path.join(app.root_path, 'static', 'uploads', filename))
        return redirect(url_for('view_corpus', corpus_id=corpus.id))
    return render_template('create_story.html', corpus=corpus)

@app.route('/corpus/<int:corpus_id>/story/<int:story_id>/delete', methods=['POST'])
def delete_story(corpus_id, story_id):
    story = Story.query.get_or_404(story_id)
    db.session.delete(story)
    db.session.commit()
    return redirect(url_for('view_corpus', corpus_id=corpus_id))

if __name__ == '__main__':
    app.run(debug=True)
