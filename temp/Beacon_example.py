from marvelmind import MarvelmindHedge
from time import sleep
import sys


def main():
    hedge = MarvelmindHedge(adr=6, tty="COM3", debug=False)  # create MarvelmindHedge thread

    hedge.start()  # start thread

    while True:
        try:
            sleep(0.5)
            print(hedge.position()) # get last position and print
            #hedge.print_position()

            # if (hedge.distancesUpdated):
                # hedge.print_distances()
        except KeyboardInterrupt:
            hedge.stop()  # stop and close serial port
            sys.exit()


main()
