from dotenv import load_dotenv
from assisstant import Assisstant

import logging
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d','--debug', help='Debug flag', action='store_true')
    args = vars(parser.parse_args())
    return args

def main():
    args = get_args()
    load_dotenv()

    # setup logging
    logging.getLogger("assisstant").setLevel(logging.DEBUG if args.get('debug') else logging.WARNING)
    logging.basicConfig()

    # run the main program flow
    ai_assisstant = Assisstant()
    ai_assisstant.run()

if __name__ == "__main__":
    main()