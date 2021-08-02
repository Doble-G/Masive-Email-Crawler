
import requests
import urllib3
import re
import tldextract
import threading


#change for have less or more threads 
THREADS=20
#file with direccionts web
DOMAIN_FILE="domain.txt"
#file to writes mails
MAIL_FILE="mails.txt"



LOCK=threading.Lock()
"""
Function that gets a xml from a web
@param web : example https://ww.google.es
return xml as string
"""
def get_string_from_web(web):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    try:
        return requests.get(web,verify=False).text
    except:
        try:
            return requests.get("http://"+web,verify=False).text
        except:
            try:
                return requests.get("https://"+web,verify=False).text
            except:
                return ""
"""
Function gets all webs in a content of string
@param string : string 
return list of webs
"""    
def get_all_webs_from_string(string):
    return get_all_matches_from_string(r'(https+:[/][/]www.)([a-z]|[A-Z]|[0-9]|[/.]|[~])*',string)

"""
Function gets all mails in a content of string
@param string : string 
return list of mails
""" 
def get_all_mail_from_string(string):
    return get_all_matches_from_string(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""",string)

"""
Function gets all matches in a content of string
@param pattern : pattern to match
@param string : string to process
return list of maches
""" 
def get_all_matches_from_string(pattern,string):
    pattern=re.compile(pattern)
    out=[]
    pos=0
    while True:
        match = pattern.search(string, pos)
        if not match:
            break
        s = match.start()
        e = match.end()
        out.append(string[s:e])
        # Move forward in text for the next search
        pos = e
    return out
"""
Function that gets the domain fo a web
@param web : web that is going to process as string
return domain
"""
def get_domain_in_web(web):
    extracted=tldextract.extract(web)
    try:
        return extracted[1]
    except:
        return None
"""
Function that gets all mails in a web and subdomains linked
@param web : web that is going to process
return list all mails
"""

def process_web(web):
    links=[]
    links.append(web)
    mails=[]
    domain=get_domain_in_web(web)
    links_to_process=[]
    links_to_process.append(web)
    links.append(web)
    while links_to_process!=[]:
        aux=[]
        for web in links_to_process:
            string_web=get_string_from_web(web)
            if string_web=="":
                break
            links_in_web=get_all_webs_from_string(string_web)
            for i in links_in_web:
                if i not in links and domain==get_domain_in_web(i):
                    links.append(i)
                    aux.append(i)
            
            mails_web=get_all_mail_from_string(string_web)
            for i in mails_web:
                if not i in mails:
                    mails.append(i)             
        links_to_process=aux    
    return mails

"""
Splits a list in n parts of same size
"""
def split_list_n_parts(list_in,n):
    z=int(len(list_in)/n)+1 
    return [list_in[i:i + z] for i in range(0, len(list_in),z)]
"""
Process a list of domains
"""
def process(list_domains):
    for i in list_domains:
        mails=process_web(i)
        write_mails(mails)
"""
Write mails in MAIL_FILE
"""
def write_mails(mails):
    global LOCK
    if mails!=[]:
        LOCK.acquire()
        with open(MAIL_FILE, 'a') as file:
            for i in mails:
                file.write(i+"\n")
        LOCK.release()
if __name__=="__main__":
    data=[]
    with open(DOMAIN_FILE, "r") as file:
        data=file.read().split("\n")
    parts=split_list_n_parts(data,THREADS)
    tread=[]
    for i in parts:
        t = threading.Thread(target=process, args=(i,))
        t.start()
        tread.append(t)
    for n in tread:
        n.join()
    