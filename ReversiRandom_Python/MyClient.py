import sys
import socket
import time
from random import randint
import operator

t1 = 0.0  # the amount of time remaining to player 1
t2 = 0.0  # the amount of time remaining to player 2
class ReversiClient:
    def __init__(self):
        # state[0][0] is the bottom left corner of the board (on the GUI)
        self.state = [[0 for x in range(8)] for y in range(8)]
        self.currRound = 0
        self.player_num = -1
        self.best_move_so_far = {}
        self.target_depth = 3

    # returns the number of the other player
    def get_other_player_num(self, my_player):
        return 2 if my_player == 1 else 1

    # simple board scorer. Score is how many pieces are yours
    # Assumes you want to score yourself
    def rate_state(self, game_state, player_num=None):
        if player_num is None:
            player_num = self.player_num
        score = 0
        for row in range(8):
            for col in range(8):
                if game_state[row][col] == player_num:
                    score += 1
        return score
    
    # changes the state of the board
    def change_state(self, state, move, player_num):
        # do player_num's move
        row = move[0]
        col = move[1]
        state[row][col] = player_num
        # change the state of the board accordingly with the move of player_num
        self.couldBe(row, col, player_num, True, state)
        return state

    # minimax algorithm. Determines the best possible move for our player
    # validMoves: the number of valid moves we have at a given depth
    # tmp_state: the state of the board as we go down the tree looking for the best move
    # max_turn: if we are at a depth where it is time for the Max part of the algorithm
    # mini: the curr minimum
    # maxi: the curr maximum
    # depth_index: the depth we are at in the tree
    def determine_move(self, validMoves, tmp_state, max_turn, mini=0, maxi=0, depth_index=0):
        # Go through each valid move, checking for further valid moves down that "branch"
        if depth_index == self.target_depth or len(validMoves) == 0:
            # rate the state currently and return
            return self.rate_state(tmp_state)

        depth_index += 1
        # set these one first round
        if mini == 0:
            mini = self.rate_state(tmp_state)
        elif maxi == 0:
            maxi = self.rate_state(tmp_state)
        
        # if the depth we are at is MAX
        # this is in dire need of abstraction...but yolo for now
        if max_turn:
            v = mini #TODO evaluate
            for i in range(len(validMoves)):
                # change state of board according to our possible moves
                tmp_state = self.change_state(tmp_state, validMoves[i])
                enemy_moves = self.getValidMoves(state, self.get_other_player_num(self.player_num))
                for j in range(len(enemy_moves)):
                    # change state of board according to enemy possible moves
                    tmp_state = self.change_state(tmp_state, enemy_moves, j) 
                    # get our new possible moves
                    new_moves = self.getValidMoves(self.player_num, state)
                    # Recursion
                    score = self.determine_move(new_moves, tmp_state, v, maxi, depth_index, False)
                    if score > v:
                        v = score
                    if v > maxi:
                        return maxi # TODO will we jump out before tabulating the best moves?
                # if we are at the root then lets look at all the scores of each choice
                if depth_index == 1:
                    self.best_move_so_far[i] = v
                    
            return v # TODO placement of these? even needed?
        # min turn
        else:
            v = maxi
            for i in range(len(validMoves)):
                tmp_state = self.change_state(tmp_state, validMoves[i])
                enemy_moves = self.getValidMoves(state, self.get_other_player_num(self.player_num))
                for j in range(len(enemy_moves)):
                    tmp_state = self.change_state(tmp_state, enemy_moves, j)
                    new_moves = self.getValidMoves(self.player_num, state)
                    # Recursion
                    score = self.determine_move(new_moves, tmp_state, mini, v, depth_index, True)
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
        self.determine_move(validMoves, tmp_state, True)
        best = max(self.best_move_so_far.items(), key=operator.itemgetter(1))[0]
        # best is the index into validMoves of the best move to take
        return best
        

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


    def checkDirection(self, row, col, incx, incy, me, change_board=False, state=None):
        sequence = []
        needs_to_change = False
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
                        # if we need to change the board
                        if change_board:
                            needs_to_change = True 
                        else:
                            return True
                    break
            else:
                if (sequence[i] == 1):
                    count = count + 1
                else:
                    if ((sequence[i] == 2) and (count > 0)):
                        if change_board:
                            needs_to_change = True 
                        else:
                            return True
                    break
        if change_board:
            # self.currRound == 0: # Can't be right TODO
            i = 1
            r = row + incy * i
            c = col + incx * i
            stone_number = state[r][c]
            while (state[r][c] == stone_number):
                state[r][c] = stone_number
                i += 1
                r = row + incy * i
                c = col + incx * i
                
        return False

    # checks all around in all directions from the position of row and col to look for valid moves
    def couldBe(self, row, col, me, change_board=False, state=None):
        couldBe = False
        for incx in range(-1, 2):
            for incy in range(-1, 2):
                if ((incx == 0) and (incy == 0)):
                    continue

                if (self.checkDirection(row, col, incx, incy, me, change_board, state)):
                    if change_board:
                        couldBe = True

        return couldBe

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

    # generates the set of valid moves for the player; 
    # myState: the state to check for valid moves
    # player_num: the player number whose moves we are looking for
    # returns a list of valid moves (validMoves)
    def getValidMoves(self, myState=None, player_num=None):
        if myState is None:
            myState = self.state
        if player_num is None:
            player_num = self.player_num
            
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
                        if (self.couldBe(i, j, player_num)):
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
                validMoves = self.getValidMoves(self.state)
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
