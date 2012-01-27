#This Script is an example of what is possible with the PostProcess feature of Auto-Sub
#The Current options available are:
# echo | simply echo the arguments given to the post process script
import sys

what = "echo"

if what == "echo":
    print
    print sys.argv[1]
    print sys.argv[2]