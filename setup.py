import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="navgurukul",
)

cur = mydb.cursor()
cur.execute("CREATE DATABASE lms;")

cur.execute("USE lms")

cur.execute('''CREATE TABLE books ( 
    id INT(11) NOT NULL AUTO_INCREMENT , 
    title VARCHAR(255) NOT NULL , 
    author VARCHAR(255) NOT NULL , 
    average_rating FLOAT NULL , 
    isbn VARCHAR(10) NOT NULL , 
    isbn13 VARCHAR(13) NOT NULL , 
    language_code VARCHAR(13) NOT NULL , 
    num_pages INT(5) NOT NULL , 
    ratings_count INT(11) NOT NULL , 
    text_reviews_count INT(11) NOT NULL , 
    publication_date DATE NOT NULL , 
    publisher VARCHAR(255) NOT NULL , 
    total_quantity INT(11) NOT NULL , 
    available_quantity INT(11) NOT NULL , 
    rented_count INT(11) NOT NULL DEFAULT 0, 
    PRIMARY KEY (id));
            ''')

cur.execute('''CREATE TABLE members ( 
    id INT(11) NOT NULL AUTO_INCREMENT , 
    name VARCHAR(100) NOT NULL , 
    email VARCHAR(100) NOT NULL ,
    registered_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , 
    outstanding_debt FLOAT NOT NULL DEFAULT 0, 
    amount_spent FLOAT NOT NULL DEFAULT 0,
    issued_books INT(11) DEFAULT 0,
    PRIMARY KEY (id));
''')

cur.execute('''CREATE TABLE transactions ( 
    id INT(11) NOT NULL AUTO_INCREMENT , 
    book_id INT(11) NOT NULL , 
    member_id INT(11) NOT NULL , 
    member_name varchar(255) NOT NULL,
    per_day_fee FLOAT NOT NULL , 
    borrowed_on TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP , 
    returned_on TIMESTAMP NULL , 
    total_charge FLOAT NULL , 
    amount_paid FLOAT NULL ,
    PRIMARY KEY (id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (member_id) REFERENCES members(id)) ENGINE = InnoDB;''')

mydb.commit()
mydb.close()


