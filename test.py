import sys, json, time, sqlite3
import Words

start_time = time.time()

start = 1
wordPattern = "*sa***"

data = { 'words': [], 'meanings': [] }

Words.Words_SQLite3.wordnet_db = 'wordnet-31.db'

try:
    wordFinder = Words.Words_SQLite3(wordPattern, start, 25)    
    wordFinder.run()
except sqlite3.Error as e:
    print("An error occurred:", e.args[0])
    sys.exit()
except Exception as inst:
    print(inst)
    sys.exit()


data['total'] = wordFinder.total;
data['count'] = wordFinder.count;

if wordFinder.count > 0: # Can be -1 one if there's an error
    for word in wordFinder:        
        data['words'].append(word)
        data['meanings'].append(wordFinder.getMeanings())

data['time'] = str(time.time() - start_time);
data['status'] = 'success'
data['message'] = ''
data['start'] = wordFinder.row_start

strJSON = json.dumps(data)    

print(strJSON);
