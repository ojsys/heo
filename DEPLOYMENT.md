# HEO Foundation - cPanel Deployment Guide

## Prerequisites

- cPanel hosting with Python support
- PostgreSQL database created
- Domain configured

## Deployment Steps

### 1. Upload Files

Upload all project files to your cPanel home directory:
```
/home/yourusername/heo/
```

### 2. Create PostgreSQL Database

In cPanel → PostgreSQL Databases:
1. Create database: `yourusername_dbase`
2. Create user: `yourusername_db_user`
3. Add user to database with all privileges

### 3. Configure Environment

Copy production environment file:
```bash
cp .env.production .env
```

Edit `.env` with your values:
- `SECRET_KEY` - Generate new: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD` - Your database credentials
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` - Your email credentials
- `ALLOWED_HOSTS` - Your domain

### 4. Update .htaccess

Edit `.htaccess` and update paths:
```apache
PassengerAppRoot /home/yourusername/heo
PassengerPython /home/yourusername/virtualenv/heo/3.11/bin/python
```

### 5. Setup Python App in cPanel

Go to cPanel → Setup Python App:

1. Click "Create Application"
2. Configure:
   - **Python version**: 3.11 (or available version)
   - **Application root**: heo
   - **Application URL**: your-domain.com
   - **Application startup file**: passenger_wsgi.py
   - **Application Entry point**: application
3. Click "Create"

### 6. Install Dependencies

In cPanel terminal or SSH:
```bash
cd ~/heo
source ~/virtualenv/heo/3.11/bin/activate
pip install -r requirements.txt
```

Or run the deployment script:
```bash
cd ~/heo
chmod +x deploy.sh
./deploy.sh
```

### 7. Run Migrations

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 8. Restart Application

In cPanel → Setup Python App:
- Click "Restart" on your application

## Troubleshooting

### 500 Internal Server Error

1. Check error logs in cPanel → Errors
2. Verify `.env` file has correct values
3. Check file permissions: `.env` should be 600

### Static Files Not Loading

1. Run `python manage.py collectstatic`
2. Check `STATIC_ROOT` path in settings
3. Verify Apache is serving `/static/` correctly

### Database Connection Error

1. Verify database credentials in `.env`
2. Check database exists in cPanel
3. Ensure user has permissions

### Email Not Sending

1. Verify email credentials
2. For Gmail, use App Password
3. Check spam folder

## Updating the Site

```bash
cd ~/heo
source ~/virtualenv/heo/3.11/bin/activate
git pull  # or upload new files
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Then restart the app in cPanel.

## Security Checklist

- [ ] `DEBUG=False` in `.env`
- [ ] Unique `SECRET_KEY` generated
- [ ] `.env` file permissions set to 600
- [ ] SSL certificate installed
- [ ] Database password is strong
- [ ] Admin URL changed (optional)
