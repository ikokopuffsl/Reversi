import sys
import socket
import time
from random import randint

t1 = 0.0  # the amount of time remaining to player 1
t2 = 0.0  # the amount of time remaining to player 2
class ReversiClient:
    def __init__(self):
        # state[0][0] is the bottom left corner of the board (on the GUI)
        self.state = [[0 for x in range(8)] for y in range(8)]
        self.currRound = 0
        self.player_num = -1
        self.best_move_so_far = {}
        self.target_depth = 5

    # simple board scorer. Score is how many pieces are yours
    def rate_state(self, game_state):
        score = 0
        for row in game_state:
            for col in game_state:
                if game_state[row][col] == self.player_num:
                    score += 1
        return score
            
    # minimax algorithm
    def determine_move(self, validMoves, tmp_state, max_turn, mini=0, maxi=0, depth_index=0):
        # Go through each valid move, checking for further valid moves down that "branch"
        if depth_index == self.target_depth or len(validMoves) == 0:
            # rate the state currently and return
            return rate_state(tmp_state)
        
        # TODO Need to pretend enemy moves
        
        # get new moves
        # change state here
        tmp_state[validMoves[i][0]][validMoves[i][1]] = self.player_num
        new_moves = self.getValidMoves(self.player_num, tmp_state)
        depth_index += 1
        # if the depth we are at is MAX
        if max_turn:
            v = mini
            for i in range(len(validMoves)):
                # Recursion
                score = self.determine_move(new_moves, tmp_state, depth_index, False)
                if score > v:
                    v = score
                if v > maxi:
                    return maxi
            return v
        # min turn
        else:
            v = maxi
            for i in range(len(validMoves)):
                # Recursion
                score = self.determine_move(new_moves, tmp_state, depth_index, True)
                if score < v:
                    v = score
                if v < mini:
                    return mini
            return v
    
    # You should modify this function
    # validMoves is a list of valid locations that you could place your "stone" on this turn
    # Note that "state" is a global variable 2D list that shows the state of the game
    def move(self, validMoves):
        # just return a random move if we are in the first 4 rounds
        if self.currRound < 4:
            myMove = randint(0, len(validMoves) - 1)
            return myMove
        # else determine  the correct move
        tmp_state = self.state.copy()
        scores = []
        scores = self.determine_move(validMoves, tmp_state, True)
        # check minimax and return best move

    # establishes a connection with the server
    def initClient(self, me, thehost):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (thehost, 3333 + me)
        print('starting up on %s port %s' % server_address, file=sys.stderr)
        sock.connect(server_address)

        info = sock.recv(1024)

        print(info)

        return sock


    # reads messages from the server
    def readMessage(self, sock):
        message = sock.recv(1024).decode("utf-8").split("\n")
        # print(message)

        turn = int(message[0])
        print("Turn: " + str(turn))

        if (turn == -999):
            time.sleep(1)
            sys.exit()

        self.currRound = int(message[1])
        print("Round: " + str(self.currRound))
        # t1 = float(message[2])  # update of the amount of time available to player 1
        # print t1
        # t2 = float(message[3])  # update of the amount of time available to player 2
        # print t2

        count = 4
        for i in range(8):
            for j in range(8):
                self.state[i][j] = int(message[count])
                count = count + 1
            print(self.state[i])

        return turn, self.currRound


    def checkDirection(self, row, col, incx, incy, me):
        sequence = []
        for i in range(1, 8):
            r = row + incy * i
            c = col + incx * i

            if ((r < 0) or (r > 7) or (c < 0) or (c > 7)):
                break

            sequence.append(self.state[r][c])

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
                    count = count + 1
                else:
                    if ((sequence[i] == 2) and (count > 0)):
                        return True
                    break

        return False


    def couldBe(self, row, col, me):
        for incx in range(-1, 2):
            for incy in range(-1, 2):
                if ((incx == 0) and (incy == 0)):
                    continue

                if (self.checkDirection(row, col, incx, incy, me)):
                    return True

        return False

    # return the beginning moves


    def check_beginning_moves(self, validMoves):
        if (self.state[3][3] == 0):
            validMoves.append([3, 3])
        if (self.state[3][4] == 0):
            validMoves.append([3, 4])
        if (self.state[4][3] == 0):
            validMoves.append([4, 3])
        if (self.state[4][4] == 0):
            validMoves.append([4, 4])

    # generates the set of valid moves for the player; returns a list of valid moves (validMoves)


    def getValidMoves(self, me, myState=None):
        if myState == None:
            myState = self.state
        validMoves = []
        print("Round: " + str(self.currRound))

        for i in range(8):
            print(myState[i])

        if (self.currRound < 4):
            self.check_beginning_moves(validMoves)
        else:
            for i in range(8):
                for j in range(8):
                    if (myState[i][j] == 0):
                        if (self.couldBe(i, j, self.player_num)):
                            validMoves.append([i, j])

        return validMoves


    # main function that (1) establishes a connection with the server, and then plays whenever it is this player's turn
    # noinspection PyTypeChecker
    def playGame(self, thehost):
        # create a random number generator

        sock = self.initClient(self.player_num, thehost)

        while (True):
            print("Read")
            status = self.readMessage(sock)
            self.currRound = status[1]
            if (status[0] == self.player_num):
                print("Move")
                validMoves = self.getValidMoves(self.player_num)
                print(validMoves)

                myMove = self.move(validMoves)

                sel = str(validMoves[myMove][0]) + "\n" + \
                    str(validMoves[myMove][1]) + "\n"
                print("<" + sel + ">")
                sock.send(sel.encode("utf-8"))
                print("sent the message")
            else:
                print("It isn't my turn")


# call: python RandomGuy.py [ipaddress] [player_number]
# ipaddress is the ipaddress on the computer the server was launched on.  Enter "localhost" if it is on the same computer
# player_number is 1 (for the black player) and 2 (for the white player)
if __name__ == "__main__":
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))
    client = ReversiClient()
    print(str(sys.argv[1]))
    client.player_num = int(sys.argv[2])
    client.playGame(sys.argv[1])
