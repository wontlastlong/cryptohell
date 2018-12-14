import securechat
import blom_agreement
import testcryptor
import socket
import sys
import traceback
from select import select

def on_recv(data):
    print data

pub = blom_agreement.BlomPubKey.from_file('node_2.pub')
prv = blom_agreement.BlomPrvKey.from_file('node_2.pub')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((sys.argv[1], int(sys.argv[2])))

try:
    chat = securechat.SecureChat(s, 50, (pub, prv),
        blom_agreement.BlomAgreement, testcryptor.TestCryptor, on_recv, False)
    chat.start()
    
    while chat.running_flag:
        rdy_read, _, _ = select([sys.stdin], [], [], 0.2)
        if rdy_read:
            to_send = raw_input()
            if to_send == ":quit":
                break
            chat.send(to_send)
            
    chat.close()
except:
    print 'meh?'
    sys.stdout.flush()
    chat.close()
    s.close()
    #print str(e)
    traceback.print_exc()

