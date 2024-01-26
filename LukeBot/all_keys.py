# Contains hidden keys values for use in other modules

with open('keys/filekey.key', 'r') as keyfile:
    DATABASE_KEY = keyfile.read()
    
with open('keys/tenor.txt', 'r') as tenorfile:
    TENOR_API_KEY = tenorfile.read()