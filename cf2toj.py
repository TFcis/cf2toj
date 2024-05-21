import asyncio
import argparse
import json
import logging
import os
import subprocess
import xml.etree.ElementTree as ET
from function import makedirs, copyfile, run_and_wait_process

async def main():
    args_parser = argparse.ArgumentParser(description='cf2toj')
    args_parser.add_argument('inputpath', type=str, help='輸入資料夾')
    args_parser.add_argument('outputpath', type=str, help='輸出資料夾')
    args_parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    args_parser.set_defaults(loglevel=logging.INFO)
    args = args_parser.parse_args()
    inputpath = args.inputpath
    outputpath = args.outputpath

    logging.basicConfig(level=args.loglevel, format='%(asctime)s %(levelname)s %(message)s')

    with open(os.path.join(inputpath, 'problem.xml')) as xml_f:
        xml = ET.parse(xml_f)
        root = xml.getroot()

    conf = {
        'timelimit': 0,
        'memlimit': 0,
        'compile': 'g++',
        'score': 'rate',
        'check': 'diff',
        'test': [],
        'metadata': {}
    }

    conf['timelimit'] = root.find('./judging/testset/time-limit').text
    conf['memlimit'] = int(int(root.find('./judging/testset/memory-limit').text) / 1024)

    makedirs(outputpath, 'res/testdata')

    tasks_group = {}
    cnt = 1
    is_one_group = True
    for test in root.findall("./judging/testset/tests/"):
        g = test.attrib.get('group', 0)
        g_weight = test.attrib.get('points', 0)
        if g != 0:
            is_one_group = False

        if g not in tasks_group:
            tasks_group[g] = {
                'weight': int(float(g_weight)),
                'data': [cnt]
            }
        else:
            tasks_group[g]['weight'] += int(float(g_weight))
            tasks_group[g]['data'].append(cnt)

        cnt += 1

    if is_one_group:
        tasks_group[0]['weight'] = 100

# format_str = "{:0" + str(len(str(cnt)) + 1) + "}"
    format_str = "{:02}"

    for g in tasks_group.values():
        conf['test'].append(g)

        for i in g['data']:
            copyfile(
                (inputpath, 'tests', (format_str + "").format(i)),
                (outputpath, 'res/testdata', "{}.in".format(i)),
            )
            copyfile(
                (inputpath, 'tests', (format_str + ".a").format(i)),
                (outputpath, 'res/testdata', "{}.out".format(i)),
            )

    logging.info('Creating config file')
    with open(os.path.join(outputpath, 'conf.json'), 'w') as conffile:
        json.dump(conf, conffile, indent=4)

    makedirs(outputpath, 'http')
    logging.info('Copying statements')
    statement_path = os.path.join(inputpath, 'statements/.html/chinese')
    if not os.path.exists(statement_path):
        statement_path = os.path.join(inputpath, 'statements/.html/english')

    for filepath in os.listdir(statement_path):
        if filepath == "problem.html":
            copyfile(
                (statement_path, 'problem.html'),
                (outputpath, 'http', 'cont.html')
            )
        else:
            copyfile(
                (statement_path, filepath),
                (outputpath, 'http', filepath),
            )

    subprocess.run(['sed', '-i', "s/background-color: #efefef;//", f'{outputpath}/http/problem-statement.css'])

    logging.info('Compress starting')
    returncode = await run_and_wait_process('tar', *[
        '-C',
        outputpath,
        '-cJf',
        os.path.join(os.path.dirname(outputpath), '{}.tar.xz'.format(os.path.basename(outputpath))),
        'http',
        'res',
        'conf.json',
    ])

    if returncode != 0:
        logging.info('Compress failed')
    else:
        logging.info('Compress successfully')

if __name__ == '__main__':
    asyncio.run(main())
