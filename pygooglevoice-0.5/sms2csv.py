#!/usr/bin/python

from googlevoice import Voice
import re
import sys
import csv
import datetime
import StringIO
import BeautifulSoup


def nextConversation(json, html) :
    tree = BeautifulSoup.BeautifulSoup(html)
    convBlock = tree.findAll('div', attrs={'id' : True}, recursive=False)
    jsonMessages = json['messages']
    for conv in convBlock :
        convId = conv['id']
        convmap = jsonMessages[convId]
        rows = conv.findAll(attrs={'class' : 'gc-message-sms-row'})
        messages = []
        for row in rows:
            spans = row.findAll('span', attrs={'class' : True}, recursive=False)
            msgitem = {}
            for span in spans:
                cl = span['class'].replace('gc-message-sms-', '')
                msgitem[cl] = (' '.join(span.findAll(text=True))).strip()
            messages.append(msgitem)
        convmap['messages'] = messages
        yield convmap
    return

voice = Voice()
voice.login('YOUR-GV-USER-ID', 'YOUR-GV-PASSWORD')

header = ('id', 'phone', 'date', 'time', 'from', 'text')
conversations = []
page = 0
dtdate = datetime.date
while True:
    page += 1
    voice.sms(page)
    count = 0
    for conv in nextConversation(voice.sms.data, voice.sms.html):
        count += 1
        startTime   = conv['startTime'].encode("utf-8")
        phoneNumber = conv['phoneNumber'].encode("utf-8")
        floatTime   = float(startTime) / 1000.0
        date        = dtdate.fromtimestamp(floatTime).strftime('%Y-%m-%d').encode('utf-8')
        item = 0
        messages = conv['messages']
        for message in messages:
            messageFrom = message['from'].encode("utf-8")
            messageTime = message['time'].encode("utf-8")
            messageText = message['text'].encode("utf-8")
            id = ('%s-%04d' % (startTime, item)).encode("utf-8")
            conversations.append((id, phoneNumber, date, messageTime, messageFrom, messageText));
                                  
            item += 1
    if count < 1:
        break
    sys.stderr.write("retrieved page %d\n" % page)

first = True
sh = StringIO.StringIO()
csvWriter = csv.writer(sh, quoting=csv.QUOTE_MINIMAL)
for conv in sorted(conversations, key=lambda element: element[0]):
    if first:
        first = False
        csvWriter.writerow(header)
    csvWriter.writerow(conv)

output = sh.getvalue()
sh.close()

sys.stdout.write(output)
