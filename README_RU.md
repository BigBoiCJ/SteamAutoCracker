# SteamAutoCracker
![GitHub all releases](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/total?color=brightgreen&label=Total%20downloads)
![GitHub release (latest by date)](https://img.shields.io/github/downloads/BigBoiCJ/SteamAutoCracker/latest/total?color=green&label=Latest%20version%20downloads)
![GitHub Repo stars](https://img.shields.io/github/stars/BigBoiCJ/SteamAutoCracker?color=yellow&label=Stars)
![GitHub watchers](https://img.shields.io/github/watchers/BigBoiCJ/SteamAutoCracker?label=Watchers)

Скрипт с открытым исходным кодом, который автоматически взламывает (удаляет DRM из) игры в Steam

## Как использовать (простой способ)
- Загрузите скомпилированную версию, нажав [здесь](https://github.com/BigBoiCJ/SteamAutoCracker/releases/latest) и скачав файл с именем `Steam.Auto.Cracker.GUI.vX.X.X.zip`.
- Распакуйте содержимое архива (.zip) на свой компьютер
- Запустите `steam_auto_cracker_gui.exe`
- Выберите папку с игрой
- Введите название игры, чтобы попытаться взломать ее! (Вы также можете ввести идентификатор Steam AppID, если он вам известен)
  - SAC автоматически попытается найти AppID по указанному вами имени. Если это не удастся, попробуйте ввести AppID самостоятельно.
  - Вы можете найти AppID в URL-адресе страницы игры в Steam. (ex: store.steampowered.com/app/-> ***620980*** <-/Beat_Saber/)

## Характеристики
- Автоматически взламывает купленные или пиратские игры Steam. Вам нужно только выбрать папку с игрой и ввести название игры или AppID.
  - Взламывает **Steam API DRM**, автоматически применяя и настраивая **Steam Emulators**.
  - Взламывает **Steam Stub DRM**, автоматически применяя **Steamless** к исполняемым файлам
- Учетная запись Steam или ключ Steam API не требуются
- Настраивается по вашему желанию
- Возможность разблокировать только DLC для купленных в Steam игр, а не взламывать их полностью
- Возможность выбрать свой собственный Steam Emu благодаря простому списку и простой системе шаблонов конфигов (по умолчанию: ALI213)
  - Список Steam emus, включенных по умолчанию:
    - ALI213 (Игра/Game)
    - Goldberg (Игра/Game)
    - CreamAPI (Дополнение/DLC)
- Открытый исходный код, прозрачность и конфиденциальность. Никакой скрытой аналитики или странных вещей!
- Автообновление и проверка версий. Подписка на конфиденциальность!

## Скриншоты
Скриншоты версии v2.0.0

<details>
<summary>Картинки</summary>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/6b9cd91e-9ff1-42a2-9efb-09586d41dbd3" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/039d5af8-1bad-47ec-b4c0-b164cc0388eb" width=50% height=50%>
<img src="https://github.com/BigBoiCJ/SteamAutoCracker/assets/101492671/25f0c44c-262f-4358-b694-fb0792bbcf52" width=50% height=50%>
</details>

## Требования
- Подключение к Интернету (SAC будет делать запросы на `steampowered.com` для получения AppID и DLC)
- Если вы используете скомпилированный .exe:
  - 64 бит Windows
- Если вы используете файл python (источник):
  - Модуль `requests`. Установите с помощью `py -m pip install requests` или `python -m pip install requests` или `python3 -m pip install requests`.
  - Модуль `pywin32` (который содержит win32api). Установите с помощью `py -m pip install pywin32` или `python -m pip install pywin32` или `python3 -m pip install pywin32`.
    - Если у вас возникли проблемы, пожалуйста, проверьте https://pypi.org/project/pywin32/.
  - Модуль `tkinter`, но он должен быть включен в Python по умолчанию.
  - Начиная с версии 2.2.0 GUI, также требуется модуль `tkinterdnd2` (v0.4.0+). Установите его с помощью `py -m pip install tkinterdnd2`. ([pypi link](https://pypi.org/project/tkinterdnd2/) - [github link](https://github.com/Eliav2/tkinterdnd2))
  - Рекомендованная версия Python 3.7+.

## Заметки о Дополнениях/DLC
Некоторые DLC в некоторых играх требуют загрузки дополнительных файлов.\
Этот инструмент не может загрузить эти файлы, вам придется получить их чистую версию.

Вы можете получить чистые файлы Steam для игр (и иногда DLC) в разделе [Steam Content Sharing с сайта cs.rin.ru](https://cs.rin.ru/forum/viewforum.php?f=22)

## Информация о сборке Windows
Скомпилировано с помощью [pyinstaller](https://pypi.org/project/pyinstaller/) и venv\
Ранее он был скомпилирован с помощью [auto-py-to-exe](https://pypi.org/project/auto-py-to-exe/) (который является просто графическим интерфейсом для pyinstaller)

Инструкции по компиляции SAC, а также полезные скрипты можно найти здесь: https://github.com/BigBoiCJ/SteamAutoCracker/tree/compile-env

## Конфиденциальность
SAC будет делать запросы на `steampowered.com` (официальный сайт Steam), чтобы получить AppID и DLC.\
Это не запрещено и не создаст вам проблем.

SAC будет выполнять запросы к этому репозиторию GitHub для проверки обновлений, загрузки автообновления и новых выпусков.\
Это произойдет только в том случае, если вы решите вручную нажать на кнопку «Проверить наличие обновлений» и решите обновляться с помощью автоапдейтера. SAC также может автоматически проверять наличие обновлений, если включить эту опцию в настройках (по умолчанию она отключена).

Ничего не регистрируется SAC.\
Вы можете удалить папку SAC в любое время, и в ней не останется никаких остатков. *

__* Исключение для остатков:__
- Если вы используете скомпилированный exe-файл, в нем останутся остатки. Это связано с тем, как работает PyInstaller / auto-py-to-exe. Встроенная версия Python и сам скрипт python будут извлечены в папку temp вашей ОС. Папка будет названа `_MEIxxxxxx`, где xxxxxx - случайное число. Вы можете удалить эту папку в любое время после использования программы, так как она может удалиться не во всех случаях. Пожалуйста, ознакомьтесь с документацией [pyinstaller](https://pyinstaller.org/en/stable/operating-mode.html#how-the-one-file-program-works) для получения дополнительной информации.

## Обнаружение вирусов
Некоторые файлы могут быть обнаружены вирусом. Самым большим нарушителем является `sac_emu/game_ali213/files/steam_api.dll`.\
Многие инструменты для взлома обнаруживаются как вредоносное ПО либо потому, что их поведение вызывает подозрения (обход защиты игры), либо потому, что они были отмечены вручную (это происходит со многими инструментами).\
Если вы сомневаетесь в легитимности файлов, просто удалите DLL-библиотеки и используйте вместо них свои собственные.\
Вы можете обсудить с другими людьми этот инструмент в [cs.rin.ru](https://cs.rin.ru/forum/viewtopic.php?f=10&t=120610) или в вопросах на GitHub.

## Благодарности
- Спасибо [atom0s for their Steamless project](https://github.com/atom0s/Steamless)
- Спасибо [oureveryday for their Steamless fork, supporting command-line](https://github.com/oureveryday/Steamless_CLI) (no longer used)
- Спасибо создателям Steam Emus, а именно тем, кто в него входит: ALI213, Goldberg и deadmau5 (создатель CreamAPI).
- Спасибо CS.RIN.RU и его членам за помощь и качественные загрузки
- Спасибо нашим соавторам, которые предлагают код, сообщают о проблемах и дают предложения! Наиболее заметные из них будут приведены в примечаниях к релизам
  - Даже если вас не отметили, это не значит, что вы не помогли! Я благодарю всех :heart:
