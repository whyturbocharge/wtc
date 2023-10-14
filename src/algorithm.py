
from src.data import Data

import numpy as np

import time

class Algorithm(Data):

    def __init__(self, presets):
        super().__init__(presets)

        self.version = '0.0.0'

    def eval(self):
        data  = self.get_database()

        try:
            updated_data = self.calculate_algorithm(data)
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")

        self.print_results(updated_data, 'entries updated')

        if len(updated_data) > 0:
            self.result = True

    def calculate_algorithm(self, data):

        created_values     = self.created_eval(data)
        description_values = self.description_eval(data)
        tags_values        = self.tags_eval(data)
        views_values       = self.views_eval(data)
        seen_values        = self.seen_eval(data)
        flickr_values      = self.flickr_eval(data)

        select = []

        i = 0
        for entry in data:
            raw_values = []

            raw_values.append(created_values[i])
            raw_values.append(description_values[i])
            raw_values.append(tags_values[i])
            raw_values.append(views_values[i])
            # raw_values.append(seen_values[i])
            raw_values.append(flickr_values[i])

            values = np.asarray(raw_values)
            resulted_value = np.sum(values) / len(raw_values)
            algorithm = round(resulted_value * 1024)

            if 'algorithm' not in entry or entry['algorithm']['value'] != algorithm:
                self.db.update({
                    'algorithm': {
                        'value': algorithm
                    }
                }, self.data.name == entry['name'])
                select.append(entry)

            i += 1

        return select

    def views_eval(self, data):
        now = round(time.time()*1000)
        added_min = self.get_added_min(data)

        values = np.zeros(len(data))

        i = 0
        for entry in data:
            if 'online' in entry:
                views = np.zeros(len(entry['online']['views']))
                j = 0
                for view in entry['online']['views']:
                    views[j] = (view['server'] - added_min) / (now - added_min)
                    j += 1

                values[i] = np.sum(views)

            i += 1

        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = value * 0.25

        return values

    def seen_eval(self, data):
        now = round(time.time()*1000)
        added_min = self.get_added_min(data)

        values = np.zeros(len(data))

        i = 0
        for entry in data:
            if 'online' in entry:
                seen = np.zeros(len(entry['online']['seen']))
                j = 0
                for see in entry['online']['seen']:
                    seen[j] = (see['server'] - added_min) / (now - added_min)
                    j += 1

                values[i] = np.sum(seen)
            else:
                values[i] = 0
            i += 1

        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = (1 - value) * 0.25

        return values

    def flickr_eval(self, data):

        now = round(time.time()*1000)
        added_min = self.get_added_min(data)

        values = np.zeros(len(data))

        i = 0
        for entry in data:
            if 'flickr' in entry:
                flickr = np.zeros(len(entry['flickr']['views']))
                j = 0
                for flickrView in entry['flickr']['views']:
                    flickr[j] = (flickrView - added_min) / (now - added_min)
                    j += 1

                values[i] = np.sum(flickr)
            else:
                values[i] = 0
            i += 1

        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = value * 0.5

        return values

    def created_eval(self, data):
        values = np.zeros(len(data))

        i = 0
        for entry in data:
            values[i] = entry['metadata']['created']
            i += 1

        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = value * 0.5

        return values

    def tags_eval(self, data):
        values = np.zeros(len(data))

        i = 0
        for entry in data:
            for tag in entry['metadata']['keywords']:
                if tag == 'A5':
                    values[i] += 1
                if tag == 'A4':
                    values[i] += 1
                if tag == 'A3':
                    values[i] += 1
            i += 1

        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = value * 0.5

        return values

    def description_eval(self, data):
        values = np.zeros(len(data))

        i = 0
        for entry in data:
            if entry['metadata']['description'] == '':
                values[i] += 1
            i += 1
 
        min = np.min(values)
        max = np.max(values)

        for i in range(values.shape[0]):
            value = self.project(values[i], min, max, 0, 1)
            values[i] = value * 0.5

        return values

    def get_added_min(self, data):
        added = np.zeros(len(data))

        i = 0
        for entry in data:
            added[i] = entry['metadata']['added']
            i += 1
        
        return np.min(added)

    def project(self, value, istart, istop, ostart, ostop):
        if istop - istart == 0:
            return 0
        else:
            return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))