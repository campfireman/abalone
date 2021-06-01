#!/bin/bash

source src/env/bin/activate
python3 main.py src.players.AlphaBetaPlayer abalone.random_player.RandomPlayer -v | tee -a output.txt
