# Run a command under a pseudo-terminal and save everything it prints. Usage: ptyrun.py <logfile> <cmd...>
import pty,sys,os
log=open(sys.argv[1],'wb')
def rd(fd):
    d=os.read(fd,65536); log.write(d); log.flush(); return d
def inp(fd):
    return b''
st=pty.spawn(sys.argv[2:],rd,inp)
sys.exit(os.waitstatus_to_exitcode(st))
