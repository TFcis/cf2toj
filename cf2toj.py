import asyncio
import argparse
import json
import logging
import os
import subprocess
import xml.etree.ElementTree as ET
import collections

from function import makedirs, copyfile, rmdir, run_and_wait_process

def replace_in_file(file_path, search_text, replace_text):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        content = content.replace(search_text, replace_text)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except FileNotFoundError:
        logging.warning(f"File not found: {file_path}")
    except Exception as e:
        logging.error(f"An error occurred while processing the file {file_path}: {str(e)}")

async def main():
    args_parser = argparse.ArgumentParser(description='cf2toj')
    args_parser.add_argument('inputpath', type=str, help='輸入資料夾')
    args_parser.add_argument('outputpath', type=str, help='輸出資料夾')
    args_parser.add_argument('-d', '--debug', action='store_const', dest='loglevel', const=logging.DEBUG)
    args_parser.add_argument('-c', '--clear-output-directory', action='store_const', dest='is_clear_output_dir', const=True, help='壓縮完成後刪除輸出資料夾')
    args_parser.set_defaults(loglevel=logging.INFO)
    args = args_parser.parse_args()
    inputpath = args.inputpath
    outputpath = args.outputpath

    logging.basicConfig(level=args.loglevel, format='%(asctime)s %(levelname)s %(message)s')

    with open(os.path.join(inputpath, 'problem.xml'), encoding='utf-8') as xml_f:
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

    tasks_group = collections.OrderedDict()
    groups_enabled = root.find('./judging/testset/groups/') is not None
    if groups_enabled:
        for group in root.findall('./judging/testset/groups/'):
            group_name = group.attrib.get('name')
            group_points = int(float(group.attrib.get('points', 0)))

            tasks_group[group_name] = {
                'weight': group_points,
                'remap': []
            }
    else:
        tasks_group[0] = {
            'weight': 0,
            'remap': []
        }

    for idx, test in enumerate(root.findall("./judging/testset/tests/")):
        g = test.attrib.get('group', 0)

        tasks_group[g]['remap'].append(idx + 1)

    if not groups_enabled:
        tasks_group[0]['weight'] = 100

    format_str = "{:02}"

    dst = 1
    for _, g in tasks_group.items():
        g['data'] = []
        for src in g['remap']:
            copyfile(
                (inputpath, 'tests', format_str.format(src)),
                (outputpath, 'res/testdata', "{}.in".format(dst)),
            )

            copyfile(
                (inputpath, 'tests', format_str.format(src) + ".a"),
                (outputpath, 'res/testdata', "{}.out".format(dst)),
            )
            g['data'].append(dst)
            dst += 1

        del g['remap']
        conf['test'].append(g)

    logging.info('Creating config file')
    with open(os.path.join(outputpath, 'conf.json'), 'w', encoding='utf-8') as conffile:
        json.dump(conf, conffile, indent=4, ensure_ascii=False)

    makedirs(outputpath, 'http')
    logging.info('Copying statements')

    statement_path = ''
    for statement in root.findall('./statements/'):
        if statement.attrib.get('type', '') == 'text/html':
            statement_path = statement.attrib.get('path', '')

    if statement_path:
        statement_path = statement_path[:-13]  # 去除 '/problem.html'
        statement_path = os.path.join(inputpath, statement_path)

        if os.path.exists(statement_path):
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
            
            # 使用 Python 替代 sed 命令来替换 CSS 文件中的内容
            replace_in_file(f'{outputpath}/http/problem-statement.css', "background-color: #efefef;", "")
        else:
            logging.warning('No statement found at path: {}'.format(statement_path))
    else:
        logging.warning('No statement path defined in problem.xml')

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

    if args.is_clear_output_dir:
        logging.info('Deleting output directory')
        rmdir(outputpath)

if __name__ == '__main__':
    asyncio.run(main())
