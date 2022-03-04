#-*- coding: utf-8 -*-
import os
import time
import json
import hashlib
import datetime

def _t():
    tmp = str(datetime.datetime.now())
    return tmp if len(tmp) >= 26 else tmp + '0' * (26 - len(tmp))

def md5_text(text):
    ctx = hashlib.md5(text)
    return ctx.hexdigest()

def get_dict_of_dir(str_dir, filter_func=None, cc='GBK'):
    pp = {'System Volume Information', '$RECYCLE.BIN'}
    str_dir = str_dir.encode(cc, 'ignore') if isinstance(str_dir, unicode) else str_dir
    if not os.path.isdir(str_dir):
        return {}
    filter_func = filter_func if hasattr(filter_func, '__call__') else lambda f, n: True
    all_files, current_files = {}, os.listdir(str_dir)
    for file_name in current_files:
        if file_name=='.' or file_name=='..':
            continue
        full_name = os.path.join(str_dir, file_name)
        if os.path.isfile(full_name):
            if filter_func(full_name, file_name):
                all_files.setdefault(full_name.decode(cc), file_name.decode(cc))
        elif os.path.isdir(full_name) and file_name not in pp \
            and not file_name.startswith('.') and not file_name.startswith('$'):
            next_files = get_dict_of_dir(full_name, filter_func)
            for n_full_name, n_file_name in next_files.items():
                all_files.setdefault(n_full_name.decode(cc), n_file_name.decode(cc))

    return all_files

def load_json(filename):
    if not os.path.isfile(filename):
        return {}

    try:
        with open(filename, 'r') as rf:
            tmp = rf.read()
            return json.loads(tmp.decode('GBK'))
    except:
        return {}

def dump_json(obj, filename):
    with open(filename, 'w') as wf:
        json.dump(obj, wf, ensure_ascii=False, indent=2)

def byte2size(num, in_tag = '', out_tag = '', dot = 2):
    in_tag, out_tag = in_tag.upper(), out_tag.upper()
    num, dot = float(num), int(dot) if dot > 0 else 0
    tag_map = {'K':1024, 'M':1024*1024, 'G':1024*1024*1024, 'T':1024*1024*1024*1024}
    if in_tag and in_tag in tag_map:
        num = num * tag_map[in_tag]

    zero_str = '.' + ('0' * dot)
    if num < 1024:
        return ('%*.*f' % (7, dot, num)).replace(zero_str, '')
    elif out_tag and out_tag in tag_map:
        tmp = round(num / tag_map[out_tag], dot)
        return ('%*.*f' % (7, dot, tmp)).replace(zero_str, '') + out_tag
    else:
        for key in 'KMGT':
            val = tag_map[key]
            tmp = round(num / val, dot)
            if 1 <= tmp < 1024:
                return ('%*.*f' % (7, dot, tmp)).replace(zero_str, '') + key
        return byte2size(num, '', 'T', dot);

def dump_list(jinfo, filename, with_path = False):
    keys = sorted(jinfo.keys())
    line = ''
    with open(filename, 'w') as wf:
        for k in keys:
            v = jinfo[k]
            ss = byte2size(v['s'])
            ss = (' ' * (8 - len(ss)) + ss) if len(ss) < 8 else ss
            tt = v['t'] + ' '
            if with_path:
                line = '%s\t%s\t%s\t%s\t\t\t#%s' % (v['h'], ss, tt, v['n'], k)
            else:
                line = '%s\t%s\t%s\t%s' % (v['h'], ss, tt, v['n'])
            if line:
                wf.write(line + '\n')

def load_list(filename):
    if not os.path.isfile(filename):
        return []

    lines = []
    try:
        with open(filename, 'r') as rf:
            lines = rf.readlines()
    except:
        return []

    jlist = []
    for line in lines:
        line = line.decode('GBK').strip()
        arr = line.split('\t', 3) if line else []
        if len(arr) != 4:
            continue

        tmp = {
            'h': arr[0].strip(),
            's': arr[1].strip(),
            't': arr[2].strip(),
            'n': arr[3].split('#')[0].strip(),
        }
        jlist.append(tmp)
    return jlist

def finto(full_name, name):
    mt = os.path.getmtime(full_name)
    return {
        'h': md5_text(full_name),
        't': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt)),
        's': os.path.getsize(full_name),
        'n': name,
    }


def main(target, lfile, jfile):
    if not os.path.isdir(target):
        return

    _jinfo = load_json(jfile) if os.path.isfile(jfile) else {}
    print _t(), '[INFO] load_json %s => %s done(%d).' % (target, jfile, len(_jinfo))
    _jlist = load_list(lfile) if os.path.isfile(lfile) else []
    print _t(), '[INFO] load_list %s => %s done(%d).' % (target, jfile, len(_jlist))

    filter_func = lambda full_name, file_name: \
        not file_name.startswith('.') and not file_name.endswith('.torrent') and \
        not full_name.startswith('G:\\tdd')

    print _t(), '[INFO] ==============================='
    _fmap = get_dict_of_dir(target, filter_func=filter_func)
    _tmp = {md5_text(k): (k, v) for k, v in _fmap.items()}
    for i in _jlist:
        h = i['h']
        if h in _tmp and i['n'] != _tmp[h][1]:
            rn = os.path.join(os.path.dirname(_tmp[h][0]), i['n'])
            try:
                if not os.path.isfile(_tmp[h][0]):
                    print _t(), '[WARN] old name %s (%s) non-existent skip.' % (_tmp[h][0], i['s'])
                    continue

                if os.path.isfile(rn):
                    print _t(), '[WARN] new name %s (%s) existent skip.' % (rn, i['s'])
                    continue

                os.rename(_tmp[h][0], rn)
                print _t(), '[INFO] os.rename %s => %s (%s) done.' % (_tmp[h][0], i['n'], i['s'])
            except Exception as ex:
                print _t(), '[ERROR] os.rename %s => %s (%s)\n\t err:%r' % (_tmp[h][0], i['n'], i['s'], ex)

    print _t(), '[INFO] ==============================='

    fmap = get_dict_of_dir(target, filter_func=filter_func)
    jinfo = {k: finto(k, v) for k, v in fmap.items()}

    dump_json(jinfo, jfile)
    print _t(), '[INFO] dump_json %s => %s done(%d).' % (target, jfile, len(jinfo))

    dump_list(jinfo, lfile)
    print _t(), '[INFO] dump_list %s => %s done(%d).' % (target, lfile, len(jinfo))


if __name__ == '__main__':
    cwd = os.getcwd()
    target, lfile, jfile = cwd, os.path.join(cwd, 'filelist.txt'), os.path.join(cwd, 'filelist.json')
    main(target, lfile, jfile)
