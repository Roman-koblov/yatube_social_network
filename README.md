# Социальная сеть для авторов Yatube 

Социальная сеть для блогеров

## Описание

Благодаря этому проекту можно будет публиковать свои записи а также читать записи других авторов. Есть возможность подписываться на интересных пользователей и комментировать их записи. У пользователей есть возможность объединяться в группы по темам и интересам. 

### Технологии

- Python 3.8.9
- Django 2.2.19

### Запуск проекта в dev-режиме

Клонировать репозиторий и перейти в него в командной строке:

<pre><code>git clone [https://github.com/Roman-koblov/yatube_social_network]</code>

<code>cd yatube_social_network</code></pre>

Cоздать и активировать виртуальное окружение:

<pre><code>python3 -m venv venv source venv/bin/activate</code></pre>

Установить зависимости из файла requirements.txt:

<pre><code>python -m pip install --upgrade pip</code>

<code>pip install -r requirements.txt</code></pre>

Выполнить миграции:

<pre><code>python3 manage.py migrate</code></pre>

----------------------------------------------------------------------------

### Автор

Коблов Роман
