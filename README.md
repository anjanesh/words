# words

Example:
========

`python3 test.py`

will return a JSON string that contains all 6 letter words with the second letter as **s** and the third letter as **a**.

`{
    "words":
        ["asadha", "asanga", "asarum", "bsarch", "isaiah", "isatis", "osasco", "psalms", "usable", "usacil", "usance"],
        "meanings": [
            ["the fourth month of the Hindu calendar"],
            ["Indian religious leader and founder of the Yogacara school of Buddhism in India (4th century)"],
            ["wild ginger"],
            ["a bachelor's degree in architecture"],
            ["(Old Testament) the first of the major Hebrew prophets (8th century BC)", "an Old Testament book consisting of Isaiah's prophecies"],
            ["Old World genus of annual to perennial herbs: woad"],
            ["a city in southeastern Brazil; suburb of Sao Paulo"],
            ["an Old Testament book consisting of a collection of 150 Psalms"],
            ["capable of being put to use", "fit or ready for use or service", "convenient for use or disposal"],
            ["a defense laboratory of the Criminal Investigation Command; the United States Army's primary forensic laboratory in support of criminal intelligence"],
            ["the period of time permitted by commercial usage for the payment of a bill of exchange (especially a foreign bill of exchange)", "(economics) the utilization of economic goods to satisfy needs or in manufacturing", "accepted or habitual practice"]
        ],
    "total": 11,
    "count": 11,
    "time": "0.03261208534240723",
    "status": "success",
    "message": "",
    "start": 0
}`

Change `wordPattern = "*sa***"` in test.py line 7 to change the pattern