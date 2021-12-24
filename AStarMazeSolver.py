#Author:            Chris Kantor
#Date  :            12/24/2021
#Description:       This program uses the A* algoritihm to solve any maze you give it. The maze must be an image filetype recognized by openCV (such as a jpg or png) and must be black and white,
#                   or the algorithm might not work. you will be able to left click on the maze for the start and end points of the maze, and if needed, can right click and drag to "paint" a 
#                   barrier onto the maze. 
#########################################################################################################
import cv2
import heapq
import math
import os.path

#Color constants we will use to set individual pixels to specific colors later in the algorithm
#openCV uses BGR instead of RGB, so the color codes are reversed
BLUE = (255, 0, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

#Global variables we use later when we select the start/end points of the maze or when we draw on the maze to add additional barriers
SEPoints = []
selectionCounter = 0
filling = False
#########################################################################################################
#The clicked event is used when we want to select the start and end points on the maze/draw any additional barriers
#Set the start/end points with LEFT CLICK
#draw any barriers with RIGHT CLICK
#only the first 2 LEFT CLICKS are considered
def clicked(event, x, y, flags, param):
    global selectionCounter, SEPoints, filling
    if event == cv2.EVENT_LBUTTONUP:
        SEPoints.append((y, x))
        selectionCounter += 1
        img[(y, x)] = GREEN

    
    if event == cv2.EVENT_RBUTTONDOWN:
        filling = True
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if filling == True:
            if inRange(y, x):
                img[(y, x)] = BLACK
                cv2.imshow("Image", img)
                cv2.waitKey(1)

    if event == cv2.EVENT_RBUTTONUP:
        filling = False



#The heuristic function used to generate the fscore. Uses DIAGONAL distance since we can move in 8 directions
#Takes the current x,y and the end x, y and returns the diagonal distance between the two
def heuristic(cx, cy, endX, endY):
    dx = (cx - endX)
    dy = (cy - endY)
    return (dx + dy) + (math.sqrt(2) - 2) * min(dx, dy)



#Checks all 8 adjacent pixels of the pixel we are currently on. Returns a list of these pixels
#a pixel is valid if it isn't a barrier, if it isn't visited, and if it is in range of the image
def generateAdj(x, y, visited):
    adj = []
    up, left, down, right = False, False, False, False

    #check UP
    if (x > 0 and not tuple(img[x - 1][y]) == BLACK) and not (x - 1, y) in visited:
        adj.append((x - 1, y))
        up = True

    #check DOWN
    if (x < img.shape[0] - 1 and not tuple(img[x + 1][y]) == BLACK) and not (x + 1, y) in visited:
        adj.append((x + 1, y))
        down = True

    #check LEFT
    if (y > 0 and not tuple(img[x][y - 1]) == BLACK) and not (x, y - 1) in visited:
        adj.append((x, y - 1))
        left = True
    
    #check RIGHT
    if (y < img.shape[1] - 1 and not tuple(img[x][y + 1]) == BLACK) and not (x, y + 1) in visited:
        adj.append((x, y + 1))
        right = True

    #CHECKING DIAGONALS
    #If the two adjacent pixels are blocked, then we can't go diagonally in that direction, otherwise we can.
    #UP/LEFT
    if ((up or left) and x > 0 and y > 0 and not tuple(img[x - 1][y - 1]) == BLACK) and not (x - 1, y - 1) in visited:
        adj.append((x - 1, y - 1))

    #UP/RIGHT
    if ((up or right) and x > 0 and y < img.shape[1] - 1 and not tuple(img[x - 1][y + 1]) == BLACK) and not (x - 1, y + 1) in visited:
        adj.append((x - 1, y + 1))

    #DOWN/LEFT
    if ((down or left) and x < img.shape[0] - 1 and y > 0 and not tuple(img[x + 1][y - 1]) == BLACK) and not (x + 1, y - 1) in visited:
        adj.append((x + 1, y - 1))

    #DOWN/RIGHT
    if ((down or right) and x < img.shape[0] - 1 and y < img.shape[1] - 1 and not tuple(img[x + 1][y + 1]) == BLACK) and not (x + 1, y + 1) in visited:
        adj.append((x + 1, y + 1))

    return adj



def inRange(x, y):
    if ((0 <= x)  and (0 <= y) ):
        if x < img.shape[0] and y < img.shape[1]:
            return True
    return False



def AStar(startX, startY, endX, endY, speed):
    #All of the data structures we need for AStar to work. fScore is the sum of gScore and the heuristic score
    openQueue = []
    visited = {}
    gScore = {}
    fScore = {}
    parent = {}
    path = []
    shouldDraw = 0

    #sets the gScore and fScore of every pixel to infinity
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            gScore[(i, j)] = float("inf")
            fScore[(i, j)] = float("inf")
    
    #sets the start pixels gScore to 0 and its fScore = the heuristic score
    gScore[(startX, startY)] = 0
    fScore[(startX, startY)] = heuristic(startX, startY, endX, endY)

    #put the start pixel into the priority queue. We are using the python heapqueue for this since it is a min-heap, and we always want to get the smallest fScore
    #this is to be sorted by fScore, so we will use the fScore as the kendY and the pixel location as the value
    heapq.heappush(openQueue, (fScore.get((startX, startY)), (startX, startY)))

    #A dictionary to hold which pixels are in the openqueue are not, as python doesn't support searching priority queues directly
    openQueueDict = {(startX, startY)}

    #Start of the actual algorithm
    #While the priority queue IS NOT empty
    while len(openQueue) > 0:

        #How often we should refresh the image to show the pathfinding, determined by speed
        if speed > 0:
            shouldDraw += 1
            #How often we need to draw. The higher speed is, the less often we draw, and the faster the visualization is
            #This depends greatly on the size of the image and layout of the maze as this loop restarts whenever we go onto another pixel
            #if the maze has a lot of white space and is very large, there are a lot of valid pixels we could move to, so we end up drawing a lot more
            #whereas a very small image or a maze which is very compact and has paths that are only a few pixels wide may have less valid pixels,
            #so we may end up drawing less
            if shouldDraw > 20 * speed:
                cv2.imshow("Pathfinding Visualization", img)
                cv2.waitKey(1)
                shouldDraw = 0

        #get the pixel with the lowest fscore from the priority queue that has not been visited yet
        currentPixel = heapq.heappop(openQueue)
        while currentPixel[1] in visited:
            currentPixel = heapq.heappop(openQueue)
        openQueueDict.remove((currentPixel[1]))

        #if this pixel is the end pixel, we are done and can return the path, which we populate by traversing backwards through the parent dictionary
        if currentPixel[1] == (endX, endY): 
            z = (endX, endY)
            path.append(z)
            while parent[z] != (startX, startY):
                path.append(z)
                z = parent[z]
            path.append(z)
            path.append((startX, startY))
            return path

        #generate a list of the current pixels adjacent pixels
        adjacent = generateAdj(currentPixel[1][0], currentPixel[1][1], visited)

        #for each of the adjacent pixels
        for i in adjacent:
            tempGScore = gScore.get((currentPixel[1][0], currentPixel[1][1])) + 1

            #if this gScore is LESS than the one an adjacent pixel already has, update that pixels gScore to tempGScore, hScore to tempGScore + its heuristic, and update its parent to the curentPixel.
            if tempGScore < gScore.get(i):
                gScore[i] = tempGScore
                fScore[i] = tempGScore + heuristic(i[0], i[1], endX, endY)
                parent[i] = (currentPixel[1])

                #add the adjacent pixel to the priority queue and the dictionary
                heapq.heappush(openQueue, (fScore.get(i), i)  )
                openQueueDict.add(i)

                #color this pixel RED and update image
                img[i] = RED

        #Set this pixel as visited
        visited[currentPixel[1]] = True
    
    #if we couldn't find a path to the end, return None
    return None



def main():
    #Gets how fast we want to visualize the pathfinding. 0 skips the visualization all together, and 1 is very slow (draws every time the while loop in A* restarts) while 10 is very fast
    #Depending on how large your image is, 10 could still be slow
    visualSpeed = input("How fast would you like the visualization to be? 1 is very slow and 10 is very fast. To skip visualization, enter 0: ")
    visualSpeed = int(visualSpeed)

    #Displays the maze image you provided. It might appear in a different window, so just look at the taskbar and open it through that
    print("\n\n\nPlease Left click where you want the start of the maze to be, then where you want the end of the maze to be")
    print("If you want to draw a barrier on the image, right click")
    print("\nPress [SPACE] after you are done to let the program find the best path between your selections")
    cv2.imshow("Image", img)

    #clicked is our function that gets the start/end points of the maze and if you want to paint in any barriers onto the maze
    #it only takes into consideration the first 2 times you left click however, the first time being the start location and the second being the end location
    #any clicks after the first 2 will not be considered
    cv2.setMouseCallback("Image", clicked)
    cv2.waitKey(0)

    startx, starty = SEPoints[0]
    endx, endy = SEPoints[1]

    print("\nSolving...")

    #The AStart algoirthm. Takes in the start and end coordinates as well as our visualization speed
    #returns a list of pixels that make up the path. If path == None, the maze is impossible to solve
    path = AStar(startx, starty, endx, endy, visualSpeed)

    if path == None:
        print("The maze is impossible to solve")
        exit()
    
    print("Solved!")
    #Sets each pixel in the path to green
    for i in path:
        img[i] = GREEN
    
    #Displays the solved maze with pathfinding on it
    print("\n\n Press [SPACE] when you are done to continue")
    cv2.imshow("Solved", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows

    #Asks if you want to save the solved maze. Will save a maze that just has the path on it, not the RED pathfinding
    save = input("\nWould you like to save this solved maze? If so, type in YES: ")
    if save == "YES":
        print("Saving...")
        
        #removes RED pathfinding from the maze
        for i in range(img.shape[0]):
            for j in range(img.shape[1]):
                if tuple(img[(i, j)]) == RED:
                    img[(i, j)] = WHITE
        
        #saves the solved maze as filename_solved.endXtention
        splitName = os.path.splitext(filename)
        cv2.imwrite(splitName[0] + "_Solved" + splitName[1], img)

        print("Saved!")



#########################################################################################################
#Start of our program, gets the user input for filename. The file must be an image, and it has to be in the same directory as this program.
filename = input("What is the name of the image you would like to use? The file must be in the same folder as this program: ")
img = cv2.imread(filename, 0)

#if the filename doesn't exist, end the program
if img is None:
    print("That file does not exist")
    exit()

#Convert the image into binary, then back into color. This will ensure that every pixel is either BLACK (0, 0, 0) or WHITE (255, 255, 255). so we can easily
#tell if something is barrier or a path we can go down. This also allows us to color in pixels as we see fit, as we can't color in binary
r, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
main()