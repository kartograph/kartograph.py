"""
command line interface for kartograph
"""


def main():
	
	import sys, os, os.path, getopt, json
	import time
	
	start = time.time()
	
	from kartograph import Kartograph
	from errors import KartographError
	
	if len(sys.argv) < 2:
		print "try: kartograph generate"
		sys.exit(1)
	
	command = sys.argv[1]
	
	if command == "generate":
		cfg = {}
		output = None
		opts, args = getopt.getopt(sys.argv[2:], 'c:o:', ['config=','output='])
		for o, a in opts:
			if o in ('-c', '--config'):
				opt_src = a
				if os.path.exists(opt_src):
					t = open(opt_src, 'r').read()
					cfg = json.loads(t)
				else:
					raise Error('config json not found')
			elif o in ('-o', '--output'):	
				output = a
				
		K = Kartograph()
		
		try:
			K.generate(cfg, output)
		except KartographError as e:
			print e
	
		elapsed = (time.time() - start)

		print 'execution time: %.4f secs'%elapsed
		
		sys.exit(0)

if __name__ == "__main__":
    main()