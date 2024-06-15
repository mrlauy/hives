# hives

Control some pins and speaker

### install

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Install it as a service
```
sudo ln -s /home/pi/hives/hives.service /etc/systemd/system/hives.service
sudo systemctl --system daemon-reload
sudo systemctl enable hives
sudo systemctl start hives
```
