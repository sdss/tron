import os

# Where to save the logs
logDir = '/data/logs/tron'

# Which words to load internally.
vocabulary = ('perms', 'hub', 'keys', 'msg')
nubs = ('client',
        'nclient',

        'mcp',
        'tcc',
        'apo',

        'sop',
        'platedb',
        'gcamera',
        'boss',
        'hartmann',
        'guider',
        'apogeecal',
        'apogee',
        'apogeeql',
        'alerts',

        'TUI')

actors = dict(alerts=    dict(host="sdss4-hub.apo.nmsu.edu", port=9995, actorName='alertsActor'),
              apo=       dict(host="sdss4-hub.apo.nmsu.edu", port=9990, actorName='apoActor'),
              gcamera=   dict(host="sdss4-hub.apo.nmsu.edu", port=9993, actorName='gcameraICC'),
              ecamera=   dict(host="sdss4-hub.apo.nmsu.edu", port=9987, actorName='ecameraICC'),
              guider=    dict(host="sdss4-hub.apo.nmsu.edu", port=9994, actorName='guiderActor'),
              toy=       dict(host="sdss4-hub.apo.nmsu.edu", port=9000, actorName='toyActor'),
              sop=       dict(host="sdss4-hub.apo.nmsu.edu", port=9989, actorName='sopActor'),

              telemetry= dict(host="sdss4-telemetry.apo.nmsu.edu", port=9986, actorName='telemetryActor'),

              platedb=   dict(host="sdss4-hub.apo.nmsu.edu", port=9992, actorName='platedbActor'),

              apogee=    dict(host="apogee-ics.apo.nmsu.edu", port=33221, actorName='apogeeICC'),
              apogeecal= dict(host="apogee-ics.apo.nmsu.edu", port=33222, actorName='apogeecalICC'),
              apogeeql=  dict(host="sdss4-apogee.apo.nmsu.edu", port=18282, actorName='apogeeqlActor'),

              boss=      dict(host="sdss4-boss-icc.apo.nmsu.edu", port=9998, actorName='bossICC'),
              benchboss= dict(host="sdss4-boss-icc.apo.nmsu.edu", port=9991, actorName='bossICC'),

              hartmann=   dict(host="sdss4-eboss.apo.nmsu.edu", port=9988, actorName='hartmannActor'),
              )

httpHost = 'sdss-hub.apo.nmsu.edu'
httpRoot = '/'
