import argparse
from mole import Mole


parser = argparse.ArgumentParser()
parser.add_argument("FILE_NAME")
args = parser.parse_args()

mole_args = [vars(args)[item] for item in vars(args).keys()]
mole = Mole(mole_args)

mole.enumerate()