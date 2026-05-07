[app]

title = Рацион сотрудника
package.name = dietapp
package.domain = org.example
version = 0.1

source.dir = frontend/
source.include_exts = py,png,jpg,jpeg,json,kv

requirements = python3,kivy==2.3.1,kivymd==1.2.0,requests,pydantic,filetype,certifi,charset-normalizer

icon.filename = %(source.dir)s/default_avatar.png
presplash.filename = %(source.dir)s/default_avatar.png

android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.allow_backup = True
android.request_legacy_external_storage = True
orientation = portrait

[buildozer]
log_level = 2