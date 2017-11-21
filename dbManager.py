import sqlite3


#create table
def createTable(name):
	if(not isinstance(name, str)):
		return None

	conn = sqlite3.connect(name)
	conn.execute("CREATE TABLE IF NOT EXISTS hosts (accessToken text, code real)")
	conn.commit()
	conn.close()


def addClient(dbName, code, accessToken):
	if(not isinstance(dbName, str)):
		return None


	conn = sqlite3.connect(dbName) #establish connection

	#check if client already exists in 

	#insert data into databse
	conn.execute("INSERT INTO hosts VALUES(?, ?)", (accessToken, code))

	#commit and close
	conn.commit()
	conn.close()

def getValue(dbName, code):
	if(not isinstance(dbName, str)):
		return None

	conn = sqlite3.connect(dbName)

	try:
		data = conn.execute("SELECT * FROM hosts WHERE code = ?", (code, ))
	except:
		return None
	
	accessToken = data.fetchone()[0]

	for element in data.fetchall():
		print(element)
		
	conn.close()
	return accessToken

def deleteTable(dbName):
	if(not isinstance(dbName, str)):
		return None

	conn = sqlite3.connect(dbName)

	conn.execute("DROP TABLE hosts")

	conn.commit()
	conn.close()