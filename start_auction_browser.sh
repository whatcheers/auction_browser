# Start tmux session
tmux new-session -d -s auction_session

# Pane 1: Activate virtual environment and start npm project
tmux send-keys -t auction_session "cd ~/auction_browser/frontend/auction-scraper" C-m
tmux send-keys -t auction_session "source ~/auction_browser/venv/bin/activate" C-m
tmux send-keys -t auction_session "npm start" C-m

# Split window for backend
tmux split-window -v
tmux send-keys -t auction_session.1 "source ~/auction_browser/venv/bin/activate" C-m
tmux send-keys -t auction_session.1 "cd ~/auction_browser/backend" C-m
tmux send-keys -t auction_session.1 "node httpsServer.js" C-m

# Attach to the tmux session
tmux attach-session -t auction_session
