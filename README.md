# automation

```bash
sudo apt-get install python3-venv
python3 -m venv venv --system-site-packages
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python3 
pip install RPi.GPIO
pip install -r requirements.txt
```


## requirements
```
requests==2.21.0
RPi.GPIO==0.7.0
six==1.12.0
urllib3==1.24.1
```

# creating the systemd service
```
$(pwd)/venv/bin/python3 makeservice.py -d $(pwd) -t keenaqua.service.mustache > keenaqua.service
```

Instructions for setting up your service can be found at https://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/

```
sudo cp keenaqua.service /lib/systemd/system/keenaqua.service
sudo chmod 644 /lib/systemd/system/keenaqua.service
sudo systemctl daemon-reload
sudo systemctl enable keenaqua.service
```
