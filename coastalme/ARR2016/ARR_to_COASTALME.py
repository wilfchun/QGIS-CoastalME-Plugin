# import required modules
import os
import sys
from datetime import datetime

import logging
from coastalme.ARR2016.ARR_COASTALME_func_lib import get_args, tpRegion_coords
pythonV = sys.version_info[0]
if pythonV == 3:
    from urllib import request as urllib2
elif pythonV == 2:
    import urllib2
import requests, zipfile, io, json
import traceback


# sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # this script is always called through cmd so this will only be temporary
# sys.path.append(os.path.dirname(__file__))  # this script is always called through cmd so this will only be temporary
from coastalme.__version__ import version as get_version

from coastalme.ARR2016.arr_settings import ArrSettings
from coastalme.ARR2016.ARR_WebRes import Arr
from coastalme.ARR2016.BOM_WebRes import Bom as BOM
from coastalme.ARR2016.downloader import Downloader


# remote debugging
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2020.3.1\debug-eggs')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2020.3.1\plugins\python\helpers\pydev')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.2\debug-eggs')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.2\plugins\python\helpers\pydev')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\debug-eggs')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2019.1.3\helpers\pydev')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\debug-eggs')
# sys.path.append(r'C:\Program Files\JetBrains\PyCharm 2024.1.4\plugins\python\helpers\pydev')

