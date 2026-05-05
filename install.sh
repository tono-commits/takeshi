#!/bin/bash
# Install the daily US market report as a systemd user timer.
# Run once to enable automatic 8:00 AM JST execution.

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"

mkdir -p "$UNIT_DIR"

cp "$REPO_DIR/market-report.service" "$UNIT_DIR/"
cp "$REPO_DIR/market-report.timer"   "$UNIT_DIR/"

systemctl --user daemon-reload
systemctl --user enable --now market-report.timer

echo "インストール完了:"
systemctl --user status market-report.timer --no-pager
echo ""
echo "次回実行予定:"
systemctl --user list-timers market-report.timer --no-pager
