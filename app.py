from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:hsw999810@localhost:5432/lego'
app.config['SECRET_KEY'] = "random string"


db = SQLAlchemy(app)

class colors(db.Model):
    __tablename__ = "colors"
    id = db.Column(db.Integer, primary_key = True, unique = True, nullable = False)
    name = db.Column(db.VARCHAR(50))
    rgb = db.Column(db.VARCHAR(10))
    is_trans = db.Column(db.Boolean)

    def __init__(self, id, name, rgb, is_trans):
        self.id = id
        self.name = name
        self.rgb = rgb
        self.is_trans = is_trans

class part_categories(db.Model):
    __tablename__ = "part_categories"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.VARCHAR(200))

    def __init__(self, id, name):
        self.id = id
        self.name = name

class parts(db.Model):
    __tablename__ = "parts"
    parts_num = db.Column(db.VARCHAR(50), primary_key = True)
    name = db.Column(db.VARCHAR(500))
    part_cat_id = db.Column(db.Integer, db.ForeignKey('part_categories.id'), nullable = False)

    def __init__(self, parts_num, name, part_cat_id):
        self.parts_num = parts_num
        self.name = name
        self.part_cat_id = part_cat_id

class themes(db.Model):
    __tablename__ = "themes"
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.VARCHAR(200))
    parent_id = db.Column(db.Integer)

    def __init__(self, id, name, parent_id):
        self.id = id
        self.name = name
        self.parent_id = parent_id

class sets(db.Model):
    __tablename__ = "sets"
    set_num = db.Column(db.VARCHAR(50), primary_key = True)
    name = db.Column(db.VARCHAR(200))
    year = db.Column(db.VARCHAR(10))
    theme_id = db.Column(db.Integer, db.ForeignKey("themes.id"))
    num_parts = db.Column(db.Integer)

    def __init__(self, set_num, name, year, theme_id, num_parts):
        self.set_num = set_num
        self.name = name
        self.year = year
        self.theme_id = theme_id
        self.num_parts = num_parts

class inventories(db.Model):
    __tablename__ = "inventories"
    id = db.Column(db.Integer, primary_key = True)
    verion = db.Column(db.Integer)
    set_num = db.Column(db.VARCHAR(50), db.ForeignKey("sets.set_num"))

    def __init__(self, id, verion, set_num):
        self.id = id
        self.verion = verion
        self.set_num = set_num

class inventory_sets(db.Model):
    __tablename__ = "inventory_sets"
    #__table_args__ = (
        #PrimaryKeyConstraint('inventory_id', 'set_num'),
    #)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventories.id"), primary_key = True)
    set_num = db.Column(db.VARCHAR(50), db.ForeignKey("sets.set_num"), primary_key = True)
    quantity = db.Column(db.Integer)

    def __init__(self, inventory_id, set_num, quantity):
        self.inventory_id = inventory_id
        self.set_num = set_num
        self.quantity = quantity

class inventory_parts(db.Model):
    __tablename__ = "inventory_parts"
    #__table_args__ = (
        #PrimaryKeyConstraint('inventory_id', 'part_num'),
    #)
    inventory_id = db.Column(db.Integer, db.ForeignKey("inventories.id"), primary_key = True)
    part_num = db.Column(db.VARCHAR(50), primary_key = True)
    color_id = db.Column(db.Integer, db.ForeignKey("colors.id"))
    quantity = db.Column(db.Integer)
    is_spare = db.Column(db.Boolean)

    def __init__(self, inventory_id, part_num, color_id, quantity, is_spare):
        self.inventory_id = inventory_id
        self.part_num = part_num
        self.color_id = color_id
        self.quantity = quantity
        self.is_spare = is_spare




@app.route('/')
def index():
   return render_template('index.html')

@app.route('/show_all_color')
def show_all_color():
   return render_template('show_all_color.html', colors = colors.query.all())

@app.route('/show_all_part_categories')
def show_all_part_categories():
   return render_template('show_all_part_categories.html', part_categories = part_categories.query.all())

@app.route('/show_all_themes')
def show_all_themes():
   return render_template('show_all_themes.html', themes = themes.query.all())

@app.route('/show_all_parts')
def show_all_parts():
   return render_template('show_all_parts.html', parts = parts.query.all())

@app.route('/show_all_sets')
def show_all_sets():
   return render_template('show_all_sets.html', sets = sets.query.all())

@app.route('/show_all_inventories')
def show_all_inventories():
   return render_template('show_all_inventories.html', inventories = inventories.query.all())

@app.route('/show_all_inventory_sets')
def show_all_inventory_sets():
   return render_template('show_all_inventory_sets.html', inventory_sets = inventory_sets.query.all())

@app.route('/show_all_inventory_parts')
def show_all_inventory_parts():
   return render_template('show_all_inventory_parts.html', inventory_parts = inventory_parts.query.order_by(inventory_parts.inventory_id, inventory_parts.part_num).limit(1000).all())



