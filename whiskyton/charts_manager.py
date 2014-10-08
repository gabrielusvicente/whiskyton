# coding: utf-8

from unipath import Path
from flask.ext.script import Manager
from whiskyton import charts, models
ChartsCommand = Manager(usage='Manage chart cache')


@ChartsCommand.command
def delete():
    "Delete all cached charts"
    folder = Path(charts.cache_path()).listdir()
    count = 0
    size = 0
    total = float(len(folder))
    for f in folder:
        print '%s Deleting %s (%s)' % (percent((count / total)),
                                       f.absolute(),
                                       filesize(f.size()))
        if f.isfile():
            count += 1
            size += f.size()
            f.remove()
    print '%s cached charts deleted (%s)' % (count, filesize(size))


@ChartsCommand.command
def create():
    "Create all charts as cache"

    # support vars
    different_tastes = []
    count = 0
    size = 0

    # get whiskies
    whiskies = models.Whisky.query.all()
    for whisky in whiskies:
        tastes = charts.tastes2list(whisky)
        if tastes not in different_tastes:
            different_tastes.append(tastes)
    total = len(different_tastes) * (len(different_tastes) - 1.0)

    # combination
    for reference in different_tastes:
        for whisky in different_tastes:
            if whisky != reference:
                filename = charts.cache_name(reference, whisky, True)
                if filename.exists():
                    filename.remove()
                charts.create(reference, whisky)
                size += Path(filename).size()
                count += 1
                print '%s Created %s (%s)' % (percent(count / total),
                                              filename.absolute(),
                                              filesize(filename.size()))
    print '%s charts created (%s)' % (count, filesize(size))


@ChartsCommand.command
def list():
    "List chached charts"
    folder = Path(charts.cache_path()).listdir()
    count = 0
    size = 0
    for f in folder:
        if f.isfile():
            print '%s (%s)' % (f.absolute(), filesize(f.size()))
            count += 1
            size += f.size()
    print '%s cached files (%s)' % (count, filesize(size))


def filesize(size):
    sizes = {
        9: 'Gb',
        6: 'Mb',
        3: 'Kb',
        0: 'bytes'
    }
    for i in [9, 6, 3, 0]:
        if size >= 10 ** i:
            return '{:.1f}'.format(size / (10.0 ** i)) + sizes[i]
    return '0 %s' % sizes[0]


def percent(number):
    return '{:.1f}%'.format(number * 100)