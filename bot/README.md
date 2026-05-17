# Bot — Python trading engine

CAN SLIM strategy with cup-with-handle entry. Runs on the DigitalOcean droplet under `systemd`.

## Layout (target)

```
bot/
├── README.md          this file
├── .env.example       template for secrets (real .env is gitignored)
├── requirements.txt   pinned dependencies (TODO: populate after migration)
├── bot.py             main loop
├── config.py          parameters (see .claude/PLAN.md for values)
└── strategy.py        cup-with-handle + CAN SLIM signal logic
```

## Deploy workflow

SSH to the VPS as `mike` (key auth — see `.claude/CLAUDE.md` §SSH Access), then:

```sh
sudo git -C /root/trading_bot pull
sudo systemctl restart trading-bot.service
```

The repo lives under `/root/` (mode 700) so `mike` can't `cd` into it; `git -C <path>` works around that without needing `sudo -i`.

## Historical: one-time migration runbook

The bot used to live at `/root/trading-bot/` (hyphen) on the VPS and was **not** in git. Migrated 2026-05-17 — kept here for reference only. The current deploy workflow is the section above.

### Step 1 — pull the current bot source to your local repo

On the VPS, stage the files in a place `mike` can scp:

```sh
ssh mike@167.172.107.21
sudo cp /root/trading-bot/bot.py /root/trading-bot/config.py /root/trading-bot/strategy.py /home/mike/
sudo chown mike:mike /home/mike/{bot,config,strategy}.py
sudo /root/trading-bot/venv/bin/pip freeze > /home/mike/requirements.txt
sudo cat /etc/systemd/system/trading-bot.service > /home/mike/trading-bot.service
exit
```

From your Windows machine, in the repo root:

```sh
scp mike@167.172.107.21:~/bot.py        bot/bot.py
scp mike@167.172.107.21:~/config.py     bot/config.py
scp mike@167.172.107.21:~/strategy.py   bot/strategy.py
scp mike@167.172.107.21:~/requirements.txt bot/requirements.txt
scp mike@167.172.107.21:~/trading-bot.service ./trading-bot.service.bak  # keep as a reference, not committed
```

Then clean up the staging area:

```sh
ssh mike@167.172.107.21 'rm /home/mike/{bot,config,strategy}.py /home/mike/requirements.txt /home/mike/trading-bot.service'
```

### Step 2 — review and commit

```sh
# Verify nothing sensitive snuck in (the .env was NOT copied — good)
grep -r -E 'ALPACA|SECRET|KEY=' bot/ | grep -v .env.example
# Should return no real secrets.

git add bot/
git commit -m "feat: import bot source from VPS (was previously scp-only)"
git push
```

### Step 3 — switch VPS deployment to git pull

```sh
ssh mike@167.172.107.21

# Stop the bot
sudo systemctl stop trading-bot.service

# Back up the old location (don't delete until verified)
sudo mv /root/trading-bot /root/trading-bot.bak

# Clone the repo to /root/trading_bot/  (note: underscore, matches the GitHub repo name)
sudo git clone https://github.com/mike-zuczkiewicz/trading_bot.git /root/trading_bot

# Restore the .env (only non-version-controlled state)
sudo cp /root/trading-bot.bak/.env /root/trading_bot/bot/.env
sudo chmod 600 /root/trading_bot/bot/.env

# Reuse the existing venv (cheaper than re-installing)
sudo mv /root/trading-bot.bak/venv /root/trading_bot/bot/venv

# Update the systemd unit's paths
sudo sed -i 's|/root/trading-bot|/root/trading_bot/bot|g' /etc/systemd/system/trading-bot.service
sudo systemctl daemon-reload

# Start the bot from the new location
sudo systemctl start trading-bot.service
sudo systemctl status trading-bot.service --no-pager
sudo tail -n 30 /root/trading_bot/bot/bot.log
```

### Step 4 — verify, then remove the backup

After watching the bot run cleanly for a session (e.g. one full scan cycle):

```sh
sudo rm -rf /root/trading-bot.bak
```

## Future changes

Edit files locally → commit → push → `git pull` on the VPS → `sudo systemctl restart trading-bot.service`. Parameter changes get logged to `bot/audit.log` per the schema in `.claude/CLAUDE.md` §Audit Trail.
