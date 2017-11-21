import dbManager

#dbManager.createTable("hosts.db")

# dbManager.addClient("hosts.db", 123, 'abcd')
# dbManager.addClient("hosts.db", 4040, 'token2')
# dbManager.addClient("hosts.db", 420, 'token3')

print(dbManager.getValue("hosts.db", 123))