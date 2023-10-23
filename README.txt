Balti Zirgai alaus baras.

Norint pasileisti pirmiausia reikia susikurti projekte local_settings.py
SECRET_KEY=''
EMAIL_HOST= ''
EMAIL_HOST_USER=''
EMAIL_HOST_PASSWORD= ""
DEBUG= True

Instaliuojam requirments.txt terminale:
pip install -r requirments.txt

Duomenų bazės užkrovimas.
terminale:
./manage.py loadata beer.json

Pasileidus Docker terminale:
docker-compose build
docker-compose up -d

