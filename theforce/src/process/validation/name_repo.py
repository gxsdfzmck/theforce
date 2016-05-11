# -*- coding: utf-8 -*-
import os

class NameRepository(object):

    def __init__(self, repo_name):
        self.repo_name = repo_name
        self.file_name = os.path.join(os.path.dirname(__file__), repo_name+'.txt')
        self.load()

    def load(self):
        if os.path.isfile(self.file_name):
            with open(self.file_name) as f:
                options = f.readlines()
                self.options = set([o.strip() for o in options if len(o.strip)>0])
        else:
            self.options = set()

    def is_in(self, checked):
        return checked in self.options

    def append(self, content):
        if content and len(content.strip()) > 0:
            content = content.strip()
            if not self.is_in(content):
                self.options.add(content)
                with open(self.file_name, 'a+') as f:
                    f.write(content)
        

