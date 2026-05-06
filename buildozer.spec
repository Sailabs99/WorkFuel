[app]

title = Рацион сотрудника
package.name = dietapp
package.domain = org.example

source.dir = frontend/
source.include_exts = py,png,jpg,jpeg,json,kv

requirements = python3,kivy==2.3.1,kivymd==1.2.0,requests,pydantic,faker

icon.filename = %(source.dir)s/default_avatar.png
presplash.filename = %(source.dir)s/default_avatar.png

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
orientation = portrait
android.allow_backup = True