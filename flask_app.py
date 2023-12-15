from flask import Flask, render_template, flash, redirect, url_for,request
from flask_mysqldb import MySQL
from wtforms import Form,validators,StringField,FloatField,IntegerField,DateField,SelectField
from datetime import datetime
import requests
import MySQLdb

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'navgurukul'
app.config['MYSQL_DB'] = 'lms'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/members')
def members():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM members")
    members = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('members.html', members=members)
    else:
        flash('No Members Found','danger')
        return render_template('members.html')
    
class AddMember(Form):
    id=IntegerField('Id',[validators.NumberRange(min=1)])
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    form = AddMember(request.form)
    if request.method == 'POST' and form.validate():
        id=form.id.data
        name = form.name.data
        email = form.email.data
        cur = mysql.connection.cursor()
        try:
            cur.execute(
            "INSERT INTO members (id,name, email) VALUES (%s,%s, %s)", (id,name, email))
            mysql.connection.commit()
        except:
            flash('Unable to add member','danger')
            return redirect(url_for('members'))
        finally:
            cur.close()
        flash("New Member Added", "success")
        return redirect(url_for('members'))
    return render_template('add_member.html', form=form)


@app.route('/delete_member/<string:id>',methods=['GET','POST'])
def delete_member(id):
    cur=mysql.connection.cursor()
    try:
        cur.execute("Delete from members where id=%s",[id])
        mysql.connection.commit()
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print(e)
        flash("Member exists in transactions.", "danger")
        return redirect(url_for('members'))
    finally:
        cur.close()        
    flash('Member removed.','success')
    return redirect(url_for('members'))

class SearchMember(Form):
    id=StringField('Member Id')
    name=StringField('Member Name')

@app.route('/search_member',methods=['GET','POST'])
def search_member():
    form=SearchMember(request.form)
    if request.method=='POST' and form.validate():
        cur=mysql.connection.cursor()
        result=cur.execute('Select * from members where id=%s or name=%s',[form.id.data,form.name.data])
        members=cur.fetchall()
        if result<1:
            flash('No Member found.','danger')
            return redirect('/search_member')
        return render_template('search_member.html',form=form,members=members)
    return render_template('search_member.html',form=form)