@app.route('/new_color/<operation>', methods = ['GET', 'POST'])
def new_color(operation):
   if request.method == 'POST' and operation == 'add':
      if not request.form['id'] or not request.form['name'] or not request.form['rgb'] or not request.form['is_trans']:
         flash('Please enter all the fields', 'error')
      elif colors.query.filter_by(id = request.form['id']).first():
         flash('This color id already exists.')
      else:
         color = colors(request.form['id'], request.form['name'],
            request.form['rgb'], eval(request.form['is_trans']))
         
         db.session.add(color)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_color'))

   elif request.method == 'POST' and operation == 'update':
      if not request.form['id']:
         flash('Please enter color id', 'error')
      elif not colors.query.filter_by(id = request.form['id']).first():
         flash('This color id does not exists.')
      else:
         colors.query.filter(colors.id == request.form['id']).update({'name': request.form['name'], 'rgb': request.form['rgb'], 'is_trans': eval(request.form['is_trans'])})
         
         db.session.commit()

         flash('Record was successfully updated')
         return redirect(url_for('show_all_color'))

   elif request.method == 'POST' and operation == 'delete':
      if not request.form['id'] and not request.form['name'] and not request.form['rgb'] and not request.form['is_trans']:
         flash('Please enter at least one field to delete record.', 'error')
      else:
         result = colors.query
         if request.form['id'] and result.filter(colors.id == request.form['id']):
            result = result.filter(colors.id == request.form['id'])
         if request.form['name'] and result.filter(colors.name == request.form['name']):
            result = result.filter(colors.name == request.form['name'])
         if request.form['rgb'] and result.filter(colors.rgb == request.form['rgb']):
            result = result.filter(colors.rgb == request.form['rgb'])
         if request.form['is_trans'] and result.filter(colors.is_trans == eval(request.form['is_trans'])):
            result = result.filter(colors.is_trans == eval(request.form['is_trans']))
         
         if not result.all():
            flash('Record does not exists')
         else:
            result = result.all()
            for r in result:
               db.session.delete(r)
            db.session.commit()

            flash('Record was successfully deleted')
            return redirect(url_for('show_all_color'))
   elif request.method == 'POST' and operation == 'select':
      if not request.form['id'] and not request.form['name'] and not request.form['rgb'] and not request.form['is_trans']:
         flash('Please enter at least one field to select record.', 'error')
      else:
         result = colors.query
         if request.form['id'] and result.filter(colors.id == request.form['id']):
            result = result.filter(colors.id == request.form['id'])
         if request.form['name'] and result.filter(colors.name == request.form['name']):
            result = result.filter(colors.name == request.form['name'])
         if request.form['rgb'] and result.filter(colors.rgb == request.form['rgb']):
            result = result.filter(colors.rgb == request.form['rgb'])
         if request.form['is_trans'] and result.filter(colors.is_trans == eval(request.form['is_trans'])):
            result = result.filter(colors.is_trans == eval(request.form['is_trans']))

         if not result.all():
            flash('Record does not exists')
         else:
            result = result.all()
            return render_template('show_all_color.html', colors = result)

   return render_template('new_color.html')

@app.route('/new_part_categories/<operation>', methods = ['GET', 'POST'])
def new_part_categories(operation):
   if request.method == 'POST' and operation == 'add':
      if not request.form['id'] or not request.form['name']:
         flash('Please enter all the fields', 'error')
      elif part_categories.query.filter_by(id = request.form['id']).first():
         flash('This part category id already exists.')
      else:
         part_categorie = part_categories(request.form['id'], request.form['name'])
         
         db.session.add(part_categorie)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_part_categories'))

   if request.method == 'POST' and operation == 'update':
      if not request.form['id']:
         flash('Please enter part category id', 'error')
      elif not part_categories.query.filter_by(id = request.form['id']).first():
         flash('This part category id does not exists.')
      else:
         part_categories.query.filter(part_categories.id == request.form['id']).update({'name': request.form['name']})
         
         db.session.commit()

         flash('Record was successfully updated')
         return redirect(url_for('show_all_part_categories'))

   elif request.method == 'POST' and operation == 'delete':
      if not request.form['id'] and not request.form['name']:
         flash('Please enter at least one field to delete record.', 'error')
      else:
         result = part_categories.query
         if request.form['id'] and result.filter(part_categories.id == request.form['id']):
            result = result.filter(part_categories.id == request.form['id'])
         if request.form['name'] and result.filter(part_categories.name == request.form['name']):
            result = result.filter(part_categories.name == request.form['name'])
         if not result.all():
            flash('Record does not exists')
         else:
            result = result.all()
            for r in result:
               db.session.delete(r)
            db.session.commit()

            flash('Record was successfully deleted')
            return redirect(url_for('show_all_part_categories'))
   elif request.method == 'POST' and operation == 'select':
      if not request.form['id'] and not request.form['name'] and not request.form['rgb'] and not request.form['is_trans']:
         flash('Please enter at least one field to select record.', 'error')
      else:
         result = part_categories.query
         if request.form['id'] and result.filter(part_categories.id == request.form['id']):
            result = result.filter(part_categories.id == request.form['id'])
         if request.form['name'] and result.filter(part_categories.name == request.form['name']):
            result = result.filter(part_categories.name == request.form['name'])

         if not result.all():
            flash('Record does not exists')
         else:
            result = result.all()
            return render_template('show_all_part_categories.html', part_categories = result)
   return render_template('new_part_categories.html')

