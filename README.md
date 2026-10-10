# Notes: anonim blog (Flask + gunicorn)

Gates Notes uslubidagi blog: katta bosh maqola, kartalar, kategoriyalar, qidiruv.
Faqat admin (`/admin`) post yozadi. Admin kunlik / haftalik / oylik tashrif statistikasini ko'radi.
Muallif ko'rsatilmaydi, tashrif hisobi anonim (IP saqlanmaydi, faqat kunlik hash).

## Imkoniyatlar

- Postlar: sarlavha, kategoriya, qisqa tavsif, muqova rasm (yuklash), mini-formatlash (`## sarlavha`, `**qalin**`, `> iqtibos`, `- ro'yxat`, `[havola](https://...)`)
- Admin: post yozish, tahrirlash, o'chirish; ko'rishlar va noyob tashriflar; 14 kunlik grafik; eng ko'p o'qilganlar
- Telefon, planshet va kompyuterga moslashgan dizayn

## 1) Sinash (kompyuteringizda)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
DEV=1 python app.py          # http://127.0.0.1:5000  (admin: /admin, login: admin / admin123)
```

## 2) Real host: VPS (Ubuntu + nginx + systemd)

```bash
sudo apt install -y python3-venv nginx
sudo mkdir -p /opt/blog /var/lib/blog
sudo cp -r . /opt/blog && cd /opt/blog
sudo python3 -m venv venv && sudo venv/bin/pip install -r requirements.txt

sudo cp .env.example .env && sudo nano .env      # ADMIN_PASS ni o'zgartiring!
sudo chown -R www-data:www-data /opt/blog /var/lib/blog
sudo chmod 600 /opt/blog/.env

sudo cp deploy/blog.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now blog

sudo cp deploy/nginx.conf /etc/nginx/sites-available/blog   # example.com ni o'zgartiring
sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d example.com -d www.example.com    # HTTPS
```

Tekshirish: `curl http://127.0.0.1:8000/healthz` → `ok`. Loglar: `journalctl -u blog -f`.
Yangilash: fayllarni almashtiring (`.env` va `/var/lib/blog` ga tegmang), keyin `sudo systemctl restart blog`.

## 3) Render + Supabase (tavsiya)

1. [supabase.com](https://supabase.com) da bepul loyiha oching.
2. **Database**: Project Settings → Database → Connection string → URI
3. **Storage**: Storage → New bucket → `covers` va `files` yarating, ikkalasini **Public** qiling.
4. **API keys**: Project Settings → API → `service_role` (secret) kalitini oling.
5. Render Environment Variables:
   - `DATABASE_URL` = Postgres URI
   - `SUPABASE_URL` = `https://xxxxx.supabase.co`
   - `SUPABASE_KEY` = service_role kaliti
   - `ADMIN_USER`, `ADMIN_PASS`, `SECRET_KEY`
   - `COOKIE_SECURE=1`
6. Start: `gunicorn wsgi:app -c gunicorn.conf.py`

Endi **postlar + statistikalar + rasmlar + fayllar** hammasi Supabase’da saqlanadi.

## 4) Docker

```bash
docker build -t blog .
docker run -d -p 8000:8000 -v blog-data:/data \
  -e ADMIN_PASS='kuchli-parol' -e SECRET_KEY='uzun-tasodifiy-kalit' \
  -e COOKIE_SECURE=0 blog        # HTTPS proksi ortida COOKIE_SECURE=1
```

## Eslatmalar

- `DATABASE_URL` berilsa **Supabase/Postgres**, berilmasa **SQLite** ishlatiladi.
- Tashrif statistikasida admin va botlar hisoblanmaydi. "Noyob tashrif": kuniga bir mehmon bir marta.
- Login xato bo'lsa 1 soniya kutiladi.
- Parolni hash qilib berish:  
  `python -c "from werkzeug.security import generate_password_hash as g;print(g('parol'))"` → `ADMIN_PASS_HASH`.
