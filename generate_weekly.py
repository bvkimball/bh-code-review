#!/usr/bin/env python
import shutil, git, re, pystache
import codecs
from datetime import date, timedelta

GIT_DIR = "/home/jweede/bh/coldfusion"
template_name = "weekly_review"

nginx_dir = "/usr/share/nginx/www/" # make sure you fix permissions or run as root

rev_re    = re.compile(r'^\s*commit\s+([0-9a-f]+)\s*')
author_re = re.compile(r'^\s*[Aa]uthor: (.*<.*@.*>)')

def get_revs_from_git( since_date, git_dir=GIT_DIR):
    g = git.Git(git_dir)
    log_output = g.log("--remotes","--pretty=full","--since=%s" % since_date).decode('ascii', 'ignore')
    #extract revs
    revs = []
    for line in log_output.split('\n'):
        m = rev_re.match(line)
        m_author = author_re.match(line)
        if m:
            revs.append({'commit': m.group(1)
                        ,'log': line + '\n'
                        })
        else:
            revs[-1]['log'] += line + '\n'
        if m_author:
            revs[-1]['author'] = m_author.group(1)
    return revs
            
    # print revs
    # return { 'raw_log': log_output.split(rev_re)
           # , 'revs':revs }

def generate_review_page_from_revs( revs_obj, since_date ):
    templ_vals = {'today': date.today().isoformat()
                 ,'since_date': since_date
                 ,'revs': revs_obj
                 ,'revs_count': len(revs_obj)
                 }
    mustache_name = '%s.html.mustache' % template_name
    output_name   = '%s.html' % template_name

    with codecs.open(mustache_name,'r','utf-8') as templatef, codecs.open(output_name,'w','utf-8') as outputf:
        outputf.write( pystache.render(templatef.read(), templ_vals) )

def copy_output_to_nginx():
    shutil.copy('%s.html' % template_name, nginx_dir)

if __name__ == '__main__':
    # We run ours every thursday.
    last_thursday = (date.today() - timedelta(weeks=1)).isoformat()
    revs_obj = get_revs_from_git( last_thursday )
    
    generate_review_page_from_revs( revs_obj, last_thursday )

    copy_output_to_nginx()
