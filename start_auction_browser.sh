#!/bin/bash

# Variables
project_dir="/var/www/html/auction-scraper"
venv_dir="~/auction_browser/venv/bin/activate"
backend_dir="~/auction_browser/backend"  # Replace with the actual path to your backend directory

# Start tmux session
tmux new-session -d -s auction_session

# Pane 1: Activate virtual environment and start npm project
tmux send-keys -t auction_session "cd $project_dir" C-m
tmux send-keys -t auction_session "source $venv_dir" C-m
tmux send-keys -t auction_session "npm start" C-m

# Split window for backend
tmux split-window -v
tmux send-keys -t auction_session.1 "cd $backend_dir" C-m
tmux send-keys -t auction_session.1 "node $backend_dir/server.js" C-m

# Split window for interactive session
tmux split-window -h
tmux select-pane -t auction_session.2

# Attach to the tmux session
tmux attach-session -t auction_session
