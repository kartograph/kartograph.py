"""
command line interface for kartograph
"""


def main():
    
    import sys, os, os.path, getopt, json
    import time
    
    start = time.time()
    
    from errors import KartographError
    
    if len(sys.argv) < 2:
        print "try: kartograph generate"
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command in ("generate", "kml", "svg"):
    
        from kartograph import Kartograph
    
        cfg = {}
        output = None
        opts, args = getopt.getopt(sys.argv[2:], 'c:o:', ['config=','output='])
        for o, a in opts:
            if o in ('-c', '--config'):
                opt_src = a
                if os.path.exists(opt_src):
                    t = open(opt_src, 'r').read()
                    if opt_src[-5:].lower() == '.json':
                        cfg = json.loads(t)
                    elif opt_src[-5:].lower() == '.yaml':
                        import yaml
                        cfg = yaml.load(t)
                    else:
                        raise Error('supported config formats are .json and .yaml')
                else:
                    raise Error('config json not found')
            elif o in ('-o', '--output'):    
                output = a
                
        K = Kartograph()
        
        try:
            if command == "kml":
                K.generate_kml(cfg, output)
            else:
                K.generate(cfg, output)
        except KartographError as e:
            print e
    
        elapsed = (time.time() - start)

        print 'execution time: %.4f secs'%elapsed
        sys.exit(0)
    
    
    
    
    elif command == "cartogram":
        
        from cartogram import Cartogram
        
        map = sys.argv[2]
        attr = sys.argv[3]
        data = sys.argv[4]
        key = sys.argv[5]
        val = sys.argv[6]
        
        C = Cartogram()
        C.generate(map,attr,data,key,val)
        
        

if __name__ == "__main__":
    main()