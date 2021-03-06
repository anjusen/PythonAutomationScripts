?   script.py C:\Python27\script.py    0   D:\Profiles\twvx38\AppData\Local\Temp\script.py ?  #!/usr/bin/python
import sys
import re

def main():
  if len(sys.argv) >= 3:
    infn = sys.argv[1]
    outfn = sys.argv[2]
    print 'Reading spec from', infn, 'and parsing it to requirements list:', outfn    
    
    inf =  open(infn, 'r')
    outf =  open(outfn, 'w')    
    
    count = 0
    suspiciousReqs = []
    prevReq = '';
    for line in inf:
      repetitions = re.findall('(?P<req>DIG-[\d\-\.]+)', line)
      if repetitions != None and len(repetitions) > 0:
        for r in repetitions:
          if len(r) - len(prevReq) > 1:
            end = r[len(prevReq):]
            if not end.startswith('.'):
              lastDot = r.rfind('.')
              lastMin = r.rfind('-')
              last = max(lastDot, lastMin)
              if last > 0:
                if len(r[last + 1:]) > 3:
                  suspiciousReqs.append(r)
          count += 1
          outf.write(r + ';\r\n')
          prevReq = r
      
    inf.close()
    outf.close()
    print count, " requirements found"
    print "Please check following requirements, which look suspicious:"
    for req in suspiciousReqs:
      print '\t', req
  els