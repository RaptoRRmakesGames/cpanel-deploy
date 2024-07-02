import mysql.connector, json

def connect():
    
    with open("db_creds.json") as f:
        db_cr = json.load(f)

    db = mysql.connector.connect(
        host=db_cr["host"],
        user=db_cr["username"],
        passwd=db_cr["password"],
        database=db_cr["dbname"],
        port=db_cr["port"],
    )

    return db, db.cursor()

def create_database():
    
    db,c = connect()
    
    with open('create_db.sql') as f:
        query = f.read()
        
    print(query.split('\n'))
        
    c.execute(query, multi=True)

    db.commit()

if __name__ == '__main__':
    
    db,c = connect()
    
    print('Connected to db')
    
    create_database()
    
    print('Created database')
    