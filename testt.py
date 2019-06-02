import requests
from json import loads
import pandas as pd
from time import sleep

class getData():

    def __init__(self, endpoint='people'):

        self.url = 'https://swapi.co/api/'
        self.endpoint = endpoint
        self.endpoints = ['people', 'planets', 'films', 'species', 'vehicles', 'starships']
        self.path = {}

    def get(self, **kwargs):

        if 'url' in kwargs.keys():
            return loads(requests.get(kwargs['url']).text)
        if self.endpoint in self.endpoints:
            return loads(requests.get('https://swapi.co/api/{}/'.format(self.endpoint)).text)
        else:
            print('No such api endpoint: {}, choose from: {} \n'.format(
                format(self.endpoint, self.endpoints)
            ))
            return False

    def getAll(self):
        # looping, because whether next page exists is only known from http response (r['next']):
        def recursiveGet(df, **kwargs):
            if len(df) == 0:
                r = self.get()
            else:
                r = self.get(url=kwargs['url'])

            df = df.append(r['results'], ignore_index=True)

            if not r['next']:
                return df
            else:
                print('Getting page {} of Star Wars {}'.format(r['next'][-1], self.endpoint))
                return recursiveGet(df, url=r['next'])

        return recursiveGet(pd.DataFrame())

    def getAttributes(self, instance):
        pass

    def choose(self, things, addonmsg = '', **kwargs):
        while True:
            for idx, thing in enumerate(things):
                instances = ''
                if 'instances' in kwargs.keys():
                    data = kwargs['instances']['data']
                    column = kwargs['instances']['column']
                    instances = len(data.loc[data[column] == thing])
                    if instances != 1:
                        instances = ' ({} instances)'.format(instances)
                    else:
                        instances = ' ({}) instance)'.format(instances)
                print(idx, thing, instances)
            thing = input('{} Choose from the above list (pick a number): '.format(addonmsg)).strip()
            try:
                thing = things[int(thing)]
                return thing
            except ValueError as e:
                print('Wrong choice. Choose a number from the list: ')
                sleep(2)

    def chooseAttribute(self, data, lastChoice=None):



        columns = []
        for c in list(data.columns):
            if lastChoice:
                if c == lastChoice['column']:
                    continue
            if (c not in self.endpoints) & (c not in ['url', 'name', 'edited', 'created']):
                if len(data[c].unique()) > 1:
                    columns.append(c)

        column = self.choose(things=columns)

        options = list(data[column].unique())
        print('\n' * 5)
        option = self.choose(things=options, addonmsg='Ok, you chose {}.'.format(column),
                             instances={'data': data, 'column': column})

        data = data.loc[data[column] == option]

        self.path[column] = option

        if (len(data) == 1):
            return data, self.path
        else:
            data, path = self.chooseAttribute(data=data, lastChoice = {'column': column, 'option': option})

            return data, path

        print(option)

if __name__  == '__main__':
    SW = getData(endpoint='starships')
    people = SW.getAll()
    chosen, path = SW.chooseAttribute(people)
    print(chosen['name'].values[0])
print(1)