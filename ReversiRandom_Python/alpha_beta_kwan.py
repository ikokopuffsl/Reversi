
import sys
import socket
import time
from random import randint

t1 = 0.0    # the amount of time remaining to player 1
t2 = 0.0    # the amount of time remaining to player 2

ROW = 8
COL = 8
state = [[0 for x in range(ROW)] for y in range(COL)] # state[0][0] is the bottom left corner of the board (on the GUI)

# You should modify this function
# validMoves is a list of valid locations that you could place your "stone" on this turn
# Note that "state" is a global variable 2D list that shows the state of the game
def move(validMoves, me):
    # just return a random move
    myMove = randint(0,len(validMoves)-1)

    # # empty
    # if not validMoves:
        




    return myMove

#establishes a connection with the server
def initClient(me,thehost):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_address = (thehost, 3333+me)
    print >> sys.stderr, 'starting up on %s port %s' % server_address
    sock.connect(server_address)
    
    info = sock.recv(1024)
    
    print info

    return sock

# reads messages from the server
def readMessage(sock):
    mensaje = sock.recv(1024).split("\n")
    #print mensaje

    turn = int(mensaje[0])
    print "Turn: " + str(turn)

    if (turn == -999):
        time.sleep(1)
        sys.exit()

    round = int(mensaje[1])
    print "Round: " + str(round)
    t1 = float(mensaje[2])  # update of the amount of time available to player 1
    #print t1
    t2 = float(mensaje[3])  # update of the amount of time available to player 2
    #print t2

    count = 4
    for i in range(ROW):
        for j in range(COL):
            state[i][j] = int(mensaje[count])
            count = count + 1
        print state[i]

    return turn, round

def checkDirection(row,col,incx,incy,me):
    sequence = []
    for i in range(1,ROW):
        r = row+incy*i
        c = col+incx*i
    
        if ((r < 0) or (r > (ROW - 1)) or (c < 0) or (c > (COL - 1))):
            break

        sequence.append(state[r][c])

    count = 0
    for i in range(len(sequence)):
        if (me == 1):
            if (sequence[i] == 2):
                count = count + 1
            else:
                if ((sequence[i] == 1) and (count > 0)):
                    return True
                break
        else:
            if (sequence[i] == 1):
                count = count+ 1
            else:
                if ((sequence[i] == 2) and (count > 0)):
                    return True
                break
    
    return False

def couldBe(row, col, me):
    for incx in range(-1,2):
        for incy in range(-1,2):
            if ((incx == 0) and (incy == 0)):
                continue

            if (checkDirection(row,col,incx,incy,me)):
                return True

    return False

# generates the set of valid moves for the player; returns a list of valid moves (validMoves)
def getValidMoves(round, me):
    validMoves = []
    print "Round: " + str(round)
    
    for i in range(ROW):
        print state[i]

    if (round < 4):
        print "ROW // 2"
        print ROW//2
        if (state[(ROW//2)-1][(COL//2)-1] == 0):
            validMoves.append([(ROW//2)-1, (COL//2)-1])
        if (state[(ROW//2)-1][(COL//2)] == 0):
            validMoves.append([(ROW//2)-1,(COL//2)])
        if (state[(ROW//2)][(COL//2)-1] == 0):
            validMoves.append([(ROW//2), (COL//2)-1])
        if (state[(ROW//2)][(COL//2)] == 0):
            validMoves.append([(ROW//2), (COL//2)])
    else:
        for i in range(ROW):
            for j in range(COL):
                if (state[i][j] == 0):
                    if (couldBe(i, j, me)):
                        validMoves.append([i, j])

    return validMoves


# main function that (1) establishes a connection with the server, and then plays whenever it is this player's turn
def playGame(me, thehost):
    
    # create a random number generator
    
    sock = initClient(me, thehost)
    
    while (True):
        print("STATE")
        print(state)
        print("ME")
        print(me)
        print "Read"
        status = readMessage(sock)
    
        if (status[0] == me):
            print "Move";
            validMoves = getValidMoves(status[1], me)
            print validMoves
            
            myMove = move(validMoves, me)
        
            sel = str(validMoves[myMove][0]) + "\n" + str(validMoves[myMove][1]) + "\n";
            print "<" + sel + ">"
            sock.send(sel);
            print "sent the message"
        else:
            print "It isn't my turn"


    return



# call: python RandomGuy.py [ipaddress] [player_number]
#   ipaddress is the ipaddress on the computer the server was launched on.  Enter "localhost" if it is on the same computer
#   player_number is 1 (for the black player) and 2 (for the white player)
if __name__ == "__main__":

    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)

    print str(sys.argv[1])
    
    playGame(int(sys.argv[2]), sys.argv[1])

