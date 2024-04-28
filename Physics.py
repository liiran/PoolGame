import phylib;
import os
import sqlite3
import math

################################################################################
# import constants from phylib to global variables

BALL_RADIUS = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE = phylib.PHYLIB_SIM_RATE
VEL_EPSILON = phylib.PHYLIB_VEL_EPSILON
DRAG = phylib.PHYLIB_DRAG
MAX_TIME = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS = phylib.PHYLIB_MAX_OBJECTS
FRAME_RATE = 0.01

HEADER = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750"
xmlns="http://www.w3.org/2000/svg"
xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />""";

FOOTER = """</svg>\n""";

################################################################################
# the standard colours of pool balls
# if you are curious check this out:  
# https://billiards.colostate.edu/faq/ball/colors/

BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
    ];

################################################################################
class Coordinate( phylib.phylib_coord ):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass;

################################################################################  
# constructors
class StillBall( phylib.phylib_object ):
    """
    Python StillBall class.
    """

    def __init__(self, number, pos):
        """
        Constructor function. Requires ball number and position (x,y) as
        arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, phylib.PHYLIB_STILL_BALL, number, pos, None, None, 0.0, 0.0)
      
        # this converts the phylib_object into a StillBall class
        self.__class__ = StillBall

    def svg(self):

        if self.obj.still_ball.number == 0:  # check if its a cue
            return """ <circle id="cue-ball" cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])
        else:
            return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.still_ball.pos.x, self.obj.still_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.still_ball.number])


class RollingBall(phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__(self, number, pos, vel, acc):
        """
        Constructor function. Requires ball number, position (x,y),
        velocity (x,y), and acceleration (x,y) as arguments.
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, phylib.PHYLIB_ROLLING_BALL, number, pos, vel, acc, 0.0, 0.0)

        # this converts the phylib_object into a RollingBall class
        self.__class__ = RollingBall

    def svg(self):
        
        return """ <circle cx="%d" cy="%d" r="%d" fill="%s" />\n""" % (self.obj.rolling_ball.pos.x, self.obj.rolling_ball.pos.y, BALL_RADIUS, BALL_COLOURS[self.obj.rolling_ball.number])


class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__(self, pos):
        """
        Constructor function. Requires position (x,y),
        """

        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, phylib.PHYLIB_HOLE, 0, pos, None, None, 0.0, 0.0)

        # this converts the phylib_object into a Hole class
        self.__class__ = Hole

    def svg(self):
        
        return """ <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (self.obj.hole.pos.x, self.obj.hole.pos.y, HOLE_RADIUS)
      

class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):
        """
        Constructor function. Requires y-coordinate as an argument.
        """
        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, phylib.PHYLIB_HCUSHION, 0, None, None, None, 0.0, y)

        # this converts the phylib_object into a HCushion class
        self.__class__ = HCushion

    def svg(self):

        if self.obj.hcushion.y == 0:
            y = -25 
        else:
            y = 2700
        
        return """ <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (y)


