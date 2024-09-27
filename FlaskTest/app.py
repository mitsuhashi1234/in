import requests
from bs4 import BeautifulSoup

def scrape_rhymes(word):
    URL = f"https://in-note.com/?word={word}"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    
    # 仮のHTML構造に基づく韻を踏んだ言葉の取得例
    rhymes = []
    for item in soup.find_all('div', class_='word-box'):
        rhymes.append(item.text.strip())
    
    return rhymes

# スクレイピング結果の確認
word = "example"  # 例として "example" を使用
rhymes = scrape_rhymes(word)
print(rhymes)

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rhymes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Rhyme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False)
    rhyme = db.Column(db.String(100), nullable=False)

db.create_all()

def save_to_db(word, rhymes):
    for rhyme in rhymes:
        if not Rhyme.query.filter_by(word=word, rhyme=rhyme).first():
            new_rhyme = Rhyme(word=word, rhyme=rhyme)
            db.session.add(new_rhyme)
    db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_word = request.form['word']
        rhymes = scrape_rhymes(search_word)
        save_to_db(search_word, rhymes)
    
    word = request.args.get('word')
    rhymes = Rhyme.query.filter_by(word=word).all() if word else []
    return render_template('index.html', word=word, rhymes=rhymes)

if __name__ == '__main__':
    app.run(debug=True)