class EditMember(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    outstanding_debt=FloatField('Outstanding Debt')


@app.route('/edit_member/<string:id>',methods=['GET','POST'])
def edit_member(id):
    form=EditMember(request.form)
    cur=mysql.connection.cursor()
    cur.execute('SELECT * FROM members where id=%s',[id])
    member=cur.fetchone()
    if request.method=="POST" and form.validate():
        name=form.name.data
        email=form.email.data
        diff=member['outstanding_debt']-form.outstanding_debt.data
        cur.execute('UPDATE members SET name=%s,email=%s,outstanding_debt=%s,amount_spent=amount_spent+%s where id=%s',[name,email,form.outstanding_debt.data,diff,id])
        mysql.connection.commit()
        cur.close()
        flash('Member details updated!','success')
        return redirect('/members')
    return render_template('edit_member.html',form=form,member=member)

@app.route('/member_details/<string:id>')
def member_details(id):
    cur=mysql.connection.cursor()
    cur.execute("select * from members WHERE id=%s",[id])
    member=cur.fetchone()
    return render_template('member_details.html',member=member)












@app.route('/books')
def books():
    cur = mysql.connection.cursor()

    result = cur.execute(
        "SELECT id,title,author,total_quantity,available_quantity,rented_count FROM books")
    books = cur.fetchall()
    cur.close()
    if result > 0:
        return render_template('books.html', books=books)
    else:
        flash('No Books Found','danger')
        return render_template('books.html')
    
@app.route('/book/<string:id>')
def bookData(id):
    cur=mysql.connection.cursor()
    result=cur.execute(
        "SELECT * FROM books where id=%s",[id])
    book=cur.fetchone()
    cur.close()
    if result>0:
        return render_template('book_data.html',book=book)
    else:
        flash('There is no book with given ID','danger')
        return render_template('books.html')
    

class AddBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author', [validators.Length(min=2, max=255)])
    average_rating = FloatField('Average Rating',[validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField(
        'No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField(
        'No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField(
        'Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField(
        'Total No. of Books', [validators.NumberRange(min=1)])



@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    form = AddBook(request.form)
    if request.method == 'POST' and form.validate():
        cur = mysql.connection.cursor()
        result = cur.execute(
            "SELECT id FROM books WHERE id=%s", [form.id.data])
        book = cur.fetchone()
        if(book):
            flash('Book with that ID already exists','danger')
            return render_template('add_book.html', form=form)

        cur.execute("INSERT INTO books (id,title,author,average_rating,isbn,isbn13,language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", [
            form.id.data,
            form.title.data,
            form.author.data,
            form.average_rating.data,
            form.isbn.data,
            form.isbn13.data,
            form.language_code.data,
            form.num_pages.data,
            form.ratings_count.data,
            form.text_reviews_count.data,
            form.publication_date.data,
            form.publisher.data,
            form.total_quantity.data,
            form.total_quantity.data
        ])
        mysql.connection.commit()
        cur.close()
        flash("New Book Added", "success")
        return redirect(url_for('books'))
    return render_template('add_book.html', form=form)

class ImportBooks(Form):
    total_books=IntegerField('Total Books',[validators.NumberRange(min=1)])
    count_per_book=IntegerField('Quantity Per Book',[validators.NumberRange(min=1)])
    title=StringField('Title',[validators.optional(),validators.Length(min=2)])
    author=StringField('Author',[validators.optional(),validators.Length(min=2)])
    isbn=StringField('ISBN',[validators.optional(),validators.Length(min=10,max=10)])
    publisher=StringField('publisher',[validators.optional(),validators.Length(min=2)])

@app.route('/import_books',methods=['GET','POST'])
def import_book():
    form=ImportBooks(request.form)
    if request.method=='POST' and form.validate():
        api_link='https://frappe.io/api/method/frappe-library'
        param={'page':1}
        if form.title.data:
            param['title']=form.title.data
        if form.author.data:
            param['authors']=form.author.data
        if form.isbn.data:
            param['isbn']=form.isbn.data
        if form.publisher.data:
            param['publisher']=form.publisher.data
        
        cur=mysql.connection.cursor()
        books_imported=0
        repeated_id=0
        while form.total_books.data != books_imported:
            data=requests.get(api_link,params=param).json()
            books=data['message']
            if not books:
               break
            for book in books:
                cur.execute('SELECT id from books where id=%s',[book['bookID']]) 
                got_book=cur.fetchone()
                if got_book == None:
                    converted_date = datetime.strptime(book['publication_date'], '%m/%d/%Y').strftime('%Y-%m-%d')
                    cur.execute('''INSERT INTO books (id,title,author,average_rating,isbn,isbn13,
                                language_code,num_pages,ratings_count,text_reviews_count,publication_date,publisher,total_quantity,available_quantity) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',[book['bookID'],book['title'],book['authors'],book['average_rating'],book['isbn'],book['isbn13'],book['language_code'],book['  num_pages'],book['ratings_count'],book['text_reviews_count'],converted_date,book['publisher'],form.count_per_book.data,form.count_per_book.data])
                    books_imported+=1
                    if books_imported==form.total_books.data:
                        break
                else:
                    repeated_id+=1
            param['page']+=1
        mysql.connection.commit()
        cur.close()
        if repeated_id:
            flash(f'{repeated_id} book(s) already exists with same ID, {books_imported} book(s) imported.','danger')
            return redirect('/books')
        if books_imported==0:
            flash('No book found with matching parameter.','danger')
            return redirect('/books')
        flash(f'{books_imported} books successfully imported!','success')
        return redirect('/books')
    return render_template('import_books.html',form=form)


class EditBook(Form):
    id = StringField('Book ID', [validators.Length(min=1, max=11)])
    title = StringField('Title', [validators.Length(min=2, max=255)])
    author = StringField('Author(s)', [validators.Length(min=2, max=255)])
    average_rating = FloatField('Average Rating',[validators.NumberRange(min=0, max=5)])
    isbn = StringField('ISBN', [validators.Length(min=10, max=10)])
    isbn13 = StringField('ISBN13', [validators.Length(min=13, max=13)])
    language_code = StringField('Language', [validators.Length(min=1)])
    num_pages = IntegerField('No. of Pages', [validators.NumberRange(min=1)])
    ratings_count = IntegerField('No. of Ratings', [validators.NumberRange(min=0)])
    text_reviews_count = IntegerField('No. of Text Reviews', [validators.NumberRange(min=0)])
    publication_date = DateField('Publication Date', [validators.InputRequired()])
    publisher = StringField('Publisher', [validators.Length(min=2, max=255)])
    total_quantity = IntegerField('Total No. of Books', [validators.NumberRange(min=1)])


@app.route('/edit_book/<string:id>',methods=['GET','POST'])
def edit_book(id):
    form=EditBook(request.form)
    cur = mysql.connection.cursor()
    cur.execute('SELECT * from books where id=%s',[id])
    book=cur.fetchone()
    if request.method=='POST' and form.validate():
        if form.id.data!=id:
            result=cur.execute('SELECT id from books where id=%s',[form.id.data])
            if result>0:
                flash("Book with given ID already exists!",'danger')
                return render_template('edit_book.html',form=form,book=book)
            
        available_quantity=book['available_quantity']+(form.total_quantity.data-book['total_quantity'])

        cur.execute("UPDATE books SET id=%s,title=%s,author=%s,average_rating=%s,isbn=%s,isbn13=%s,language_code=%s,num_pages=%s,ratings_count=%s,text_reviews_count=%s,publication_date=%s,publisher=%s,total_quantity=%s,available_quantity=%s where id=%s", [form.id.data,form.title.data,form.author.data,form.average_rating.data,form.isbn.data,form.isbn13.data,form.language_code.data,form.num_pages.data,form.ratings_count.data,form.text_reviews_count.data,form.publication_date.data,form.publisher.data,form.total_quantity.data,available_quantity,id])
        mysql.connection.commit()
        cur.close()
        flash("Book Data Edited", "success")
        return redirect(url_for('books'))
    return render_template('edit_book.html',form=form,book=book)


@app.route('/delete_book/<string:id>')
def delete_book(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM books WHERE id=%s", [id])
        mysql.connection.commit()
    except:
        flash('Unsuccessful Atempt! Books is issued.', "danger")
        return redirect(url_for('books'))
    finally:
        cur.close()
    flash("Book Deleted", "success")
    return redirect(url_for('books'))

class Search(Form):
    id=StringField('BookID',[validators.optional(),validators.Length(min=1)])
    title=StringField('Book Title',[validators.optional(),validators.Length(min=1)])
    author=StringField('Author',[validators.optional(),validators.Length(min=1)])

@app.route('/search', methods=['GET','POST'])
def search():
    form=Search(request.form)
    if request.method=='POST' and form.validate():
        cur = mysql.connection.cursor()
        id=form.id.data
        if form.title.data=='':
            form.title.data='None'
        if form.author.data=='':
            form.author.data='None'
        title = '%'+form.title.data+'%'
        author = '%'+form.author.data+'%'
        result = cur.execute("SELECT * FROM books WHERE id=%s OR title LIKE %s OR author LIKE %s", [id,title, author])
        books = cur.fetchall()
        cur.close()
        if result<1:
            flash('No book found','danger')
            return redirect('/search')
        flash(f'{result} Book(s) Found.','success')
        return render_template('search.html',form=form,books=books)
    return render_template('search.html',form=form)

class Issue(Form):
    member_id=SelectField('Member Id',choices=[])
    rent=IntegerField('Rent Per Day')

@app.route('/issue/<string:id>',methods=['GET','POST'])
def issue(id):
    form=Issue(request.form)
    cur=mysql.connection.cursor()
    cur.execute('SELECT id,name FROM members')
    mbs=cur.fetchall()
    member_list=[]
    for mb in mbs:
        member_list.append(mb['id'])

    form.member_id.choices=member_list
    if request.method=='POST' and form.validate():
        result=cur.execute('select available_quantity from books where id=%s',[id])
        get_book=cur.fetchone()

        if get_book['available_quantity']<1:
            flash('Book is not available at this moment.','danger')
            return redirect('/issue_book')
        
        get_member=cur.execute('select * from members where id=%s',[form.member_id.data])
        member=cur.fetchone()
        if get_member<1:
            flash('First add the member.','danger')
            return redirect('/issue_book')
        
        if member['outstanding_debt']>500:
            flash('Outstanding debt is more than 500/- ','danger')
            return redirect('/members')
        
        cur.execute('''INSERT INTO transactions 
                    (book_id,member_id,member_name,per_day_fee) 
                    values(%s,%s,%s,%s)''',
                    [id,form.member_id.data,member['name'],form.rent.data])
        
        cur.execute('''UPDATE books 
                    SET available_quantity=available_quantity-1,
                    rented_count=rented_count+1 where id=%s''',[id])
        
        cur.execute('''UPDATE members 
                    SET issued_books=issued_books+1 
                    where id=%s''',[form.member_id.data])
        mysql.connection.commit()
        cur.close()
        flash('book issued successfully!','success')
        return redirect('/transactions')
    return render_template('issue_book.html',id=id,form=form)














@app.route('/transactions')
def transactions():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM transactions")
    transactions = cur.fetchall()
    cur.close()
    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"
    if result > 0:
        return render_template('transactions.html', transactions=transactions)
    else:
        flash('No Transactions Found','danger')
        return render_template('transactions.html')
    
class IssueBook(Form):
    book_id=SelectField('Book Id',choices=[])
    member_id=SelectField('Member Id',choices=[])
    rent=IntegerField('Rent Per Day')

@app.route('/issue_book',methods=['GET','POST'])
def issue_book():
    form=IssueBook(request.form)
    cur=mysql.connection.cursor()
    cur.execute('SELECT id,title FROM books')
    bks=cur.fetchall()
    book_list=[]
    for bk in bks:
        b=(bk['id'],bk['title'])
        book_list.append(b)

    cur.execute('SELECT id,name FROM members')
    mbs=cur.fetchall()
    member_list=[]
    for mb in mbs:
       
        member_list.append(mb['id'])

    form.book_id.choices=book_list
    form.member_id.choices=member_list
    
    if request.method=='POST' and form.validate():
        
        result=cur.execute('select available_quantity from books where id=%s',[form.book_id.data])
        get_book=cur.fetchone()

        if result<1 or get_book['available_quantity']<1:
            flash('Book is not available at this moment.','danger')
            return redirect('/issue_book')
        
        get_member=cur.execute('select * from members where id=%s',[form.member_id.data])
        member=cur.fetchone()
        if get_member<1:
            flash('First add the member.','danger')
            return redirect('/issue_book')
        
        if member['outstanding_debt']>500:
            flash('Outstanding debt is more than 500/- ','danger')
            return redirect('/members')
        name=member['name']
        cur.execute('''INSERT INTO transactions 
                    (book_id,member_id,member_name,per_day_fee) 
                    values(%s,%s,%s,%s)''',
                    [form.book_id.data,form.member_id.data,name,form.rent.data])
        
        cur.execute('''UPDATE books 
                    SET available_quantity=available_quantity-1,
                    rented_count=rented_count+1 where id=%s''',[form.book_id.data])
        
        cur.execute('''UPDATE members 
                    SET issued_books=issued_books+1 
                    where id=%s''',[form.member_id.data])
        mysql.connection.commit()
        cur.close()
        flash('book issued successfully!','success')
        return redirect('/transactions')
    return render_template('issue_book.html',form=form)


class Return(Form):
    amount=IntegerField('Amount Paid')

@app.route('/return_book/<int:id>',methods=['GET','POST'])
def return_book(id):
    form=Return(request.form)
    cur=mysql.connection.cursor()
    cur.execute('Select * from transactions where id=%s',[id])
    transaction=cur.fetchone()
    issue_date=transaction['borrowed_on']
    return_date=datetime.now()
    days=(return_date-issue_date).days
    total_amount=days*transaction['per_day_fee']
    cur.execute('select * from members where id=%s',[transaction['member_id']])
    member=cur.fetchone()
    outstanding_debt=member['outstanding_debt']
    if request.method=='POST' and form.validate():
        debt=total_amount-form.amount.data
        outstanding=outstanding_debt+debt
        if outstanding>500:
            flash('Can not return book! Outstanding dept is more than 500.','danger')
            return redirect('/transactions')
        if outstanding_debt+total_amount<form.amount.data:
            flash('Can not return book! Amount paid is more than outstanding debt.','danger')
            return redirect('/transactions')
        cur.execute('UPDATE members SET outstanding_debt=outstanding_debt+%s,amount_spent=amount_spent+%s,issued_books=issued_books-1 WHERE id=%s',[debt,form.amount.data,transaction['member_id']])
        cur.execute('UPDATE books SET rented_count=rented_count+1, available_quantity=available_quantity+1 where id=%s',[transaction['book_id']])
        cur.execute('UPDATE transactions SET returned_on=%s, total_charge=%s,amount_paid=%s where id=%s',[return_date,total_amount,form.amount.data,id])
        mysql.connection.commit()
        cur.close()
        flash('Book returned.','success')
        return redirect('/transactions')
    return render_template('return_book.html',form=form,transaction=transaction,total=total_amount,days=days,returned_on=return_date,outstanding_debt=outstanding_debt)

class SearchTransaction(Form):
    book_id=StringField('Book Id')
    member_id=StringField('Member Id')



@app.route('/search_transaction',methods=['GET','POST'])
def search_transaction():
    form=SearchTransaction(request.form)
    if request.method=='POST' and form.validate():
        cur=mysql.connection.cursor()
        result=cur.execute('select * from transactions where book_id=%s or member_id=%s',[form.book_id.data,form.member_id.data])
        transactions=cur.fetchall()
        cur.close()
        for transaction in transactions:
            for key, value in transaction.items():
                if value is None:
                    transaction[key] = "-"
        if result>0:
            flash('Transaction Found!','success')
            return render_template('search_transaction.html',form=form,transactions=transactions)
        flash('Did not found Transaction!','danger')
        return render_template('search_transaction.html',form=form)
    return render_template('search_transaction.html',form=form)


@app.route('/delete_transaction/<string:id>',methods=['GET','POST'])
def delete_transaction(id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM transactions WHERE id=%s", [id])
        mysql.connection.commit()
    except:
        flash("Unsuccessful Attempt!", "danger")
        return redirect(url_for('/transactions'))
    finally:
        cur.close()
    flash("Attempt Successful:)", "success")
    return redirect(url_for('transactions'))

@app.route('/reports')
def reports():
    cur=mysql.connection.cursor()
    cur.execute('Select * from books order by rented_count desc LIMIT 5')
    top_books=cur.fetchall()
    cur.execute('SELECT * FROM members ORDER BY amount_spent DESC LIMIT 5')
    top_members=cur.fetchall()
    if not top_books and not top_members:
        flash('There is no transactions yet!','danger')
        return render_template('reports.html')
    return render_template('reports.html',top_books=top_books,top_members=top_members)

@app.route('/sort/<string:param>')
def sort1(param):
    cur=mysql.connection.cursor()
    cur.execute(f"SELECT * FROM transactions order by {param}")
    transactions=cur.fetchall()
    for transaction in transactions:
        for key, value in transaction.items():
            if value is None:
                transaction[key] = "-"
    return render_template('transactions.html',transactions=transactions)



if __name__ == '__main__':
    app.secret_key = "secret"
    app.run(debug=True)