sudo mkdir -p /etc/monitor
sudo cp config/pmonitor.conf /etc/pmonitor

sudo cp pmonitor/process_monitor.py /usr/local/bin

sudo mkdir -p /var/lib/pmonitor

sudo mkdir -p /srv/venv
sudo python3 -m venv /srv/venv/process-monitoring
sudo /srv/venv/process-monitoring/bin/pip install -r requirements.txt

sudo cp systemd/process_monitor.py /etc/systemd/system
sudo systemctl daemon-reload
sudo systemctl start process_monitor.service
sudo systemctl enable process_monitor.service