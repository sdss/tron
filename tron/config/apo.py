"""Configuration for APO."""

__all__ = ['nubs', 'actors', 'httpHost', 'httpRoot']


nubs = ('client',
        'nclient',
        'mcp',
        'tcc',
        'apo',
        'boss',
        'hartmann',
        'apogeecal',
        'apogee',
        'apogeeql',
        'alerts',
        'TUI')


actors = dict(alerts=dict(host='sdss5-hub.apo.nmsu.edu',
                          port=9995,
                          actorName='alertsActor'),
              apo=dict(host='sdss5-hub.apo.nmsu.edu',
                       port=9990,
                       actorName='apoActor'),
              apogee=dict(host='apogee-ics.apo.nmsu.edu',
                          port=33221,
                          actorName='apogeeICC'),
              apogeecal=dict(host='apogee-ics.apo.nmsu.edu',
                             port=33222,
                             actorName='apogeecalICC'),
              apogeeql=dict(host='sdss5-apogee.apo.nmsu.edu',
                            port=18282,
                            actorName='apogeeqlActor'),
              boss=dict(host='sdss5-boss-icc.apo.nmsu.edu',
                        port=9998,
                        actorName='bossICC'),
              benchboss=dict(host='sdss5-boss-icc.apo.nmsu.edu',
                             port=9991,
                             actorName='bossICC'),
              hartmann=dict(host='sdss5-eboss.apo.nmsu.edu',
                            port=9988,
                            actorName='hartmannActor'),
              tcc=dict(host='sdss5-tcc.apo.nmsu.edu',
                       port=2500,
                       actorName='tcc'))


httpHost = 'sdss-hub.apo.nmsu.edu'
httpRoot = '/'
