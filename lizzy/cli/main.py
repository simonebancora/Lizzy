#  Copyright 2025-2026 Simone Bancora, Paris Mulye
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

import argparse
from lizzy.utils.splash_logo import print_logo

def main():
    parser = argparse.ArgumentParser(
        prog="lizzy",
        description="Lizzy CLI",)

    subparsers = parser.add_subparsers(dest="command")

    # Info command
    subparsers.add_parser("info", help="Display information on installed Lizzy solver")

    args = parser.parse_args()

    # Default: print available commands if no subcommand
    if args.command is None:
        print_logo()
        print("Available commands:")
        for cmd in subparsers.choices.keys():
            print(f"  {cmd}")
        return

    # Handle commands
    if args.command == "info":
        print ("Lizzy Solver - v0.1.0")
        print ("Developed by S. Bancora and P. Mulye")
        print ("Copyright 2025-2026")
        print ("Licensed under the GNU General Public License v3.0")
        print ("For more information, visit https://github.com/simonebancora/lizzy")