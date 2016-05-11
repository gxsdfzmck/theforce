# -*- coding: utf-8 -*-
import os

import yaml


class Repository(object):
    def __init__(self, abs_files):
        self._repo = dict([self.load(f) for f in abs_files])

    def load(self, abs_file):
        with open(abs_file) as f:
            model = yaml.load(f.read())
            return (os.path.basename(abs_file)[:-4], model)

    def get(self, model_name):
        return self._repo[model_name] if model_name in self._repo else None
