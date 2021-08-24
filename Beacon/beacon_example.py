from marvelmind import MarvelmindHedge
from time import sleep
import sys


def main():
    hedge = MarvelmindHedge(tty="COM3", adr=5, debug=False)  # create MarvelmindHedge thread
    hedge.start()  # start thread
    while True:
        try:
            sleep(1)
            # print (hedge.position()) # get last position and print
            hedge.print_position()
            if (hedge.distancesUpdated):
                hedge.print_distances()
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port
            sys.exit()


main()
