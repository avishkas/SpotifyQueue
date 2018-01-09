import sqlite3


#create table
def createTable(name):
	if(not isinstance(name, str)):
		raise TypeError("Database Name not of type string")

	conn = sqlite3.connect(name)
	conn.execute("CREATE TABLE IF NOT EXISTS hosts (accessToken text, code text, userID text, playlistID text)")
	conn.commit()
	conn.close()


def addClient(dbName, code, accessToken, userID, playlistID):
	if(not isinstance(dbName, str)):
		raise TypeError("Database Name not of type string")


	conn = sqlite3.connect(dbName) #establish connection

	#check if code already exists
	if(codeIsDuplicate(dbName, code)):
		raise NameError("Duplicate Code Found")

	#insert data into databse
	conn.execute("INSERT INTO hosts VALUES(?, ?, ?, ?)", (accessToken, code, userID, playlistID))

	#commit and close
	conn.commit()
	conn.close()


def getData(dbName, code):
	if(not isinstance(dbName, str)):
		raise TypeError("Database Name not of type string")

	conn = sqlite3.connect(dbName)

	try:
		cursor = conn.execute("SELECT * FROM hosts WHERE code = ?", (code, ))
	except:
		return None
	
	data = cursor.fetchone()	
	conn.close()

	return data


def codeIsDuplicate(dbName, code):
	if(not isinstance(dbName, str)):
		return None

	conn = sqlite3.connect(dbName)

	status = conn.execute("SELECT EXISTS(SELECT 1 FROM hosts WHERE code = ? LIMIT 1)", (code,)) #return 0 or 1 depending on if code exists
	
	if status.fetchone()[0] == 0:
		conn.close()
		return False
	else:
		conn.close()
		return True


def deleteTable(dbName):
	if(not isinstance(dbName, str)):
		return None

	conn = sqlite3.connect(dbName)

	conn.execute("DROP TABLE hosts")

	conn.commit()
	conn.close()