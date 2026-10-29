import json,re,sys
def load(p):
    t=open(p,encoding='utf-8').read()
    t=re.sub(r'^\s*/\*.*?\*/\s*','',t,flags=re.S)
    return json.loads(t)
if __name__=='__main__':
    print(json.dumps(load(sys.argv[1]),indent=1,ensure_ascii=False))
