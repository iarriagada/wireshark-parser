#!/usr/bin/env python3

import sys
import os
import re
import argparse
from datetime import datetime
import numpy as np
from chanMonitor import plotEpicsData as ped

id_filt = re.compile(r'^[ ]*([0-9]+) ')
ts_filt = re.compile(r'[0-9]{4}(-[0-9]{2}){2} [0-9]{2}(:[0-9]{2}){2}.[0-9]{6}')
search_filt = re.compile(r'Search\(')
# reply_filt = re.compile(r'(\(13\)|Reply\(1\))[^R]+Reply\(1\)')
reply_filt = re.compile(r'Reply\(1\)')
seq_filt = re.compile(r'Seq=202 Ack=146')
ts_format = '%Y-%m-%d %H:%M:%S.%f'

def parse_args():
    '''
    This routines parses the arguments used when running this script
    '''
    parser = argparse.ArgumentParser(
        description='Parse txt file generated by Wireshark capture')

    parser.add_argument('ws_txt_cap',
                        metavar='Wireshark-txt',
                        nargs='*',
                        help='path to txt file generated by Wireshark')

    # parser.add_argument('-st',
                           # '--starttime',
                           # dest='stime',
                           # default=None,
                           # help='Plot range start time, eg. 210111T2130')

    # parser.add_argument('-et',
                           # '--endtime',
                           # dest='etime',
                           # default=None,
                           # help='Plot range end time, eg. 210111T2315')

    # parser.add_argument('-lc',
                        # '--list-channels',
                        # dest='list_chan',
                        # action='store_true',
                        # help='List channel names contained in data file')

    # parser.add_argument('-hst',
                        # '--histogram',
                        # dest='hst',
                        # action='store_true',
                        # help='Use this option to plot In Pos Duration Histogram')

    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    search_flag = False
    ack_flag = False
    reply_flag = False
    request_ca_time = []
    request_ca_id = []
    reply_ca_time = []
    reply_ca_id = []
    seq_ca_time = []
    seq_ca_id = []
    lost_req_id = []
    lost_req_no = []
    # ws_cap_file = 'tim-capture-text-full.txt'
    ws_cap_file = args.ws_txt_cap
    i = 1
    for cap_file in ws_cap_file:
        with open(cap_file,'r') as f:
            ws_cap_data = f.readlines()

    for l in ws_cap_data:
        if not(search_filt.search(l)
               or reply_filt.search(l)
               or seq_filt.search(l)):
            continue
        if search_filt.search(l) and search_flag:
            continue
        if reply_filt.search(l) and not(search_flag):
            continue
        if seq_filt.search(l) and not(search_flag):
            continue
        ts_str = ts_filt.search(l).group(0)
        pkg_ts = datetime.strptime(ts_str, ts_format).timestamp()
        pkg_id = id_filt.search(l).group(1)
        if search_filt.search(l) and not(search_flag):
            if not(ack_flag) and lost_req_id:
                lost_req_id.append(request_ca_id.pop())
                lost_req_no.append(i)
                request_ca_time.pop()
                reply_ca_id.pop()
                reply_ca_time.pop()
            request_ca_id.append(pkg_id)
            request_ca_time.append(pkg_ts)
            search_flag = True
            ack_flag = False
            reply_flag = False
            print(f"********* {i} *************")
            print(l, end='')
            i += 1
            continue
        if reply_filt.search(l) and search_flag and not(reply_flag):
            reply_ca_id.append(pkg_id)
            reply_ca_time.append(pkg_ts)
            reply_flag = True
            # search_flag = False
            print(l, end='')
            continue
        seq_ca_id.append(pkg_id)
        seq_ca_time.append(pkg_ts)
        print(l, end='')
        search_flag = False
        ack_flag = True
        reply_flag = False

    print(f"Search flag: {search_flag}")
    print(f"req len:{len(request_ca_time)}")
    print(f"reply len:{len(reply_ca_time)}")
    print(f"seq len:{len(seq_ca_time)}")
    if search_flag:
        del(request_ca_id[-1])
        del(request_ca_time[-1])
    ca_response_time = list(np.subtract(reply_ca_time,request_ca_time))
    ca_full_pkg_time = list(np.subtract(seq_ca_time,request_ca_time))
    ca_response_sample = list(range(len(ca_response_time)))
    ca_response_plt = ped.DataAxePlotter(1)
    ca_response_plt.Axe['c1']['g1'] = ped.DataAx([ca_response_sample,
                                                  ca_response_time],
                                                 'r',
                                                 marker='*',
                                                 rawx=True)
    ca_response_plt.Axe['c1']['g2'] = ped.DataAx([ca_response_sample,
                                                  ca_full_pkg_time],
                                                 'g',
                                                 marker='o',
                                                 rawx=True)
    ca_response_plt.positionPlot()
    ca_response_plt.plotConfig()





