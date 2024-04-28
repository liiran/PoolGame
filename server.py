import sys
import cgi
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import Physics
import random
import json

playerNames = []
gameName = "Pool Game"

class MyHandler(BaseHTTPRequestHandler):
    currentTable = None
    currentPlayer = None
    condition = False
    winner = None

    def do_GET(self):

        # parse the URL to get the path and form data
        parsed = urlparse(self.path)
        pathQuery = parsed.path
        
        # check if the web-pages matches the list
        if pathQuery == "/":

            # retreive the HTML file
            with open("index.html", "r") as fp:
                content = fp.read()
            
            # print(f"Requested path: {pathQuery}")

            # generate the headers
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(content))
            self.end_headers()

            # send it to the broswer
            self.wfile.write(bytes(content, "utf-8"))
            fp.close()

        # check if the web-pages matches the list
        elif pathQuery == "/pool.html":
            
            with open("pool.html", "r") as fp:
                content = fp.read()
            
            if MyHandler.currentTable:
                poolTable = MyHandler.currentTable.svg()
                svgContent = content.replace('<!-- SVG_PLACEHOLDER -->', poolTable)

                # replace player names with comments
                svgContent = svgContent.replace('<!-- Player One -->', playerNames[0])
                svgContent = svgContent.replace('<!-- Player Two -->', playerNames[1])
                svgContent = svgContent.replace('<!-- Current Player -->', "Current Turn: " + MyHandler.currentPlayer)

            # send it to the broswer
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(svgContent))
            self.end_headers()

            # send it to the broswer
            self.wfile.write(bytes(svgContent, "utf-8"))
            fp.close()

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % self.path, "utf-8"))

    def do_POST(self):

        # parse the URL to get the path and form data
        parsed  = urlparse(self.path);

        if parsed.path in ['/start']:
             
            # get the content length of the request
            content_length = int(self.headers['Content-Length'])
            # extract the form data from the request body
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = dict(parse_qs(post_data))

            # clear the player names list
            playerNames.clear()

            # extract player names from the form data
            player1 = form_data.get('player1', ['Default Player 1'])[0]
            player2 = form_data.get('player2', ['Default Player 2'])[0]

            playerNames.append(player1)
            playerNames.append(player2)

            MyHandler.currentPlayer = random.choice(playerNames)

            # set up the initial table
            MyHandler.currentTable = self.setupTable()
            MyHandler.game = Physics.Game(gameName=gameName, player1Name=playerNames[0], player2Name=playerNames[1])

            self.send_response(302)
            self.send_header("Location", "/pool.html")
            self.end_headers()
            self.wfile.write(MyHandler.currentPlayer.encode())
        
        elif parsed.path in ['/shoot']:

            # get the content length of the request
            content_length = int(self.headers['Content-Length'])

            # extract the form data from the request body
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = dict(parse_qs(post_data))

            xvel = float(form_data["velocityX"][0])
            yvel = float(form_data["velocityY"][0])

            table = MyHandler.currentTable

            print("CURRENT SHOT: " + MyHandler.currentPlayer)
            # call the shoot function and store the returned JSON string
            svgContent = MyHandler.game.shoot(gameName, MyHandler.currentPlayer, table, xvel, yvel)
            MyHandler.currentTable = MyHandler.game.table

            if not MyHandler.condition:
                if MyHandler.game.sunkBalls:
                    if MyHandler.game.sunkBalls[0] != 8 and MyHandler.game.sunkBalls[0] < 8:
                        MyHandler.game.lowPlayer = MyHandler.currentPlayer
                        
                        if MyHandler.game.lowPlayer == playerNames[0]:
                            MyHandler.game.highPlayer = playerNames[1]
                        elif MyHandler.game.lowPlayer == playerNames[1]:
                            MyHandler.game.highPlayer = playerNames[0]

                    elif MyHandler.game.sunkBalls[0] != 8 and MyHandler.game.sunkBalls[0] > 8:
                        MyHandler.game.highPlayer = MyHandler.currentPlayer

                        if MyHandler.game.highPlayer == playerNames[0]:
                            MyHandler.game.lowPlayer = playerNames[1]
                        elif MyHandler.game.highPlayer == playerNames[1]:
                            MyHandler.game.lowPlayer = playerNames[0]

            if MyHandler.game.lowPlayer != "None" and MyHandler.game.highPlayer != "None":
                MyHandler.condition = True
            
            previousPlayer = MyHandler.currentPlayer

            if MyHandler.currentPlayer == playerNames[0]:
                MyHandler.currentPlayer = playerNames[1]
            else:
                MyHandler.currentPlayer = playerNames[0]

            print("LOW: " + MyHandler.game.lowPlayer)
            print("HIGH: " + MyHandler.game.highPlayer)
            # set high / low to their respective string. content.replace

            svgNTurn = {
                'svgContent': svgContent,
                'currentPlayer': MyHandler.currentPlayer,
                'lowPlayer': MyHandler.game.lowPlayer,
                'highPlayer': MyHandler.game.highPlayer,
                'previousPlayer': previousPlayer,
                'winner': MyHandler.game.winner
            }
            # print(MyHandler.game.winner)
            print("NEXT SHOT: " + MyHandler.currentPlayer)

            # send the JSON string as a response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(json.dumps(svgNTurn).encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % self.path, "utf-8"))

    # check ball ordering
    def setupTable(self):

        # create an instance of Table
        poolTable = Physics.Table()

        # add the cue ball
        pos = Physics.Coordinate(Physics.TABLE_WIDTH / 2.0 + 2, Physics.TABLE_LENGTH - Physics.TABLE_WIDTH / 2.0)
        cueBall = Physics.StillBall(0, pos)
        poolTable += cueBall

        ballNum = 1  # start from the second ball
        offset = 5 

        for row in range(1, 6):  # number of rows in the triangle
            for col in range(row):
                # calculate positions for other balls in the triangle
                sbx = 675 + (col - (row - 1) / 2) * Physics.BALL_DIAMETER * 1.08
                sby = 675 - (row - 1) * Physics.BALL_DIAMETER * 1.05

                # add a small offset based on if the row is even or odd
                if row % 2 == 0: 
                    sbx -= offset
                else: 
                    sbx += offset

                ball = Physics.StillBall(ballNum, Physics.Coordinate(sbx, sby))
                poolTable += ball
                ballNum += 1

        return poolTable

if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("\nPlease enter a port.\nCorrect usage: python3 server.py <port #>\n")
        sys.exit(1)

    port = int(sys.argv[1])
    httpd = HTTPServer(('localhost', port), MyHandler)
    print(f"\nServer is active and listening on port #{port}")
    httpd.serve_forever()
