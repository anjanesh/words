import re, sqlite3

class SQLIterator:

    """
    row_start : offset - Starting row (First row is normally indexed 0)
    row_count : limit  - Number of Rows to fetch

    count     : Total number of rows using LIMIT
    total     : Total number of rows without using LIMIT

    LIMIT row_start, row_count
    Example : LIMIT 10, 20
    """
    def __init__(self, row_start = 0, row_count = 10):
        self.rows = None
        self.rows_iterator = None

        self.row_start = row_start
        self.row_count = row_count

        self.count = -1
        self.total = -1
        self.row_end = -1 # row_end = row_start + min(row_count, count)

class SQLite3Iterator (SQLIterator):

    """
    customFilter is used when further filtering not possible (or slower) using SQL's WHERE
    But total using COUNT(*) will not return total rows
    """
    customFilter = False
    custom = { 'filter':True, 'getTotalFirst':True }

    """    
    row_start : offset - Starting row (First is 0)
    row_count : limit  - Number of Rows to fetch
    """
    def __init__(self, row_start = 0, row_count = 10):
        SQLIterator.__init__(self, row_start, row_count)        
        self.cursor = self.conn.cursor()

    def run(self):
        sql = self.getSQL()                
        self.cursor.execute("SELECT COUNT(%s) AS `Total` FROM %s WHERE %s;" % (sql['SELECT'][0], sql['FROM'], sql['WHERE']))        
        row = self.cursor.fetchone()
        self.total = row['Total']        

        query = "SELECT %s FROM %s WHERE %s ORDER BY %s" % (",".join(sql['SELECT']), sql['FROM'], sql['WHERE'], sql['ORDER BY'])
        if self.customFilter is False: query += " LIMIT %s" % sql['LIMIT']
        query += ";"

        # if self.customFilter is True: self.total = self.__getTotalbyFilter(query)

        self.cursor.execute(query)     
        self.rows = self.cursor.fetchall()
        self.rows_iterator = iter(self.rows)
        self.sql_count = len(self.rows) # cursor.rowcount will return -1 in Python3
        self.count = self.sql_count if self.customFilter is False else 0
        self.row_end = self.row_start + min(self.row_count, self.count)

    def __next__(self):

        if self.customFilter is False:            
            row = next(self.rows_iterator)
            if not row: raise StopIteration
        else:
            while True:
                row = next(self.rows_iterator)
                if not row: raise StopIteration
                if self.filter(row) is True:
                    self.count += 1
                    break
                # self.total -= 1        
        return row

    def filter(self, row):
        return True

    def __getTotalbyFilter(self, query):
        self.cursor.execute(query)
        total = 0
        while True:
            row = self.cursor.fetchone()
            if row == None: break
            if self.filter(row) is True: total += 1
        return total

    def __iter__(self):
        return self

class Words:

    """
    pattern   : Word Pattern
    row_start : Starting row (First is 1)
    row_count : Number of Rows to fetch
    """
    def __init__(self, pattern, row_start, row_count):
        self.pattern = pattern
        self.length = len(self.pattern)
        # self.row_start = row_start
        # self.row_end = -1
        # self.row_count = row_count

        self.spaces = True
        self.hyphens = True
        self.quotations = True
        self.numbers = True

        self.variable = 'f'

        self.wordid = 0

    def getPattern(self):
        return self.pattern

    def getLength(self):
        return self.length

    def getWordId(self):
        return self.wordid



class Words_SQLite3(Words, SQLite3Iterator):

    wordnet_db = None

    def __init__(self, pattern, row_start, row_count):
        
        if not Words_SQLite3.wordnet_db:
            raise Exception("Wordnet database has to be set. Example: Words.Words_SQLite3.wordnet_db = '/path/wordnet-31.db'. If you don't have it, you can download it from: https://storage.googleapis.com/anjanesh/wordnet-31.db")

        self.conn = sqlite3.connect(Words_SQLite3.wordnet_db)
        self.conn.row_factory = sqlite3.Row
        SQLite3Iterator.__init__(self, row_start - 1, row_count)
        Words.__init__(self, pattern, row_start - 1, row_count) # row_start = offset in MySQL and start at 0        

    def getSQL(self):
        sql0 = """
        SELECT w.`wordid`, w.`lemma`
        FROM `words` w
        WHERE %s
        LIMIT %d, %d ;""" % (self.getWHERE() , self.row_start , self.row_count)

        sql = {}
        sql['SELECT']   = ["w.`wordid`", "w.`lemma`"]
        sql['FROM']     = "`words` w"
        sql['WHERE']    = "%s" % self.getWHERE()
        sql['LIMIT']    = "%d, %d" % (self.row_start , self.row_count)
        sql['ORDER BY'] = "w.`lemma` ASC"

        sql1 = """
        SELECT w.lemma, sy.definition
        FROM `words` w
        LEFT JOIN `senses` se on w.wordid = se.wordid
        LEFT JOIN `synsets` sy on se.synsetid = sy.synsetid
        WHERE %s    
        GROUP BY se.sensenum
        LIMIT %d, %d
        ;""" % (self.getWHERE() , self.row_start , self.row_count)

        return sql

    def getWHERE(self):
        sql = ""

        if self.variable == 'f':
            sql += "LENGTH(w.`lemma`) = %d AND " % self.length
            for i in range(0, len(self.pattern)):
                if self.pattern[i] == '*':continue
                sql += """SUBSTR(`lemma`, %d, 1) = '%s' AND """ % (i + 1, self.pattern[i])

        elif self.variable == 'l':
            sql += "w.`lemma` LIKE '%"
            flag = False
            for i in range(0, len(self.pattern)):
                if self.pattern[i] == '*' and flag == False: continue
                flag = True # Reached a non * chartacter
                sql += self.pattern[i] if self.pattern[i] != '*' else '_'
            sql += "' AND "

        elif self.variable == 'r':
            sql += "w.`lemma` LIKE '"
            like = ''
            flag = False
            for i in range(len(self.pattern) - 1, -1, -1):
                if self.pattern[i] == '*' and flag == False: continue
                flag = True # Reached a non * chartacter
                like = (self.pattern[i] if self.pattern[i] != '*' else '_') + like
            sql += like + "%' AND "

        elif self.variable == 'b':
            like = re.sub(r'^\**(.*?)\**$', r'%\1%', self.pattern)
            like = re.sub(r'\*', r'_', like)
            sql += "w.`lemma` LIKE '%s' AND " % like

        if self.spaces is False:sql += "INSTR(w.`lemma`,' ') = 0 AND "
        if self.hyphens is False:sql += "INSTR(w.`lemma`,'-') = 0 AND "
        if self.quotations is False:sql += """INSTR(w.`lemma`,'"') = 0 AND INSTR(w.`lemma`,"'") = 0 AND """
        if self.numbers is False:sql += "w.`lemma` REGEXP '[0-9]' = 0 AND "

        sql += "1"

        return sql

    def __next__(self):        
        row = SQLite3Iterator.__next__(self)        
        self.wordid = row['wordid']        
        return row['lemma']

    def __iter__(self):
        return self

    def getMeanings(self):

        sql = """
        SELECT w.lemma, sy.definition
        FROM `words` w
        LEFT JOIN `senses` se on w.wordid = se.wordid
        LEFT JOIN `synsets` sy on se.synsetid = sy.synsetid
        WHERE w.wordid = '%d'        
        GROUP BY se.sensenum
        ;""" % (self.wordid)

        cursor = self.conn.cursor()
        # print(sql)
        cursor.execute(sql)
        rows = cursor.fetchall()
        meanings = [row['definition'] for row in rows] # List Comprehension

        return meanings