@app.route('/new_parts/<operation>', methods = ['GET', 'POST'])
def new_parts(operation):
   if request.method == 'POST':
      if not request.form['parts_num'] or not request.form['name'] or not request.form['part_cat_id']:
         flash('Please enter all the fields', 'error')
      elif parts.query.filter_by(parts_num = request.form['parts_num']).first():
         flash('This part number already exists.')
      else:
         part = parts(request.form['parts_num'], request.form['name'], request.form['part_cat_id'])
         
         db.session.add(part)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_parts'))
   return render_template('new_parts.html')

@app.route('/new_themes/<operation>', methods = ['GET', 'POST'])
def new_themes(operation):
   if request.method == 'POST':
      if not request.form['id'] or not request.form['name'] or not request.form['parent_id']:
         flash('Please enter all the fields', 'error')
      elif themes.query.filter_by(id = request.form['id']).first():
         flash('This theme id already exists.')
      else:
         theme = themes(request.form['id'], request.form['name'], request.form['parent_id'])
         
         db.session.add(theme)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_themes'))
   return render_template('new_themes.html')

@app.route('/new_sets/<operation>', methods = ['GET', 'POST'])
def new_sets(operation):
   if request.method == 'POST':
      if not request.form['set_num'] or not request.form['name'] or not request.form['year'] or not request.form['theme_id'] or not request.form['num_parts']:
         flash('Please enter all the fields', 'error')
      elif sets.query.filter_by(set_num = request.form['set_num']).first():
         flash('This set number already exists.')
      else:
         s = sets(request.form['set_num'], request.form['name'], request.form['year'], request.form['theme_id'], request.form['num_parts'])
         
         db.session.add(s)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_sets'))
   return render_template('new_sets.html')

@app.route('/new_inventories/<operation>', methods = ['GET', 'POST'])
def new_inventories(operation):
   if request.method == 'POST':
      if not request.form['id'] or not request.form['verion'] or not request.form['set_num']:
         flash('Please enter all the fields', 'error')
      elif inventories.query.filter_by(id = request.form['id']).first():
         flash('This inventory id already exists.')
      else:
         inventorie = inventories(request.form['id'], request.form['verion'], request.form['set_num'])
         
         db.session.add(inventorie)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_inventories'))
   return render_template('new_inventories.html')

@app.route('/new_inventory_sets/<operation>', methods = ['GET', 'POST'])
def new_inventory_sets(operation):
   if request.method == 'POST':
      if not request.form['inventory_id'] or not request.form['set_num'] or not request.form['quantity']:
         flash('Please enter all the fields', 'error')
      elif inventory_sets.query.filter_by(inventory_id = request.form['inventory_id']).first() and inventory_sets.query.filter_by(set_num = request.form['set_num']).first():
         flash('This inventory set already exists.')
      else:
         i_set = inventory_sets(request.form['inventory_id'], request.form['set_num'], request.form['quantity'])
         
         db.session.add(i_set)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_inventory_sets'))
   return render_template('new_inventory_sets.html')

@app.route('/new_inventory_parts/<operation>', methods = ['GET', 'POST'])
def new_inventory_parts(operation):
   if request.method == 'POST':
      if not request.form['inventory_id'] or not request.form['part_num'] or not request.form['color_id'] or not request.form['quantity'] or not request.form['is_spare']:
         flash('Please enter all the fields', 'error')
      elif inventory_parts.query.filter_by(inventory_id = request.form['inventory_id']).first() and inventory_parts.query.filter_by(part_num = request.form['part_num']).first():
         flash('This inventory part already exists.')
      else:
         i_part = inventory_parts(request.form['inventory_id'], request.form['part_num'], request.form['color_id'], request.form['quantity'], eval(request.form['is_spare']))
         
         db.session.add(i_part)
         db.session.commit()
         
         flash('Record was successfully added')
         return redirect(url_for('show_all_inventory_parts'))
   return render_template('new_inventory_parts.html')

if __name__ == '__main__':
    db.create_all()
    app.run(debug = True, port = 8080)