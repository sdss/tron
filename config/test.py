"""Configuration for testing."""

nubs = ('client',
        'nclient',

        'tcc',
        'lco',

        'alerts',
        'sop',
        'platedb',
        'gcamera',
        'guider',

        'apogeecal',
        'apogee',
        'apogeeql',

        'TUI')

actors = dict(alerts=    dict(host="localhost", port=9995, actorName='alertsActor'),
              # apo=       dict(host="localhost", port=9990, actorName='apoActor'),
              gcamera=   dict(host="139.229.101.50", port=9993, actorName='gcameraICC'),
              # ecamera=   dict(host="localhost", port=9987, actorName='ecameraICC
              guider=    dict(host="139.229.101.50", port=9994, actorName='guiderActor'),
              toy=       dict(host="localhost", port=9000, actorName='toyActor'),
              sop=       dict(host="localhost", port=9989, actorName='sopActor'),

              # platedb=   dict(host="localhost", port=9992, actorName='platedbActor'),

              # NOTE: eventually!
              # apogee=    dict(host="apogee-ics.lco.cl", port=33221, actorName='apogeeICC'),
              # apogeecal= dict(host="apogee-ics.lco.cl", port=33222, actorName='apogeecalICC'),
              # apogeeql=  dict(host="sdss4-apogee.lco.cl", port=18282, actorName='apogeeqlActor'),
              )

httpHost = '139.229.101.50'
httpRoot = '/'
