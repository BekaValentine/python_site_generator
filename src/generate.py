import os
import re
import shutil
import sys

import marko
from bs4 import BeautifulSoup as bs

def markdown_to_html(md):
  return marko.convert(md)

def pretty_html(html):
  return bs(html, features='lxml').prettify()

def extract_metadata(md):
  meta = []
  outlines = []
  for line in md.split('\n'):
    s = line.strip()
    if len(s) > 0 and s[0] == '@':
      mline = parse_metadata_line(s[1:])
      if mline is not None:
        meta.append(mline)
    else:
      outlines.append(s)

  return (dict(meta), '\n'.join(outlines))

def parse_metadata_line(l):
  m = re.match('^(\S+)\s+(\S.*)$', l)
  if not m:
    return None

  return (m.group(1), m.group(2))

def ELEMENT_HEAD(path, meta):
  title = meta.get('title') or path
  # print('FINDME: ', meta)
  NEWLINE = '\n'
  return f'''

<head>
  <title>{title}</title>
  <base href="file:///mount/ultralaser_home/Projects/python_site_engine/out/" />
  <link rel="stylesheet" href="css.css" />
  <!--
    metadata
{
  NEWLINE.join([
    "      " + key + ": " + value for key, value in meta.items()
  ])
}
  -->
</head>

'''

def generate(src_dir_path, dest_dir_path):

  page_index = []

  # walk src and copy files to dest
  # converting md to html
  for root, dirs, files in os.walk(src_dir_path):
    local_root = root[len(src_dir_path):]
    for f in files:
      name, _, ext = f.rpartition('.')
      dest_local_root = f'{dest_dir_path}{local_root}'
      src_file_path = f'{root}/{f}'
      os.makedirs(dest_local_root, exist_ok=True)
      if ext == 'md':
        dest_file_path = f'{dest_local_root}/{name}.html'
        with open(src_file_path, 'r') as src:
          with open(dest_file_path, 'w') as dest:
            path = f'{local_root}/{name}.html'
            meta, md = extract_metadata(src.read())
            page_index.append({
              'path': path,
              'metadata': meta
            })
            dest.write(pretty_html(ELEMENT_HEAD(path, meta) + '<div id="content">' + markdown_to_html(md) + '</div>'))
      else:
        dest_file_path = f'{dest_local_root}/{f}'
        shutil.copy(src_file_path, dest_file_path)

  # generate an index page
  index_lines = []
  for page in sorted(page_index, key=lambda p: p['path']):
    path = page['path'][1:]
    title = page['metadata'].get('title') or path
    date = page['metadata'].get('date') or '1970-01-01'
    if 'tags' in page['metadata']:
      tags = '\n- tags: ' + page['metadata']['tags']
    else:
      tags = ''
    index_lines.append(f'{date}: [{title}]({path}){tags}')
    index_lines.append('')

  index_path = f'{dest_dir_path}/index.html'
  with open(index_path, 'w') as dest:
    dest.write(pretty_html(ELEMENT_HEAD(path, { **meta, 'title': 'index' }) + '<div id="content">' +  markdown_to_html('\n'.join(index_lines)) + '</div>'))


if __name__ == '__main__':

  if len(sys.argv) != 3:
    print('please provide a source directory and destination directory')
    exit()

  src = os.path.abspath(sys.argv[1])
  dest = os.path.abspath(sys.argv[2])

  if not os.path.isdir(src):
    print(f'{src} is not a directory')
    exit()

  if not os.path.isdir(dest):
    print(f'creating destination directory {dest}')
    os.makedirs(dest, exist_ok=True)

  generate(src, dest)
