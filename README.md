# Социальная сеть для авторов Yatube 

Благодаря этому проекту можно публиковать свои записи а также читать записи других авторов. Есть возможность подписываться на интересных пользователей и комментировать их записи. У пользователей есть возможность объединяться в группы по темам и интересам. 

Над проектом трудился [Роман Коблов](https://github.com/Roman-koblov/)

## Какие технологии и пакеты использовались:

* Python 3.8
* Django 2.2.16
* mixer 7.1.2
* Pillow 8.3.1
* pytest 6.2.4
* pytest-django 4.4.0
* pytest-pythonpath 0.7.3
* requests 2.26.0
* six 1.16.0
* sorl-thumbnail 12.7.0
* Faker 12.0.1

---
---


## Как разместить и запустить проект:
> *команды указаны для MacOS/Linux, на Windows используйте ~~python3 и pip3~~ python и pip*

Клонировать репозиторий и перейти в него в командной строке:

<pre><code>git clone [https://github.com/Roman-koblov/yatube_social_network]</code>

<code>cd yatube_social_network</code></pre>

Cоздать и активировать виртуальное окружение:

<pre><code>python3 -m venv venv</code>

<code>source venv/bin/activate</code></pre>

Установить зависимости из файла requirements.txt:

<pre><code>python3 -m pip install --upgrade pip</code>

<code>pip3 install -r requirements.txt</code></pre>

Выполнить миграции:

<pre><code>python3 manage.py migrate</code></pre>

Запустить проект:

<pre><code>python3 manage.py runserver</code></pre>

Создать суперпользователя:

<pre><code>python3 manage.py createsuperuser</code>

<code>Username (leave blank to use 'user'): # Придумайте логин (например, admin)</code>

<code>Email address: # укажите почту</code>

<code>Password: # придумайте пароль</code>

<code>Password (again): # повторите пароль</code>

<code>Superuser created successfully</code></pre>

- Интерфейс администратора доступен по адресу http://127.0.0.1:8000/admin/
- Адрес проекта http://127.0.0.1:8000/
