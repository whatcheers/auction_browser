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

# Attach to the tmux session
tmux attach-session -t auction_session
