import ast, io, sys
class K:
    def __init__(s,*a,**k): pass
    def __getattr__(s,n): return K()
    def __call__(s,*a,**k): return K()
    def __enter__(s): return K()
    def __exit__(s,*a): return False
    def __iter__(s): return iter([K() for _ in range(8)])
    def __bool__(s): return False
for m in ('streamlit','plotly','plotly.graph_objects','plotly.express','streamlit.components.v1'):
    sys.modules.setdefault(m, K())
def yukle(dosya):
    s=io.open(dosya,encoding='utf-8').read()
    tree=ast.parse(s); son=None
    for n in tree.body:
        if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='SAYFALAR': son=n.lineno; break
    NS={'__name__':'olcut'}
    exec(compile('\n'.join(s.splitlines()[:son-1]),'olcut','exec'), NS)
    return NS
LEAF=('protokol','aciklama','olcum','birim','degerlendirme')
def testler(NS):
    out={}
    def yuru(d,yol):
        for k,v in d.items():
            if k.startswith('_'): continue
            if isinstance(v,dict):
                if any(x in v for x in LEAF): out[k]=' > '.join(yol)
                else: yuru(v,yol+[k])
    yuru(NS['TEST_KATALOGU'],[])
    return out
