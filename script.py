import requests
from json import loads
import pandas as pd
from time import sleep
from multiprocessing import Pool
from collections import OrderedDict


def choose(things, addonmsg='', **kwargs):
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


class getData():

    def __init__(self, endpoints, endpoint='people'):

        self.url = 'https://swapi.co/api/'
        self.endpoint = endpoint
        self.endpoints = endpoints
        self.path = OrderedDict()

    def get(self, **kwargs):

        if 'url' in kwargs.keys():
            return loads(requests.get(kwargs['url']).text)
        if self.endpoint in self.endpoints:
            return loads(requests.get(self.url + self.endpoint).text)
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

    def ifColumnHasUrlsThenGiveName(self, data):

        if len(data.loc[data.astype(str).str.contains(self.url)]) == 0:
            return data
        else:
            data = data.loc[data.astype(str).str.contains(self.url)]
            print('\n Making additional api calls for {} \n'.format( pd.DataFrame(data).columns[0] ))
        unique_links = []

        for val in data.values:
            if isinstance(val, tuple):
                for subval in val:
                    if subval not in unique_links:
                        unique_links.append(subval)
            else:
                unique_links.append(val)

        if __name__ == '__main__':

            pool = Pool(processes=5)
            names = pd.DataFrame(pool.map(worker, unique_links))

        else:
            exit('Can only do multiprocessing if not importing this module elsewhere')

        for idx in data.index:
            val = data.at[idx]
            val = list(val) if isinstance(val, tuple) else val
            val = [val] if isinstance(val, str) else val

            # if not isinstance(data.at[idx], list) or not isinstance(data.at[idx], tuple):
            #     val = [val]
            for subindex, subval in enumerate(val):
                val[subindex] = names[subval].loc[pd.notna(names[subval])].values[0]
            data.at[idx] = tuple(val)

        return data

    def chooseAttribute(self, data, lastChoice=None):

        columns = []
        for c in list(data.columns):
            if lastChoice:
                if c == lastChoice['column']:
                    continue
            if (c not in self.endpoints) & (c not in ['url', 'name', 'edited', 'created']):
                if len(data[c].unique()) > 1:
                    columns.append(c)

        column = choose(things=columns)

        data.loc[data.index, column] = self.ifColumnHasUrlsThenGiveName(data[column])

        options = list(data[column].unique())
        print('\n' * 5)
        option = choose(things=options, addonmsg='Ok, you chose {}.'.format(column),
                             instances={'data': data, 'column': column})

        data = data.loc[data[column] == option]

        self.path[column] = option

        if (len(data) == 1):
            return data, self.path
        else:
            data, path = self.chooseAttribute(data=data, lastChoice={'column': column, 'option': option})

            return data, path


    def list_to_tuple(self, data):
        for column in data.columns:
            try:
                data[column].unique()
            except TypeError as e:
                if "unhashable type: 'list'" in str(e):
                    data[column] = data[column].apply(lambda x: tuple(x))
        return data


if __name__ == '__main__':

    endpoints = ['people', 'planets', 'films', 'species', 'vehicles', 'starships']

    SW = getData(endpoints=endpoints, endpoint=choose(endpoints))


    def worker(link):
        return {link: SW.get(url=link)['name']}

    data = SW.getAll()

    # to allow applying .unique() on a series of lists, turn lists into tuples
    # as tuples are hashable lists are not.
    data = SW.list_to_tuple(data)

    chosen, path = SW.chooseAttribute(data)

    print('\n\n You chose: ')
    selection = ''
    for key in path:
        selection += '{}: {}, '.format(key, path[key])
        if len(path.keys()) >= 2:
            if key == list(path.keys())[-2]:
                selection += 'and finally '
    selection = selection[:-2] + '.'
    print(selection)



    # it seems that only films do not have a name attribute:
    default_keys = {'films': 'title'}
    if SW.endpoint in default_keys.keys():
        key = default_keys[SW.endpoint]
    else:
        key = 'name'

    result = chosen[key].values[0]

    print('The result is: ',result)
