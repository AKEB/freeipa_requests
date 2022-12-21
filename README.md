# freeipa_requests

## Настройка

Необходимо переименовать файл ```.env.default``` в ```.env```. Или передавать ```host```, ```login``` и ```password``` в параметрах

## Сбросить пароль и OTP у одного пользователя

```./freeipa.sh -u <user_name> -g <group_name> -r -o```

Параметры

| Параметр        | Описание                   |
| --------------- | -------------------------- |
| -H \<host\>     | freeipa host with https:// |
| -l \<login\>    | freeipa admin login        |
| -p \<password\> | freeipa admin password     |
| -u \<username\> | freeipa username           |
| -c              | check login                |
| -g \<group\>    | add to group               |
| -r              | reset password             |
| -o              | reset otp                  |

## Сбросить пароль и OTP у списка пользователей

```./users_reset.sh -g <group_name> -r -o```

Параметры

| Параметр        | Описание                   |
| --------------- | -------------------------- |
| -H \<host\>     | freeipa host with https:// |
| -l \<login\>    | freeipa admin login        |
| -p \<password\> | freeipa admin password     |
| -c              | check login                |
| -g \<group\>    | add to group               |
| -r              | reset password             |
| -o              | reset otp                  |
