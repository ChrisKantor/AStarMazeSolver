AStarMazeSolver
AUTHOR:     Chris K
DATE:       12/24/2021


Uses A* Algorithm to solve a maze image which the user provides
The image must be placed in the same folder as the program
#The image should be black/white. Black means a barrier and white means a pixel we can traverse through. The image is automatically converted into binary, so any colored mazes might get improperly converted, and thus won't be shown properly
I have provided a test image to use for the program called TestMaze.png. File formatting is important, and any maze file you use has to be compatible with OpenCV. I would recommend using any common image format, such as png or jpg to be safe.


You can left click on the image to select the start/end points of the maze. Only the first 2 selections are considered
You can right click and drag to "paint" a barrier on the maze. This is useful if the maze image doesn't have a border around it, which could cause the algorithm to pathfind outside of the bounds of the maze
You can choose the visualization speed, the higher number the faster it will be, although this greatly depends on the size of the image and the complexity of the maze.
You can also save the image after the pathfinding is complete.
