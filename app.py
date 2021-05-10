from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import re
import string
from pyjarowinkler import distance
from datetime import datetime

def normalize_text(text):
    text = text.upper()
    text = re.sub('[%s]'%re.escape(string.punctuation),'',text)
    return text

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content1 = db.Column(db.String(200), nullable=False)
    content2 = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Float, default=0.0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/')
def main():
    return render_template('index.html')


@app.route('/posts', methods = ['GET', 'POST'])
def posts():
    if request.method == 'POST':
        string_1 = request.form['string1']
        string_2 = request.form['string2']
        string_3 = normalize_text(string_1)
        string_4 = normalize_text(string_2)
        jaro_winkler_score = distance.get_jaro_distance(string_3, string_4, winkler=True, scaling=0.1)
        score = format(jaro_winkler_score,".2f")
        new_post = Todo(content1=string_3, content2=string_4, score = score)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/posts')
        
    else:
        all_strings = Todo.query.all()
        return render_template('index.html', names=all_strings)
    
@app.route('/posts/delete/<int:id>')
def delete(id):
    name = Todo.query.get_or_404(id)
    db.session.delete(name)
    db.session.commit()
    return redirect('/posts')


if __name__ == "__main__":
    app.run(debug=True)