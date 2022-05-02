from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hsw999810@localhost:5432/lego'
app.config['SECRET_KEY'] = "random string"


db = SQLAlchemy(app)

class colors(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    name = db.Column(db.VARCHAR(50), nullable = False)
    rgb = db.Column(db.VARCHAR(10), nullable = False)
    is_trans = db.Column(db.Boolean, nullable = False)

    def __init__(self, id, name, rgb, is_trans):
        self.id = id
        self.name = name
        self.rgb = rgb
        self.is_trans = is_trans


@app.route('/')
def show_all():
   return render_template('show_all.html', colors = colors.query.all() )


@app.route('/new', methods = ['GET', 'POST'])
def new():
   if request.method == 'POST':
      if not request.form['id'] or not request.form['name'] or not request.form['rgb'] or not request.form['is_trans']:
         flash('Please enter all the fields', 'error')
      else:
         color = colors(request.form['id'], request.form['name'],
            request.form['rgb'], eval(request.form['is_trans']))
         
         db.session.add(color)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all'))
   return render_template('new.html')


if __name__ == '__main__':
    db.create_all()
    app.run(debug = True, port = 8080)