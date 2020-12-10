from tokens import *
import psutil
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import operator
import time
import sys
import telepot
import os
import Adafruit_DHT

shellexecution = []
timelist = []

stopmarkup = {'keyboard': [['Stop']]}
hide_keyboard = {'hide_keyboard': True}

def clearall(chat_id):
    if chat_id in shellexecution:
        shellexecution.remove(chat_id)

class YourBot(telepot.Bot):
    def __init__(self, *args, **kwargs):
        super(YourBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        # Do your stuff according to `content_type` ...
        #print("Your chat_id:" + str(chat_id)) # this will tell you your chat_id
        if chat_id in adminchatid:  # Store adminchatid variable in tokens.py
            if content_type == 'text':
                if msg['text'] == '/stats' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    memory = psutil.virtual_memory()
                    disk = psutil.disk_usage('/')
                    boottime = datetime.fromtimestamp(psutil.boot_time())
                    now = datetime.now()
                    timedif = "Online for: %.1f Hours" % (((now - boottime).total_seconds()) / 3600)
                    memtotal = "Total memory: %.2f GB " % (memory.total / 1000000000)
                    memavail = "Available memory: %.2f GB" % (memory.available / 1000000000)
                    memuseperc = "Used memory: " + str(memory.percent) + " %"
                    diskused = "Disk used: " + str(disk.percent) + " %"
                    pids = psutil.pids()
                    pidsreply = ''
                    procs = {}
                    for pid in pids:
                        p = psutil.Process(pid)
                        try:
                            pmem = p.memory_percent()
                            if pmem > 0.5:
                                if p.name() in procs:
                                    procs[p.name()] += pmem
                                else:
                                    procs[p.name()] = pmem
                        except:
                            print("Hm")
                    sortedprocs = sorted(procs.items(), key=operator.itemgetter(1), reverse=True)
                    for proc in sortedprocs:
                        pidsreply += proc[0] + " " + ("%.2f" % proc[1]) + " %\n"
                    reply = timedif + "\n" + \
                            memtotal + "\n" + \
                            memavail + "\n" + \
                            memuseperc + "\n" + \
                            diskused + "\n\n" + \
                            pidsreply
                    bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                elif msg['text'] == "Stop":
                    clearall(chat_id)
                    bot.sendMessage(chat_id, "All operations stopped.", reply_markup=hide_keyboard)
                elif msg['text'] == "/shell" and chat_id not in shellexecution:
                    bot.sendMessage(chat_id, "Send me a shell command to execute", reply_markup=stopmarkup)
                    shellexecution.append(chat_id)
                elif chat_id in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    p = Popen(msg['text'], shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    output = p.stdout.read()
                    if output != b'':
                        bot.sendMessage(chat_id, output, disable_web_page_preview=True)
                    else:
                        bot.sendMessage(chat_id, "No output.", disable_web_page_preview=True)
                elif msg['text'] == '/temp' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    humidity, temperature = Adafruit_DHT.read_retry(Adafruit_DHT.AM2302, 17)
                        if humidity is not None and temperature is not None:
                            tmpform = "Температура воздуха = {0:0.1f}*".format(temperature)
                            humform = "Влажность воздуха = {0:0.1f}%".format(humidity)
                            reply = tmpform + "\n" + \
                                    humform
                            bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                        else:
                            bot.sendMessage(chat_id, "Ошибка получения данных!", disable_web_page_preview=True)
                elif msg['text'] == '/cpu' and chat_id not in shellexecution:
                    bot.sendChatAction(chat_id, 'typing')
                    data = open("/sys/class/thermal/thermal_zone0/temp", 'r').read().strip()
                    reply = "Температура процессора = {0:0.1f}*".format(float(data)/1000)
                    if data is not None:
                        bot.sendMessage(chat_id, reply, disable_web_page_preview=True)
                    else:
                        bot.sendMessage(chat_id, "Ошибка чтения температуры процессора!", disable_web_page_preview=True)


TOKEN = telegrambot

bot = YourBot(TOKEN)
bot.message_loop()