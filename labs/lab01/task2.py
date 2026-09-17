import string

UPPERCASE_CHARS = set(string.ascii_uppercase)
SPECIAL_CHARS = set(string.punctuation)
DIGIT_CHARS = set(string.digits)



pidor = 'plAne'
small = False
big = False

if len(pidor) > 0:
    for i in pidor:
        if i in UPPERCASE_CHARS:
            print ('pidor')
            big =True
            if len(i) >0:
                print ('niga')
if big == False:
    print('hyesos')