# psi-environment

## Jak używać

Zainstalowanie biblioteki wraz ze wszystkimi potrzebnymi dependencjami:

```console
$ cd /path/to/this/repo
$ pip install -e .
```

Podanie flagi -e sprawi, że biblioteka zainstaluje się jako editable i każda zmiana w kodzie będzie już widoczna gdziekolwiek
gdzie biblioteka jest używana. Inaczej trzebaby instalować ponownie bibliotekę po każdej zmianie.

Aby zainstalować biblioteki przydatne do pracy nad biblioteką:

```console
$ pip install .[dev]
```

Sprawdzenie czy biblioteka poprawnie się zainstalowała:

```console
$ python
Python 3.10.14 (main, May  6 2024, 19:42:50) [GCC 11.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from psi_environment.main import hello_world
>>> hello_world()
Hello World!
```