# Handle registering and loading of files

import os
import json
import getpass
import base64
from urllib.request import Request, urlopen
import urllib.parse
import re
from terminaltables import AsciiTable
import glob
import csv


class User:

    def __init__(self):
        self.dirpath = os.path.expanduser('~/.oftt')
        self.cfgpath = os.path.expanduser('~/.oftt/config.json')

        if self.exists_user():
            self.load()
        else:
            self.register()

    def exists_user(self):
        if not self.files_exist():
            self.create_filestructure()
            return False
        return self.files_contain_userdata()

    def files_exist(self):
        if os.path.isdir(self.dirpath):
            if os.path.exists(self.cfgpath):
                return True
        return False

    def create_filestructure(self):
        if not os.path.isdir(self.dirpath):
            os.mkdir(self.dirpath)
        open(self.cfgpath, "x")

    # TODO Write more advanced checks, like if values are present and have correct format etc
    def files_contain_userdata(self):
        file = open(self.cfgpath, 'r')
        content = file.read()
        parsed = json.loads(content)

        if not 'auth' in parsed:
            return False
        if not 'lectures' in parsed:
            return False
        return True

    def register(self):
        data = dict()
        data['auth'] = self.get_login_data()
        print(data['auth'])
        data['lectures'] = self.get_lecture_data(data['auth'])



    def get_login_data(self):
        print('WARNING: THIS WILL SAVE YOUR CREDENTIALS IN BASICALLY CLEARTEXT!!!')
        print('neither do I know, nor do I care how to do this better though... xD')

        username = input('username (idxxxxxx): ')
        password = getpass.getpass()
        print(bytes(username + ":" + password, 'utf-8'))
        return 'Basic ' + str(base64.b64encode(bytes(username + ':' + password, 'utf-8')))[2:-1]

    def get_lecture_data(self, auth):
        self.download(auth)
        lectures = []

        files = glob.glob(self.dirpath+'/*.csv')
        files.sort()
        file = self.select(files)

        lectures = self.select(self.compile_subjects(file), multiple=True)
        print(lectures)

    def compile_subjects(self, file):
        with open(file, 'r') as csvfile:
            csvreader=csv.reader(csvfile, delimiter=";")
            fields = next(csvreader)
            rows = list()
            for row in csvreader:
                rows.append(row[2])
        return list(set(rows))


    def download(self, auth):
        baseurl = 'https://stundenplan.ostfalia.de/i/Alle%20Daten%20im%20CSV-Format/Semester/'
        req = Request(baseurl)
        req.add_header('Authorization', auth)
        content = urlopen(req).read()
        items = re.findall('<a[^>]*.csv">', str(content))
        pattern = re.compile(r'\".*\"')
        items = [pattern.findall(x)[0][1:-1] for x in items]
        for file in items:
            req = Request(baseurl + file)
            req.add_header('Authorization', auth)

            with open(self.dirpath+'/' +urllib.parse.unquote(file).replace(" ", "-"), 'w') as f:
                f.write(urlopen(req).read().decode('unicode_escape'))

    def select(self, data, multiple=False):
        table_data = [[data.index(d), d] for d in data]
        table_data.insert(0, ["ID", "Name"])
        table = AsciiTable(table_data)
        print(table.table)
        while True:
            if multiple:
                indexes = input("Enter desired indexes (1,2,3): ")
            else:
                index = input("Enter desired index: ")
            try:
                if multiple:
                    indexes = [int(x) for x in indexes.split(',')]
                    indexes.sort()
                    flag = False
                    for i in indexes:
                        if i < 0 or i >= len(data):
                            flag = True
                    if not flag:
                        break
                else:
                    index = int(index)
                    if index >= 0 and index < len(data):
                        break
            except:
                print("Wrong format! Enter again...")
        if multiple:
            return [data[i] for i in indexes]
        else:
            return data[index]