class VCushion(phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__(self, x):
        """
        Constructor function. Requires x-coordinate as an argument.
        """
        # this creates a generic phylib_object
        phylib.phylib_object.__init__(self, phylib.PHYLIB_VCUSHION, 0, None, None, None, x, 0.0)

        # this converts the phylib_object into a VCushion class
        self.__class__ = VCushion

    def svg(self):

        if self.obj.vcushion.x == 0:
            x = -25 
        else:
            x = 1350
        
        return """ <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (x)

################################################################################

class Table( phylib.phylib_table ):
    """
    Pool table class.
    """

    def __init__( self ):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__( self );
        self.current = -1;

    def __iadd__( self, other ):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object( other );
        return self;

    def __iter__( self ):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        self.current = -1
        return self;

    def __next__( self ):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1;  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[ self.current ]; # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1;    # reset the index counter
        raise StopIteration;  # raise StopIteration to tell for loop to stop

    def __getitem__( self, index ):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object( index ); 
        if result==None:
            return None;
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall;
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall;
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole;
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion;
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion;
        return result;

    def __str__( self ):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = "";    # create empty string
        result += "time = %6.1f;\n" % self.time;    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj);  # append object description
        return result;  # return the string

    def segment( self ):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment( self );
        if result:
            result.__class__ = Table;
            result.current = -1;
        return result;

    def svg(self):

        # create a string with the header
        svgString = HEADER

        # iterate over every object in the table
        # if the obj is not null then call the corresponding object's svg method and add the result to the string
        for obj in self:
            if obj is not None:
                svgString += obj.svg()

        svgString += FOOTER
        return svgString
    
    def roll( self, t ):
        new = Table();
        for ball in self:
            if isinstance( ball, RollingBall ):
                # create4 a new ball with the same number as the old ball
                new_ball = RollingBall( ball.obj.rolling_ball.number, Coordinate(0,0), Coordinate(0,0), Coordinate(0,0) );
                # compute where it rolls to
                phylib.phylib_roll( new_ball, ball, t );
        
                # add ball to table
                new += new_ball;
        
            if isinstance( ball, StillBall ):
                # create a new ball with the same number and pos as the old ball
                new_ball = StillBall( ball.obj.still_ball.number, Coordinate( ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y ) );
        
                # add ball to table
                new += new_ball;
        
        # return table
        return new;

    def cueBall(self):
        for ball in self:
            if isinstance(ball, StillBall) and ball.obj.still_ball.number == 0:
                return ball
        return None

class Database:

    def __init__(self, reset=False):

        # if reset is true then check if phylib.db exists and if it does then delete it
        if (reset):
            if os.path.exists('phylib.db'):
                os.remove('phylib.db');

        self.conn = sqlite3.connect('phylib.db')

    def createDB(self):

        self.cursor = self.conn.cursor()

        # create all the required tables
        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS Ball (
                    BALLID INTEGER PRIMARY KEY AUTOINCREMENT,
                    BALLNO INTEGER NOT NULL,
                    XPOS FLOAT NOT NULL,
                    YPOS FLOAT NOT NULL,
                    XVEL FLOAT,
                    YVEL FLOAT ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS Ttable (
                    TABLEID INTEGER PRIMARY KEY AUTOINCREMENT,
                    TIME FLOAT NOT NULL ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS BallTable (
                    BALLID INTEGER NOT NULL,
                    TABLEID INTEGER NOT NULL,
                    FOREIGN KEY (BALLID) REFERENCES Ball,
                    FOREIGN KEY (TABLEID) REFERENCES Ttable ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS Shot (
                    SHOTID INTEGER PRIMARY KEY AUTOINCREMENT,
                    PLAYERID INTEGER NOT NULL,
                    GAMEID INTEGER NOT NULL,
                    FOREIGN KEY (PLAYERID) REFERENCES Player,
                    FOREIGN KEY (GAMEID) REFERENCES Game ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS TableShot (
                    TABLEID INTEGER NOT NULL,
                    SHOTID INTEGER NOT NULL,
                    FOREIGN KEY (TABLEID) REFERENCES Ttable,
                    FOREIGN KEY (SHOTID) REFERENCES Shot ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS Game (
                    GAMEID INTEGER PRIMARY KEY AUTOINCREMENT,
                    GAMENAME VARCHAR(64) NOT NULL ) """)

        self.cursor.execute(""" CREATE TABLE IF NOT EXISTS Player (
                    PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT,
                    GAMEID INTEGER NOT NULL,
                    PLAYERNAME VARCHAR(64) NOT NULL,
                    FOREIGN KEY (GAMEID) REFERENCES Game ) """)

        self.conn.commit()
        self.cursor.close()
        
    def readTable(self, tableID):

        self.cursor = self.conn.cursor()
        
        # select the time from Ttable where the tableid corresponds
        self.cursor.execute(""" SELECT TIME FROM Ttable WHERE TABLEID = ?""", (tableID + 1,))
        time = self.cursor.fetchone()

        # CHECK + time vs time[0]
        if time is None:
            return None
        
        table = Table()
        table.time = time[0]

        # cselect all from Ball and join with BallTable
        self.cursor.execute("""SELECT * FROM Ball INNER JOIN BallTable ON Ball.BALLID = BallTable.BALLID WHERE BallTable.TABLEID = ?""", (tableID + 1,))
        balls = self.cursor.fetchall()

        for ball in balls:
            pos = Coordinate(ball[2], ball[3])

            # still ball case
            if ball[4] is None and ball[5] is None:
                table += StillBall(ball[1], pos)
            else:
                # if its a rolling ball then calculate speed same as we did in A2
                # check if speed is greater or less than VEL_EPSILON
                vel = Coordinate(ball[4], ball[5])
                speed = math.sqrt((ball[4] * ball[4]) + (ball[5] * ball[5]))

                if speed > VEL_EPSILON:
                    acc = Coordinate(-(ball[4] / speed) * DRAG, -(ball[5] / speed) * DRAG)
                else:
                    acc = Coordinate(0.0, 0.0)
           
                table += RollingBall(ball[1], pos, vel, acc)
            
        self.conn.commit()
        self.cursor.close()
        
        # check if any balls were retrieved from the database for the given TABLEID
        # if there are balls return the table and if not then return None
        if len(balls) > 0:
            return table
        else: 
            return None

    # OPTIMIZE - less insert statements - multi execute
    def writeTable(self, table):
        
        # connect cursor and store the time
        self.cursor = self.conn.cursor()
        time = table.time

        # insert time into Ttable
        self.cursor.execute(""" INSERT INTO Ttable (TIME) VALUES (?)""", (time,))
        tableID = self.cursor.lastrowid
        
        for obj in table:
            # if its a stillBall instance then insert the corresponding values into Ball and BallTable tables
            if isinstance(obj, StillBall):

                self.cursor.execute(""" INSERT INTO Ball (BALLNO, XPOS, YPOS) VALUES (?, ?, ?)""", (obj.obj.still_ball.number, obj.obj.still_ball.pos.x, obj.obj.still_ball.pos.y))
                ballID = self.cursor.lastrowid
                self.cursor.execute(""" INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)""", (ballID, tableID))
            
            # if its a rollingBall instance then insert the corresponding values into Ball and BallTable tables
            elif isinstance(obj, RollingBall):
                
                self.cursor.execute(""" INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)""", 
                                    (obj.obj.rolling_ball.number, obj.obj.rolling_ball.pos.x, obj.obj.rolling_ball.pos.y, 
                                     obj.obj.rolling_ball.vel.x, obj.obj.rolling_ball.vel.y))
                ballID = self.cursor.lastrowid
                self.cursor.execute(""" INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)""", (ballID, tableID))

        # commit then close
        self.conn.commit()
        self.cursor.close()
        self.cursor = self.conn.cursor()
        
        return (tableID - 1)

    def gameGet(self, gameID):

        # select the gameID and the two player names and join the tables
        # then order the table by playerID
        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT Game.GAMENAME, Player.PLAYERNAME FROM Game JOIN Player ON Game.GAMEID = Player.GAMEID WHERE Game.GAMEID = ? ORDER BY Player.PLAYERID""", (gameID,))
        result = self.cursor.fetchall()
        
        self.cursor.close()
        return result

    def gameSet(self, gameName, player1Name, player2Name):
        
        self.cursor = self.conn.cursor()

        # insert the game name into Game
        self.cursor.execute("""INSERT INTO Game (GAMENAME) VALUES (?)""", (gameName,))
        gameID = self.cursor.lastrowid

        # insert player 1 and player 2 names into Player table then commit
        self.cursor.execute("""INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, player1Name))
        self.cursor.execute("""INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, player2Name))
        
        self.conn.commit()
        self.cursor.close()

        return (gameID - 1)
    
    def newShot(self, gameName, playerName):

        self.cursor = self.conn.cursor()

        # select the GAMEID from the game table that matches the GAMENAME and then the first result
        self.cursor.execute("""SELECT GAMEID FROM Game WHERE GAMENAME = ?""", (gameName,))
        gameID = self.cursor.fetchone()[0]

        # select the PLAYERID from the player table that matches the PLAYERNAME and the GAMEID
        self.cursor.execute("""SELECT PLAYERID FROM Player WHERE PLAYERNAME = ? AND GAMEID = ?""", (playerName, gameID))
        playerID = self.cursor.fetchone()[0]

        # inserts a new row into the Shot table containing the PLAYERID and GAMEID
        self.cursor.execute("""INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)""", (playerID, gameID))
        
        self.conn.commit()
        shotID = self.cursor.lastrowid

        self.cursor.close()
        return shotID

    def getFinalTable(self):

        self.cursor = self.conn.cursor()
        self.cursor.execute("""SELECT TABLEID FROM TTable ORDER BY TABLEID DESC LIMIT 1""")
        tableID = self.cursor.fetchone()[0]

        if tableID:
            poolTable = self.readTable(tableID - 1)
            return poolTable
        else:
            return None
    
    def getTableAtTime(self, time):

        try:
            self.cursor = self.conn.cursor()
            self.cursor.execute("""SELECT TABLEID FROM TTable ORDER BY ABS(TIME - ?) LIMIT 1""", (time,))
            tableID = self.cursor.fetchone()[0]

            if tableID:
                poolTable = self.readTable(tableID - 1)
                return poolTable
            else:
                return None
        
        except:
            print("Getting last table instead")
            lastTable = self.getLastTable()
            return lastTable

    def close(self):
        
        # commit connection then close the cursor and connection
        self.conn.commit()
        self.cursor.close()
        self.conn.close()
        
class Game:

    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):

        # declaring instance variables
        self.gameID = gameID
        self.gameName = gameName
        self.player1Name = player1Name
        self.player2Name = player2Name
        self.lowPlayer = "None"
        self.highPlayer = "None"
        self.winner = None
        self.sunkBalls = []

    def shoot(self, gameName, playerName, table, xvel, yvel):

        svgContentsArray = []

        # find the cue ball and its position
        cueBall = table.cueBall()
            
        if cueBall is not None:

            # store the cue ball's position values and set the type to rolling ball
            xpos = cueBall.obj.still_ball.pos.x
            ypos = cueBall.obj.still_ball.pos.y
            cueBall.type = phylib.PHYLIB_ROLLING_BALL

            # set the position attributes to the stored values 
            # and set the velocity attributes using the passed values
            cueBall.obj.rolling_ball.pos.x = xpos
            cueBall.obj.rolling_ball.pos.y = ypos
            
            cueBall.obj.rolling_ball.vel.x = xvel
            cueBall.obj.rolling_ball.vel.y = yvel
            
            # recalculate the acceleration
            speed = math.sqrt(xvel* xvel + yvel* yvel)

            if (speed > VEL_EPSILON):
                cueBall.obj.rolling_ball.acc.x = (-(xvel / speed) * DRAG)
                cueBall.obj.rolling_ball.acc.y = (-(yvel / speed) * DRAG)
            else:
                cueBall.obj.rolling_ball.acc.x = 0.0
                cueBall.obj.rolling_ball.acc.y = 0.0
            
            cueBall.obj.rolling_ball.number = 0

            # print(cueBall.obj.rolling_ball.acc.x)
            # print(cueBall.obj.rolling_ball.acc.y)

        beforeBallsArray = []
        afterBallsArray = []

        for ball in table:
            if ball and isinstance(ball, StillBall):
                beforeBallsArray.append(ball.obj.still_ball.number)
            elif ball and isinstance(ball, RollingBall):
                beforeBallsArray.append(ball.obj.rolling_ball.number)

        # get the first segment of the table
        segment = table.segment()
        delimiter = "<!-- SVG DELIMITER -->"
        
        # while segment is not NULL
        while segment is not None:
            segmentLength = segment.time - table.time
            frameCount = int(segmentLength / FRAME_RATE)

            for i in range(frameCount):
                
                loopTime = i * FRAME_RATE
                newTable = table.roll(loopTime)
                newTable.time = table.time + loopTime

                svgContentsArray.append(newTable.svg())  # add SVG string to array

            table = segment
            segment = table.segment()
            svgContentsArray.append(table.svg())

        for ball in table:
            if ball and isinstance(ball, StillBall):
                afterBallsArray.append(ball.obj.still_ball.number)
            elif ball and isinstance(ball, RollingBall):
                afterBallsArray.append(ball.obj.rolling_ball.number)

        for ball in beforeBallsArray:
            if ball not in afterBallsArray:
                self.sunkBalls.append(ball)

        if all(ball != 0 for ball in afterBallsArray):
            # create a new cue ball element with the same id
            cueBall = StillBall(0, Coordinate(675, 2025))
            cueBall.id = 'cue-ball'

            # add the cue ball to the table and append the last svg
            table += cueBall
            svgContentsArray.append(table.svg())

        print(self.sunkBalls)

        if 8 in self.sunkBalls:
            # check which player shot the 8 ball
            if playerName == self.player1Name:
                self.winner = self.player2Name
            else:
                self.winner = self.player1Name

        # logic for high ball - low ball continuous turns
        # logic for game end
        
        svgContentDel = delimiter.join(svgContentsArray)
        self.table = table

        return svgContentDel
    