
# Network 3
Конькова Мария 166

Для запуска приложения необходимо:

1) В перменные окружения добавить информацию

  `PORT` - порт сервера
  
  `HOST` - хост сервера

2) Используются библиотеки питона:

`os`, `socket`, `json`

3) Программы запускаются `python3 client.py`

4) Клиент настроен на работу в виде диалога с пользователем

```Hello! It's the right time to buy or sell car!
Username: 1
Please, type password
Password: 2
Welocme, 1
Your command (may use "HELP"): BUY
Would yoy like see all park? (y/n): n
Please, type models you would like (if all, type all): peugeot toyota
Please, type colors you would like (if all, type all): red black
Please, type the lowest year (if all, type all): all
Plese, type the highest year (if all, type all): all
Please, type the lowest price (if all, type all): all
Plese, type the highest price (if all, type all): all
Listing cars:

toyota black 2015 800000
Would you like to buy anything? (y/n): n
Your command (may use "HELP"): BYE
See you next time, 1```
