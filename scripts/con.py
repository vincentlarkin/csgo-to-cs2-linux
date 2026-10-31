# Send console commands to CS2 (-netconport 2121) and print what comes back.
import socket,sys,time
s=socket.create_connection(('127.0.0.1',2121)); s.settimeout(0.5)
wait=float(sys.argv[1]); out=b''
for c in sys.argv[2:]:
    s.sendall((c+'\n').encode()); time.sleep(0.3)
end=time.time()+wait
while time.time()<end:
    try:
        d=s.recv(65536)
        if not d: break
        out+=d
    except socket.timeout: pass
print(out.decode('utf8','replace')[-6000:])
