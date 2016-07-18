"""Configuration for LCO."""

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

actors = dict(alerts=    dict(host="sdss4-hub.lco.cl", port=9995, actorName='alertsActor'),
              lco=       dict(host="sdss4-hub.lco.cl", port=9990, actorName='apoActor'),
              gcamera=   dict(host="sdss4-hub.lco.cl", port=9993, actorName='gcameraICC'),
              ecamera=   dict(host="sdss4-hub.lco.cl", port=9987, actorName='ecameraICC'),
              guider=    dict(host="sdss4-hub.lco.cl", port=9994, actorName='guiderActor'),
              toy=       dict(host="sdss4-hub.lco.cl", port=9000, actorName='toyActor'),
              sop=       dict(host="sdss4-hub.lco.cl", port=9989, actorName='sopActor'),
              tcc=       dict(host="sdss4-hub.lco.cl", port=25000, actorName='tcc'),
              platedb=   dict(host="sdss4-hub.lco.cl", port=9992, actorName='platedbActor'),

              # NOTE: eventually!
              # apogee=    dict(host="apogee-ics.lco.cl", port=33221, actorName='apogeeICC'),
              # apogeecal= dict(host="apogee-ics.lco.cl", port=33222, actorName='apogeecalICC'),
              # apogeeql=  dict(host="sdss4-apogee.lco.cl", port=18282, actorName='apogeeqlActor'),
              )

# Eventually it will be this, but for now we are using the BPG URL.
# httpHost = 'sdss-hub.lco.cl'
httpHost = '139.229.101.71'
httpRoot = '/'
