sudo mkdir -p /etc/pmonitor/
sudo cp config/pmonitor.conf /etc/pmonitor/

sudo cp pmonitor/process_monitor.py /usr/local/bin/

sudo mkdir -p /var/lib/pmonitor/

sudo mkdir -p /srv/venv/
sudo python3 -m venv /srv/venv/process-monitoring/
sudo /srv/venv/process-monitoring/bin/pip install -r requirements.txt

sudo cp systemd/process_monitor.service /etc/systemd/system/process_monitor.service
sudo systemctl daemon-reload
sudo systemctl start process_monitor.service
sudo systemctl enable process_monitor.service