def ARR_to_COASTALME(args_list):
    settings = ArrSettings.get_instance()
    build_type, version = get_version()
    now = datetime.now()
    disclaimer = 'This plugin is provided free of charge as a tool to automate the process of obtaining hydrologic data\n' \
                 'from the ARR datahub and BOM IFD. In no event will BMT Pty Ltd (the developer) be liable for the\n' \
                 'results of this plugin. The accuracy of this data, and any pre-processing done by this plugin is the\n' \
                 'responsibility of the user. Please cross check all results with the raw ARR datahub text files.'

    # inputs
    site_name = '205'  # site id, used in outputs
    latitude = -37.6243  # note negative sign
    longitude = 145.0491  # non negative :)
    catchment_area = 3.785276443449942  # catchment area (km2)
    AEP = {'1%': 'AEP'} # dict object {magnitude(str): unit(str)} e.g. {'100y': 'ARI', '2%': 'AEP', '0.5': 'EY'} or 'all'
    duration = {60: 'm'}  # dict object {mag(float/int): unit(str)} e.g. {30: 'm', 60: 'm', 1.5: 'h'} or 'all'
    non_stnd_dur = {}  # non-standard durations. dict object similar to duraton e.g. {4.5: 'hr'}
    point_tp_csv = None  #r"C:\_Advanced_Training\Module_Data\ARR\WT_Increments.csv"  # file path or None
    areal_tp_csv = None  #"C:\_Advanced_Training\Module_Data\ARR\Areal_Rwest_Increments.csv"  # file path or None
    out_form = 'csv'   # csv or ts1
    output_notation = 'ari'  # controls output notation e.g. output as 1p_60m or 100y_60m
    frequent_events = False  # set to true to include frequent events (12EY - 0.2EY)
    rare_events = False  # set to true to include rare events (1 in 200 - 1 in 2000)
    cc = True  # Set to True to output climate change
    cc_param = {}
    cc_years = []  # climate change years. List object [year(int)] e.g. [2090]
    cc_RCP = []  # Representative Concentration Pathways. List object [RCP(str)] e.g. ['RCP8.5']
    preBurst = '50%'  # preburst percentile
    lossMethod = 'interpolate'  # chosen loss method e.g. 60min, interpolate, rahman, hill, static
    mar = 0  # mean annual rainfall - for the rahman loss method
    staticLoss = 0  # for the static loss method
    coastalme_loss_method = 'infiltration'  # options: infiltration, excess
    user_initial_loss = None  # float or str or None  e.g. 10, '10', None
    user_continuing_loss = None  # float or str or None e.g. 2.5, '2.5', None
    urban_initial_loss = None
    urban_continuing_loss = None
    use_global_continuing_loss = False
    probability_neutral_losses = True
    bComplete_storm = False
    preburst_pattern_method = None
    preburst_pattern_dur = None
    preburst_pattern_tp = None
    bPreburst_dur_proportional = False
    add_tp = []  # additional temporal patterns to include in the extract
    ARF_frequent = False  # Set to true if you want to ignore ARF limits and apply to frequent events (>50% AEP)
    min_ARF = 0.2  # minimum ARF factor
    export_path = r'E:\ARR_tool_debugging'  # Export path
    access_web = True  # once the .html files have been read, they are saved and you can set this to false for debugging
    bom_raw_fname = None  # str or None
    arr_raw_fname = None  # str or None
    catchment_no = 0  # used in batch mode if specifying more than one catchment. Iterate in cmd to append catchments.
    limb_data = None
    all_point_tp = False
    add_areal_tp = 0

    # batch inputs (system/cmd arguments). If not running from GIS, will use above inputs as defaults so be careful.
    try:
        arg_error, arg_message, args = get_args(args_list)
    except Exception as e:
        if '-out' in args_list:
            i = args_list.index('-out')
            export_path = args_list[i+1]
        else:
            export_path = __file__
        logger = r'{0}{1}err_log.txt'.format(export_path, os.sep)
        with open(logger, 'w') as fo:
            fo.write("ERROR: Unable to read arguments...")
            raise Exception("Error: Unable to read arguments...")

    # export path - get earlier so we can start logging
    if 'out' in args.keys():
        export_path = args['out'][0].strip("'").strip('"')  # remove input quotes from path
    # site name - get earlier so we can start logging
    if 'name' in args.keys():
        site_name = args['name'][0]

    # logger - new in 3.0.4 - move away from using stdout and stderr
    logger = logging.getLogger('ARR2019')
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(r'{0}{1}{2}_log.txt'.format(export_path, os.sep, site_name), mode='w')
    fh.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    fmt = logging.Formatter('%(message)s')
    fh.setFormatter(fmt)
    ch.setFormatter(fmt)
    logger.addHandler(fh)
    logger.addHandler(ch)

    #print('STARTING ARR2019 to COASTALME SCRIPT\nVersion: {0}\nScript run date: {1:02d}-{2:02d}-{3} at ' \
    #      '{4:02d}:{5:02d}:{6:02d}\n\nFound the following system arguments:'\
    #      .format(version, now.day, now.month, now.year, now.hour, now.minute, now.second))
    logger.info('STARTING ARR2019 to COASTALME SCRIPT\nVersion: {0}\nScript run date: {1:02d}-{2:02d}-{3} at ' \
                '{4:02d}:{5:02d}:{6:02d}\n\nFound the following system arguments:'\
                .format(version, now.day, now.month, now.year, now.hour, now.minute, now.second))
    # create argument order map so arguments are always printed in the same order
    arg_map = {'name': 0, 'coords': 1, 'area': 2, 'mag': 3, 'dur': 4, 'nonstnd': 5, 'format': 6, 'output_notation': 7,
               'frequent': 8, 'rare': 9, 'cc': 10, 'cc_param': 11, 'rcp': 12, 'preburst': 13, 'lossmethod': 14, 'mar': 15,
               'lossvalue': 16, 'coastalme_loss_method': 17, 'probability_neutral_losses': 18,
               'complete_storm': 18.1, 'preburst_pattern_method': 18.2, 'preburst_pattern_dur': 18.3,
               'preburst_pattern_tp': 18.4, 'preburst_dur_proportional': 18.5,
               'user_initial_loss': 19,
               'user_continuing_loss': 20,
               'urban_initial_loss': 21, 'urban_continuing_loss': 22,
               'global_continuing_loss': 22.5, 'addtp': 23,
               'point_tp': 24, 'areal_tp': 25, 'arffreq': 26, 'minarf': 27, 'out': 28, 'offline_mode': 29, 'arr_file': 30,
               'bom_file': 31, 'catchment_no': 32, 'limb': 33, 'all_point_tp': 34, 'add_areal_tp': 35}
    for key in sorted(args, key=lambda k: arg_map[k]):
        value = args[key]
        #print('{0}={1};'.format(key, ",".join(map(str,value))))
        logger.info('{0}={1};'.format(key, ",".join(map(str,value))))
    #print('\n')
    logger.info('\n')
    if arg_error:
        #print(arg_message)
        logger.error(arg_message)
        logging.shutdown()
        raise Exception(arg_message)

    # longitude and latitude (must be input as argument)
    if 'coords' in args.keys():
        coords = args['coords']
        for x in coords:
            if float(x) < -9.0 and float(x) > -45.0:
                latitude = float(x)
            elif float(x) > 110.0 and float(x) < 155.0:
                longitude = float(x)
            else:
                #print('Coordinates not recognised. Must be in decimal degrees. Latitude must be negative. ' \
                #      'Or input coordinates may be out of available range for ARR2016')
                logger.error('Coordinates not recognised. Must be in decimal degrees. Latitude must be negative. ' \
                      'Or input coordinates may be out of available range for ARR2016')
                logging.shutdown()
                raise Exception('Coordinates not recognised. Must be in decimal degrees. Latitude must be negative. ' \
                                 'Or input coordinates may be out of available range for ARR2016')

    # AEP
    if 'mag' in args.keys():
        event_mags = args['mag']
        AEP = {}
        try:
            if event_mags[0].lower() == 'all':
                AEP = 'all'
            else:
                event_mags = str(event_mags).strip('[').strip(']').strip("'").strip()
                event_mags = event_mags.split(' ')
                for event_mag in event_mags:
                    if event_mag[-2:] == 'EY':
                        AEP[event_mag[:-2]] = event_mag[-2:]
                    elif event_mag[-3:] == 'ARI':
                        AEP[event_mag[:-3] + 'y'] = event_mag[-3:]
                    else:
                        AEP[event_mag[:-3] + '%'] = event_mag[-3:]
        except:
            #print('Could not process event magnitude arguments. Make sure it is in the form [X]AEP or [X]ARI or [X]EY')
            logger.error('Could not process event magnitude arguments. Make sure it is in the form [X]AEP or [X]ARI or [X]EY')
            logging.shutdown()
            raise Exception('Could not process event magnitude arguments. Make sure it is in the form [X]AEP or [X]ARI or [X]EY')

    # duration
    if 'dur' in args.keys():
        duration = {}
        if args['dur'][0] == 'none':
            duration = {}
        elif len(args['dur']) > 0:
            event_durs = args['dur']
            try:
                if event_durs[0].lower() == 'all':
                    duration = 'all'
                else:
                    event_durs = str(event_durs).strip('[').strip(']').strip("'").strip()
                    event_durs = event_durs.split(' ')
                    for event_dur in event_durs:
                        try:
                            duration[float(event_dur[:-1])] = event_dur[-1]
                        except:
                            if event_dur[-2:].lower() == 'hr':
                                duration[float(event_dur[:-2])] = event_dur[-2:]
                            else:
                                duration[float(event_dur[:-3])] = event_dur[-3:]

            except:
                #print('Could not process duration arguments. Make sure unit is specified (s, m, h, d)')
                logger.error('Could not process duration arguments. Make sure unit is specified (s, m, h, d)')
                logging.shutdown()
                raise Exception('Could not process duration arguments. Make sure unit is specified (s, m, h, d)')

    # non standard durations
    if 'nonstnd' in args.keys():
        non_stnd_dur = {}
        if args['nonstnd'][0] == 'none':
            non_stnd_dur = {}
        elif len(args['nonstnd']) > 0:
            event_nonstnd_durs = args['nonstnd']
            try:
                event_nonstnd_durs = str(event_nonstnd_durs).strip('[').strip(']').strip("'").strip()
                event_nonstnd_durs = event_nonstnd_durs.split(' ')
                for event_nonstnd_dur in event_nonstnd_durs:
                    try:
                        non_stnd_dur[float(event_nonstnd_dur[:-1])] = event_nonstnd_dur[-1]
                    except:
                        if event_nonstnd_dur[-2:].lower() == 'hr':
                            non_stnd_dur[float(event_nonstnd_dur[:-2])] = event_nonstnd_dur[-2:]
                        else:
                            non_stnd_dur[float(event_nonstnd_dur[:-3])] = event_nonstnd_dur[-3:]
            except:
                #print('Could not process non-standard event duration arguments. Make sure unit is specified (s, m, h, d)')
                logger.error('Could not process non-standard event duration arguments. Make sure unit is specified (s, m, h, d)')
                logging.shutdown()
                raise Exception('Could not process non-standard event duration arguments. Make sure unit is specified (s, m, h, d)')

    # frequent event switch
    if 'frequent' in args.keys():
        if args['frequent'][0].lower() == 'true':
            frequent_events = True
        elif args['frequent'][0].lower() == '':
            frequent_events = True
        else:
            frequent_events = False
    # rare event switch
    if 'rare' in args.keys():
        if args['rare'][0].lower() == 'true':
            rare_events = True
        elif args['rare'][0].lower() == '':
            rare_events = True
        else:
            rare_events = False
    # output format
    if 'format' in args.keys():
        out_form = args['format'][0]
    # climate change
    if 'cc' in args.keys():
        if args['cc'][0].lower() == 'true':
            cc = True
        elif args['cc'][0].lower() == '':
            cc = True
        else:
            cc = False
    if 'cc_param' in args.keys():
        if args['cc_param'] and args['cc_param'][0]:
            cc_param = json.loads(args['cc_param'][0])
    # climate change year
    if 'year' in args.keys():
        cc_years = []
        if args['year'][0] == 'none':
            cc_years = []
        elif len(args['year']) > 0:
            try:
                cc_years_str = args['year']
                cc_years_str = str(cc_years_str).strip('[').strip(']').strip("'").strip()
                cc_years_str = cc_years_str.split(' ')
                for item in cc_years_str:
                    cc_years.append(float(item))
            except:
                #print('Could not process climate change forecast year arguments')
                logger.error('Could not process climate change forecast year arguments')
                logging.shutdown()
                raise Exception('Could not process climate change forecast year arguments')

    # RCP
    if 'rcp' in args.keys():
        cc_RCP = []
        if args['rcp'][0] == 'none':
            cc_RCP = []
        elif len(args['rcp']) > 0:
            try:
                cc_RCP_str = args['rcp']
                cc_RCP_str = str(cc_RCP_str).strip('[').strip(']').strip("'").strip()
                cc_RCP_str = cc_RCP_str.split(' ')
                for item in cc_RCP_str:
                    cc_RCP.append('RCP{0}'.format(item))
            except:
                #print('Could not process climate change RCP arguments')
                logger.error('Could not process climate change RCP arguments')
                logging.shutdown()
                raise Exception('Could not process climate change RCP arguments')

    # catchment area
    if 'area' in args.keys():
        catchment_area = float(args['area'][0])
    # catchment number
    if 'catchment_no' in args.keys():
        catchment_no = float(args['catchment_no'][0])
    # Output notation
    if 'output_notation' in args.keys():
        if 'ari' in args['output_notation'][0].lower():
            output_notation = 'ari'
        else:
            output_notation = 'aep'
    # Preburst percentile
    if 'preburst' in args.keys():
        if args['preburst'][0] in ['10%', '25%', '50%', '75%', '90%']:
            preBurst = args['preburst'][0]
        else:
            preBurst = '50%'
    # use ARF for frequent events
    if 'arffreq' in args.keys():
        if args['arffreq'][0].lower() == 'true':
            ARF_frequent = True
        elif args['arffreq'][0].lower() == '':
            ARF_frequent = True
        else:
            ARF_frequent = False
    # Minimum ARF
    if 'minarf' in args.keys():
        min_ARF = float(args['minarf'][0])
    # Loss method
    if 'lossmethod' in args.keys():
        if args['lossmethod'][0] in ['interpolate', 'rahman', 'hill', 'static', '60min', 'interpolate_linear_preburst',
                                     'interpolate_log', 'interpolate_log_preburst']:
            lossMethod = args['lossmethod'][0]
        else:
            lossMethod = 'interpolate'
    # Mean Annual Rainfall
    if 'mar' in args.keys():
        try:
            mar = float(args['mar'][0])
        except:
            #print('MAR value not recognised. Must be greater than 0mm. Using default value of 800mm.')
            logger.warning('MAR value not recognised. Must be greater than 0mm. Using default value of 800mm.')
            mar = 800
    # Static Loss Value
    if 'lossvalue' in args.keys():
        try:
            staticLoss = float(args['lossvalue'][0])
        except:
            #print('Static Loss Value not recognised. Must be greater than 0. Using default of 0')
            logger.warning('Static Loss Value not recognised. Must be greater than 0. Using default of 0')
            staticLoss = 0
    # Additional temporal pattern regions
    if 'addtp' in args.keys():
        if args['addtp'][0] == 'false':
            add_tp = False
        else:
            add_tp = []
            for tp in args['addtp'][0].split(','):
                add_tp.append(tp.strip())
    # coastalme loss method
    if 'coastalme_loss_method' in args.keys():
        if args['coastalme_loss_method'][0] in ['infiltration', 'excess']:
            coastalme_loss_method = args['coastalme_loss_method'][0]
        else:
            coastalme_loss_method = 'infiltration'
    # point temporal pattern
    if 'point_tp' in args.keys():
        if args['point_tp'][0] == 'none':
            point_tp_csv = None
        else:
            point_tp_csv = args['point_tp'][0]
    # areal temporal pattern
    if 'areal_tp' in args.keys():
        if args['areal_tp'][0] == 'none':
            areal_tp_csv = None
        else:
            areal_tp_csv = args['areal_tp'][0]
    # access web / offline mode
    if 'offline_mode' in args.keys():
        if args['offline_mode'][0] == 'true':
            access_web = False
        else:
            access_web = True
    # arr file
    if 'arr_file' in args.keys():
        if args['arr_file'][0] == 'none':
            arr_raw_fname = None
        else:
            arr_raw_fname = args['arr_file'][0]
    # bom file
    if 'bom_file' in args.keys():
        if args['bom_file'][0] == 'none':
            bom_raw_fname = None
        else:
            bom_raw_fname = args['bom_file'][0]
    # user initial loss
    if 'user_initial_loss' in args.keys():
        if args['user_initial_loss'][0] == 'none':
            user_initial_loss = None
        else:
            user_initial_loss = args['user_initial_loss'][0]
    # user continuing loss
    if 'user_continuing_loss' in args.keys():
        if args['user_continuing_loss'][0] == 'none':
            user_continuing_loss = None
        else:
            user_continuing_loss = args['user_continuing_loss'][0]
    # urban initial loss
    if 'urban_initial_loss' in args.keys():
        if args['urban_initial_loss'][0] == 'none':
            urban_initial_loss = None
        else:
            urban_initial_loss = args['urban_initial_loss'][0]
    # urban continuing loss
    if 'urban_continuing_loss' in args.keys():
        if args['urban_continuing_loss'][0] == 'none':
            urban_continuing_loss = None
        else:
            urban_continuing_loss = args['urban_continuing_loss'][0]
    # global continuing loss
    if 'global_continuing_loss' in args.keys():
        if args['global_continuing_loss'][0] == 'true':
            use_global_continuing_loss = True
        else:
            use_global_continuing_loss = False
    # probability neutral losses
    if 'probability_neutral_losses' in args.keys():
        if args['probability_neutral_losses'][0] == 'false':
            probability_neutral_losses = False
        else:
            probability_neutral_losses = True
    # complete storm stuff
    if 'complete_storm' in args.keys():
        if args['complete_storm'][0] == 'true':
            bComplete_storm = True
        else:
            bComplete_storm = False
    if 'preburst_pattern_method' in args.keys():
        preburst_pattern_method = args['preburst_pattern_method'][0]
    if 'preburst_pattern_dur' in args.keys():
        preburst_pattern_dur = args['preburst_pattern_dur'][0]
    if 'preburst_pattern_tp' in args.keys():
        preburst_pattern_tp = args['preburst_pattern_tp'][0]
    if 'preburst_dur_proportional' in args.keys():
        if args['preburst_dur_proportional'][0] == 'true':
            bPreburst_dur_proportional = True
        else:
            bPreburst_dur_proportional = False

    # limb data
    if 'limb' in args.keys():
        if args['limb'][0].lower() == 'none' or args['limb'][0].lower() == 'false':
            limb_data = None
        else:
            limb_data = args['limb'][0].lower()

    # additional temporal patterns
    if 'all_point_tp' in args.keys():
        all_point_tp = True if args['all_point_tp'][0].lower() == 'true' else False
    if 'add_areal_tp' in args.keys():
        add_areal_tp = int(args['add_areal_tp'][0])

    warnings = []

    # BOM Depth Data
    # Open and save raw BOM depth information
    if not os.path.exists(export_path):  # check output directory exists
        os.mkdir(export_path)
    if bom_raw_fname is None:
        bom_raw_fname = os.path.join(export_path, 'data', 'BOM_raw_web_{0}.html'.format(site_name))
    else:
        #print("Using user specified BOM IFD file: {0}".format(bom_raw_fname))
        logger.info("Using user specified BOM IFD file: {0}".format(bom_raw_fname))
    if not os.path.exists(os.path.dirname(bom_raw_fname)):  # check output directory exists
        os.mkdir(os.path.dirname(bom_raw_fname))

    if access_web:
        # opener = urllib2.build_opener()
        # opener.addheaders.append(('Cookie',
        #                           'acknowledgedConditions=true;acknowledgedCoordinateCaveat=true;ifdCookieTest=true'))
        if len(non_stnd_dur) > 0:  # if any non-standard durations, make sure included in web address
            nsd = ''
            for dur, unit in non_stnd_dur.items():
                nsd += 'nsd%5B%5D={0}&nsdunit%5B%5D={1}&'.format(dur, unit[0])

        else:
            nsd = 'nsd[]=&nsdunit[]=m&'
        url = 'http://www.bom.gov.au/water/designRainfalls/revised-ifd/?design=ifds&sdmin=true&sdhr=true&sdday' \
              '=true&{0}coordinate_type=dd&latitude={1}&longitude={2}&user_label=&values=depths&update' \
              '=&year=2016'.format(nsd, abs(latitude), longitude)
        url_frequent = 'http://www.bom.gov.au/water/designRainfalls/revised-ifd/?design=very_frequent&sdmin=true&sdhr' \
                       '=true&sdday=true&{0}coordinate_type=dd&latitude={1}&longitude={2}&user_label=&values=depths&update'\
                       '=&year=2016'.format(nsd, abs(latitude), longitude)
        url_rare = 'http://www.bom.gov.au/water/designRainfalls/revised-ifd/?design=rare&sdmin=true&sdhr=true&sdday=true' \
                   '&{0}&coordinate_type=dd&latitude={1}&longitude={2}&user_label=brisbane&values=depths&update=&year=2016'\
                   .format(nsd, abs(latitude), longitude)
        # urlRequest = urllib2.Request(url, headers={'User-Agent': 'Magic Browser'})
        # urlRequest_frequent = urllib2.Request(url_frequent, headers={'User-Agent': 'Magic Browser'})
        # urlRequest_rare = urllib2.Request(url_rare, headers={'User-Agent': 'Magic Browser'})
        # headers = {
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,  image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        #     'Accept-Encoding': 'gzip', 'Accept-Language': 'en-US,en;q=0.9,es;q=0.8', 'Upgrade-Insecure-Requests': '1',
        #     'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

        # BOM standard
        logger.info('Attempting to access BOM: {0}'.format(url))
        downloader = Downloader(url, headers)
        if downloader.type() == 'Requests':
            logger.info('QGIS libraries not found. Using python requests library to download data. Unable to use any proxy settings in this mode.')
        downloader.download()
        if not downloader.ok():
            logger.error('Failed to get data from BOM website')
            logger.error('HTTP error {0}'.format(downloader.ret_code))
            logger.error(downloader.error_string)
            raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
        page = downloader.data

        # BOM frequent
        if frequent_events:
            logger.info('Attempting to access BOM frequent events: {0}'.format(url_frequent))
            downloader = Downloader(url_frequent, headers)
            downloader.download()
            if not downloader.ok():
                logger.error('Failed to get data from BOM website')
                logger.error('HTTP error {0}'.format(downloader.ret_code))
                logger.error(downloader.error_string)
                raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
            page_frequent = downloader.data

        # BOM rare
        if rare_events:
            logger.info('Attempting to access BOM rare events: {0}'.format(url_rare))
            downloader = Downloader(url_rare, headers)
            downloader.download()
            if not downloader.ok():
                logger.error('Failed to get data from BOM website')
                logger.error('HTTP error {0}'.format(downloader.ret_code))
                logger.error(downloader.error_string)
                raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
            page_rare = downloader.data


        # try:
        #     #print('Attempting to access BOM: {0}'.format(url))
        #     logger.info('Attempting to access BOM: {0}'.format(url))
        #     # f = opener.open(urlRequest)
        #     # page = f.read()
        #     r = requests.get(url, headers=headers)
        #     if not r.ok:
        #         logger.error('Failed to get data from BOM website')
        #         logger.error('HTTP error {0}'.format(r.status_code))
        #         logger.error(r.text)
        #         raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
        #     page = r.text
        #     if frequent_events:
        #         #print('Attempting to access BOM frequent events: {0}'.format(url_frequent))
        #         logger.info('Attempting to access BOM frequent events: {0}'.format(url_frequent))
        #         # f_frequent = opener.open(urlRequest_frequent)
        #         # page_frequent = f_frequent.read()
        #         r = requests.get(url_frequent, headers=headers)
        #         if not r.ok:
        #             logger.error('Failed to get data from BOM website')
        #             logger.error('HTTP error {0}'.format(r.status_code))
        #             logger.error(r.text)
        #             raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
        #         page_frequent = r.text
        #     if rare_events:
        #         #print('Attempting to access BOM rare events: {0}'.format(url_rare))
        #         logger.info('Attempting to access BOM rare events: {0}'.format(url_rare))
        #         # f_rare = opener.open(urlRequest_rare)
        #         # page_rare = f_rare.read()
        #         r = requests.get(url_rare, headers=headers)
        #         if not r.ok:
        #             logger.error('Failed to get data from BOM website')
        #             logger.error('HTTP error {0}'.format(r.status_code))
        #             logger.error(r.text)
        #             raise Exception('Failed to get data from BOM website. Please check logfile for more details.')
        #         page_rare = r.text
        # except:
        #     #print('Failed to get data from BOM website')
        #     logger.error('Failed to get data from BOM website')
        #     logging.shutdown()
        #     raise Exception('Failed to get data from BOM website')

        #print('Saving: {0}'.format(bom_raw_fname))
        logger.info('Saving: {0}'.format(bom_raw_fname))
        try:
            # fo = open(bom_raw_fname, 'wb')
            fo = open(bom_raw_fname, 'w')
        except PermissionError:
            #print("File is locked for editing: {0}".format(bom_raw_fname))
            logger.error("File is locked for editing: {0}".format(bom_raw_fname))
            logging.shutdown()
            raise Exception("ERROR: File is locked for editing: {0}".format(bom_raw_fname))
        except IOError:
            #print("Unexpected error opening file: {0}".format(bom_raw_fname))
            logger.error("Unexpected error opening file: {0}".format(bom_raw_fname))
            logging.shutdown()
            raise Exception("ERROR: Unexpected error opening file: {0}".format(bom_raw_fname))
        fo.write(page)
        if frequent_events:
            fo.write(page_frequent)
        if rare_events:
            fo.write(page_rare)
        # fo.flush()
        fo.close()
        #print('Done saving file.')
        logger.info('Done saving file.')

    # Load BOM file
    Bom = BOM()
    Bom.load(bom_raw_fname, frequent_events, rare_events)
    if Bom.error:
        #print('ERROR: {0}'.format(Bom.message))
        logger.error('ERROR: {0}'.format(Bom.message))
        logging.shutdown()
        raise Exception(Bom.message)

    #print ('Found {0} AEPs and {1} durations in .html file'.format(Bom.naep, Bom.ndur))
    logger.info ('Found {0} AEPs and {1} durations in .html file'.format(Bom.naep, Bom.ndur))

    # save out depth table
    if catchment_area <= 1.0:  # no catchment area, so no ARF. otherwise write out rainfall after ARF applied
        bom_table_fname = os.path.join(export_path, 'data', 'BOM_Rainfall_Depths_{0}.csv'.format(site_name))
        #print('Saving: {0}'.format(bom_table_fname))
        logger.info('Saving: {0}'.format(bom_table_fname))
        Bom.save(bom_table_fname, site_name)
        #print('Done saving file.')
        logger.info('Done saving file.')

    # ARR data
    # Open and save raw ARR information
    areal_tp_download = None
    if arr_raw_fname is None:
        arr_raw_fname = os.path.join(export_path, 'data', 'ARR_Web_data_{0}.txt'.format(site_name))
    else:
        #print("Using user specified ARR datahub file: {0}".format(arr_raw_fname))
        logger.info("Using user specified ARR datahub file: {0}".format(arr_raw_fname))
    if access_web:
        # longitude changed if greater than 153.2999 - set to 153.2999
        # this seems to be a limit for ARR datahub as of June 2019
        # only affects south-eastern most point of qld and north-eatern most point of NSW
        # if longitude > 153.2999:
        #     long_changed = 153.2999
        #     #print('\nWARNING: Longitude changed from {0} to {1}:\n'
        #     #      '   ARR datahub does not support longitudes greater than {1}.\n'
        #     #      '   If this is no longer the case and you would like have this switch removed please contact support@coastalme.com.\n'
        #     #      '   Longitude for BOM IFD extraction has not been altered.\n'.format(longitude, long_changed))
        #     logger.warning('\nWARNING: Longitude changed from {0} to {1}:\n'
        #                    '   ARR datahub does not support longitudes greater than {1}.\n'
        #                    '   If this is no longer the case and you would like have this switch removed please contact support@coastalme.com.\n'
        #                    '   Longitude for BOM IFD extraction has not been altered.\n'.format(longitude, long_changed))
        # else:
        #     long_changed = longitude

        # ARR datahub
        url = 'http://data.arr-software.org/?lon_coord={0}5&lat_coord={1}&type=text&All=1'.format(longitude, -abs(latitude))
        downloader = Downloader(url, headers)
        downloader.download()
        if not downloader.ok():
            logger.error('Failed to get data from ARR website')
            logger.error('HTTP error {0}'.format(downloader.ret_code))
            logger.error(downloader.error_string)
            raise Exception('Failed to get data from ARR website. Please check logfile for more details.')
        arr_page = downloader.data
        logger.info('Saving: {0}'.format(arr_raw_fname))
        try:
            fo = open(arr_raw_fname, 'w')
        except PermissionError:
            # print("File is locked for editing: {0}".format(arr_raw_fname))
            logger.error("File is locked for editing: {0}".format(arr_raw_fname))
            logging.shutdown()
            raise Exception("ERROR: File is locked for editing: {0}".format(arr_raw_fname))
        except IOError:
            # print("Unexpected error opening file: {0}".format(arr_raw_fname))
            logger.error("Unexpected error opening file: {0}".format(arr_raw_fname))
            logging.shutdown()
            raise Exception("ERROR: Unexpected error opening file: {0}".format(arr_raw_fname))
        fo.write(arr_page)
        fo.close()
        logger.info('Done saving file.')

        # Areal Temporal Pattern
        atp_success = False
        if areal_tp_csv is None:
            logger.info('Downloading Areal Temporal Pattern csv...')
            atpRegion = Arr()
            atpRegionCode = atpRegion.arealTemporalPatternCode(arr_raw_fname)
            if atpRegionCode:
                url_atp = 'http://data.arr-software.org//static/temporal_patterns/Areal/Areal_{0}.zip'.format(atpRegionCode)
                logger.info('URL: {0}'.format(url_atp))
                downloader = Downloader(url_atp, headers)
                downloader.download()
                if not downloader.ok():
                    logger.warning("ERROR: failed to download areal temporal pattern.. skipping step. Contact support@coastalme.com\n{0}".format(e))
                else:
                    atp_success = True
        if atp_success:
            z = zipfile.ZipFile(io.BytesIO(downloader.data))
            z.extractall(os.path.join(export_path, "data"))
            atpIncFiles = [x.filename for x in z.filelist]
            atpInc = ""
            for f in atpIncFiles:
                if 'INCREMENTS' in f.upper():
                    atpInc = f
            areal_tp_download = os.path.join(export_path, "data", atpInc)
            if os.path.exists(areal_tp_download):
                logger.info('Areal temporal pattern csv: {0}'.format(areal_tp_download))
            else:
                logger.info('ERROR finding areal temporal pattern csv: {0}'.format(areal_tp_download))
                logger.info('skipping step...')



        # seems to require a dummy browser, or ARR rejects the connection
        # user_agent = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'
        # headers = {'User-Agent': user_agent}

        # request the URL
        # try:
        #     #print('Attempting to access ARR: {0}'.format(url))
        #     logger.info('Attempting to access ARR: {0}'.format(url))
        #     req = urllib2.Request(url, None, headers)
        #     response = urllib2.urlopen(req)
        #     the_page = response.read()
        #     # save the page to file
        #     #print('Saving: {0}'.format(arr_raw_fname))
        #     logger.info('Saving: {0}'.format(arr_raw_fname))
        #     try:
        #         fo = open(arr_raw_fname, 'wb')
        #     except PermissionError:
        #         #print("File is locked for editing: {0}".format(arr_raw_fname))
        #         logger.error("File is locked for editing: {0}".format(arr_raw_fname))
        #         logging.shutdown()
        #         raise Exception("ERROR: File is locked for editing: {0}".format(arr_raw_fname))
        #     except IOError:
        #         #print("Unexpected error opening file: {0}".format(arr_raw_fname))
        #         logger.error("Unexpected error opening file: {0}".format(arr_raw_fname))
        #         logging.shutdown()
        #         raise Exception("ERROR: Unexpected error opening file: {0}".format(arr_raw_fname))
        #     fo.write(the_page)
        #     fo.flush()
        #     fo.close()
        #     #print('Done saving file.')
        #     logger.info('Done saving file.')
        # except urllib2.URLError:
        #     if os.path.exists(arr_raw_fname):
        #         foundTP = False
        #         with open(arr_raw_fname) as fo:
        #             for line in fo:
        #                 if '[STARTPATTERNS]' in line.upper():
        #                     foundTP = True
        #                     break
        #         if foundTP:
        #             #print('WARNING: Could not access ARR website... found and using existing ARR web data {0}'.format(
        #             #    arr_raw_fname))
        #             logger.warning('WARNING: Could not access ARR website... found and using existing ARR web data {0}'.format(
        #                            arr_raw_fname))
        #         else:
        #             #print('Failed to get data from ARR website')
        #             logger.error('Failed to get data from ARR website')
        #             logging.shutdown()
        #             raise Exception('Failed to get data from ARR website')
        #     else:
        #         #print('Failed to get data from ARR website')
        #         logger.error('Failed to get data from ARR website')
        #         logging.shutdown()
        #         raise Exception('Failed to get data from ARR website')

        # if areal_tp_csv is None:
        #     logger.info('Downloading Areal Temporal Pattern csv...')
        #     atpRegion = Arr()
        #     atpRegionCode = atpRegion.arealTemporalPatternCode(arr_raw_fname)
        #     if atpRegionCode:
        #         try:
        #             url_atp = 'http://data.arr-software.org//static/temporal_patterns/Areal/Areal_{0}.zip'.format(atpRegionCode)
        #             logger.info('URL: {0}'.format(url_atp))
        #             r = requests.get(url_atp)
        #             z = zipfile.ZipFile(io.BytesIO(r.content))
        #             z.extractall(os.path.join(export_path, "data"))
        #             atpIncFiles = [x.filename for x in z.filelist]
        #             atpInc = ""
        #             for f in atpIncFiles:
        #                 if 'INCREMENTS' in f.upper():
        #                     atpInc = f
        #             areal_tp_download = os.path.join(export_path, "data", atpInc)
        #             if os.path.exists(areal_tp_download):
        #                 logger.info('Areal temporal pattern csv: {0}'.format(areal_tp_download))
        #             else:
        #                 logger.info('ERROR finding areal temporal pattern csv: {0}'.format(areal_tp_download))
        #                 logger.info('skipping step...')
        #         except Exception as e:
        #             logger.warning("ERROR: failed to download areal temporal pattern.. skipping step. Contact support@coastalme.com\n{0}".format(e))
        #     else:
        #         logger.warning("WARNING: unable to determine areal temporal pattern region... skipping step")
        # else:
        #     logger.warning("WARNING: User specified areal temporal pattern found... skipping areal pattern download")

        if point_tp_csv is None:  # only check if user has not specified temporal patterns manually
            #print('Checking Temporal Pattern Region...')
            logger.info('Checking Temporal Pattern Region...')
            tpRegionCheck = Arr()
            tpRegion = tpRegionCheck.temporalPatternRegion(arr_raw_fname)
            #print(tpRegion)
            logger.info(tpRegion)
            if tpRegion.upper() == 'RANGELANDS WEST AND RANGELANDS':
                #print("Splitting {0} into separate regions: Rangelands West, Rangelands".format(tpRegion))
                logger.info("Splitting {0} into separate regions: Rangelands West, Rangelands".format(tpRegion))
                if not add_tp or'rangelands west' not in add_tp:
                    #print('Adding Rangelands West to additional temporal patterns')
                    logger.info('Adding Rangelands West to additional temporal patterns')
                    if type(add_tp) is bool:
                        add_tp = []
                    add_tp.append("rangelands west")
                else:
                    #print("Rangelands West already selected in additional temporal patterns... skipping")
                    logger.info("Rangelands West already selected in additional temporal patterns... skipping")
                if not add_tp or 'rangelands' not in add_tp:
                    #print('Adding Rangelands to additional temporal patterns')
                    logger.info('Adding Rangelands to additional temporal patterns')
                    if type(add_tp) is bool:
                        add_tp = []
                    add_tp.append("rangelands")
                else:
                    #print("Rangelands already selected in additional temporal patterns... skipping")
                    logger.info("Rangelands already selected in additional temporal patterns... skipping")


        if add_tp != False:
            if len(add_tp) > 0:
                for tp in add_tp:
                    add_tpFilename = os.path.join(export_path, 'data', 'ARR_Web_data_{0}_TP_{1}.txt'.format(site_name, tp))
                    tpCoord = tpRegion_coords(tp)
                    url2 = 'http://data.arr-software.org/?lon_coord={0}5&lat_coord={1}&type=text&All=1' \
                           .format(tpCoord[1], tpCoord[0])

                    try:
                        logger.info('Attempting to access ARR for additional Temporal Pattern: {0}'.format(tp))
                        downloader = Downloader(url2, headers)
                        downloader.download()
                        if not downloader.ok():
                            raise Exception('Download error code: {0}\n{1}'.format(downloader.ret_code, downloader.error_string))
                        the_page = downloader.data
                        # req = urllib2.Request(url2, None, headers)
                        # response = urllib2.urlopen(req)
                        # the_page = response.read()
                    except Exception as e:
                        logger.error(str(e))
                        logger.error('Failed to get data from ARR website')
                        logging.shutdown()
                        raise Exception('Failed to get data from ARR website')

                    #print('Saving: {0}'.format(add_tpFilename))
                    logger.info('Saving: {0}'.format(add_tpFilename))
                    try:
                        fo = open(add_tpFilename, 'w')
                    except PermissionError:
                        #print("File is locked for editing: {0}".format(add_tpFilename))
                        logger.error("File is locked for editing: {0}".format(add_tpFilename))
                        raise Exception("ERROR: File is locked for editing: {0}".format(add_tpFilename))
                    except IOError:
                        #print("Unexpected error opening file: {0}".format(add_tpFilename))
                        logger.error("Unexpected error opening file: {0}".format(add_tpFilename))
                        raise Exception("ERROR: Unexpected error opening file: {0}".format(add_tpFilename))
                    fo.write(the_page)
                    fo.flush()
                    fo.close()
                    #print('Done saving file.')
                    logger.info('Done saving file.')

                    # areal tp
                    logger.info('Downloading areal temporal pattern for: {0}'.format(tp))
                    tpRegionCheck = Arr()
                    tpCode = tpRegionCheck.arealTemporalPatternCode(add_tpFilename)
                    url2 = 'http://data.arr-software.org//static/temporal_patterns/Areal/Areal_{0}.zip'.format(tpCode)
                    downloader = Downloader(url2, headers)
                    downloader.download()
                    if not downloader.ok():
                        logger.warning("ERROR: failed to download areal temporal pattern, error code: {0} - {1}.. skipping step. Contact support@coastalme.com".format(downloader.ret_code, downloader.error_string))
                        continue
                    z = zipfile.ZipFile(io.BytesIO(downloader.data))
                    # req = urllib2.Request(url2, headers=headers)
                    # response = urllib2.urlopen(req)
                    # z = zipfile.ZipFile(io.BytesIO(response.read()))
                    z.extractall(os.path.join(export_path, "data"))
                    atpIncFiles = [x.filename for x in z.filelist]
                    atpInc = ""
                    for f in atpIncFiles:
                        if 'INCREMENTS' in f.upper():
                            atpInc = f
                    areal_csv = os.path.join(export_path, "data", atpInc)
                    if os.path.exists(areal_tp_download):
                        logger.info('Areal temporal pattern csv: {0}'.format(areal_csv))
                    else:
                        logger.info('ERROR finding areal temporal pattern csv: {0}'.format(areal_csv))
                        logger.info('skipping step...')

    # load from file
    settings.preburst_percentile = preBurst
    ARR = Arr()
    try:
        ARR.load(arr_raw_fname, catchment_area, add_tp=add_tp, point_tp=point_tp_csv, areal_tp=areal_tp_csv,
                 user_initial_loss=user_initial_loss, user_continuing_loss=user_continuing_loss,
                 areal_tp_download=areal_tp_download, limb_data=limb_data, add_areal_tp=add_areal_tp)
    except Exception as e:
        logger.error(f"ERROR: Unable to load ARR data: {e}\n{traceback.format_exc()}")
        logging.shutdown()
        raise Exception("ERROR: Unable to load ARR data: {0}".format(e))
    if ARR.error:
        #print('ERROR: {0}'.format(ARR.message))
        logger.error('ERROR: {0}'.format(ARR.message))
        #print("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logger.error("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logging.shutdown()
        raise Exception(ARR.message)

    # loop through each AEP and export
    #print ('Exporting data...\n')
    logger.info('Exporting data...\n')
    # noinspection PyBroadException
    try:
        # Combine standard and non standard durations
        if len(non_stnd_dur) > 0:
            for len_, unit in non_stnd_dur.items():
                conflict = False
                if len_ in duration:
                    conflict = True
                    if duration[len_] == 'm':
                        if len_ / 60. not in duration:
                            duration[len_ / 60.] = 'h'
                            conflict = False
                    elif duration[len_] == 'h':
                        if len_ * 60. not in duration:
                            duration[len_ * 60] = 'm'
                            conflict = False
                if conflict:
                    if unit == 'm':
                        len_ /= 60
                        unit = 'h'
                    elif unit == 'h':
                        len_ *= 60
                        unit = 'm'
                    if len_ not in duration:
                        duration[len_] = unit
                    else:
                        logger.info('ERROR: should not be here - couldn\'t add duration {0}{1} - please contact support@coastalme.com'.format(len_, unit))
                else:
                    duration[len_] = unit

        ARR.export(export_path, aep=AEP, dur=duration, name=site_name, format=out_form, bom_data=Bom, climate_change=cc,
                   climate_change_years=cc_years, cc_rcp=cc_RCP, cc_param=cc_param, area=catchment_area, frequent=frequent_events,
                   rare=rare_events, catch_no=catchment_no, out_notation=output_notation, arf_frequent=ARF_frequent,
                   min_arf=min_ARF, preburst=preBurst, lossmethod=lossMethod, mar=mar, staticloss=staticLoss,
                   add_tp=add_tp, coastalme_loss_method=coastalme_loss_method, urban_initial_loss=urban_initial_loss,
                   urban_continuing_loss=urban_continuing_loss, probability_neutral_losses=probability_neutral_losses,
                   use_complete_storm=bComplete_storm, preburst_pattern_method=preburst_pattern_method,
                   preburst_pattern_dur=preburst_pattern_dur, preburst_pattern_tp=preburst_pattern_tp,
                   preburst_dur_proportional=bPreburst_dur_proportional,
                   use_global_continuing_loss=use_global_continuing_loss,
                   all_point_tp=all_point_tp)
    except Exception as e:
        #print('ERROR: Unable to export data: {0}'.format(e))
        try:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error('ERROR: Unable to export data: {0}'.format(e))
            logger.error("{0}".format(traceback.print_exception(exc_type, exc_value, exc_traceback)))
        finally:
            del exc_type, exc_value, exc_traceback
        #print("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logger.error("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logging.shutdown()
        raise Exception("Unable to export data")

    if ARR.error:
        #print('ERROR: {0}'.format(ARR.message))
        logger.error('ERROR: {0}'.format(ARR.message))
        #print("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logger.error("ERROR: if problem persists please email input files and log.txt to support@coastalme.com.")
        logging.shutdown()
        raise Exception(ARR.message)
    else:
        #print('\nDisclaimer: {0}'.format(disclaimer))
        logger.info('\nDisclaimer: {0}'.format(disclaimer))
        #print('\nSCRIPT FINISHED\n')
        logger.info('\nSCRIPT FINISHED\n')
        logging.shutdown()