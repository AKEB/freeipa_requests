# freeipa_requests

## Настройка

Необходимо переименовать файл ```.env.default``` в ```.env```. Или передавать ```host```, ```login``` и ```password``` в параметрах

## Сбросить пароль и OTP у одного пользователя

```./freeipa.sh -u <user_name> -g <group_name> -r -o```

Параметры

| Параметр           | Описание                   |
| ------------------ | -------------------------- |
| -H \<host\>        | freeipa host with https:// |
| -l \<login\>       | freeipa admin login        |
| -p \<password\>    | freeipa admin password     |
| -u \<username\>    | freeipa username           |
| -i \<otp_issuer\>  | otp issuer                 |
| -e \<enigma_host\> | enigma host                |
| -c                 | check login                |
| -g \<group\>       | add to group               |
| -r                 | reset password             |
| -o                 | reset otp                  |

## Сбросить пароль и OTP у списка пользователей

```./users_reset.sh -R users_reset.csv -W users_ready.csv -g <group_name> -r -o```

Параметры

| Параметр           | Описание                   |
| ------------------ | -------------------------- |
| -H \<host\>        | freeipa host with https:// |
| -l \<login\>       | freeipa admin login        |
| -p \<password\>    | freeipa admin password     |
| -i \<otp_issuer\>  | otp issuer                 |
| -e \<enigma_host\> | enigma host                |
| -W \<write_file\>  | csv write file             |
| -R \<read_file\>   | csv read file              |
| -c                 | check login                |
| -g \<group\>       | add to group               |
| -r                 | reset password             |
| -o                 | reset otp                  |

## Отправка писем всем по списку

```./mail_sender.sh -f users_ready.csv -t template_mail.txt```

Параметры

| Параметр                  | Описание               |
| ------------------------- | ---------------------- |
| -S \<smtp_server\>        | SMTP host              |
| -L \<smtp_username\>      | SMTP username          |
| -P \<smtp_password\>      | SMTP password          |
| -s \<sender_email\>       | Sender E-mail          |
| -f \<csv_file_name\>      | csv file name          |
| -t \<template_file_name\> | template for mail send |
| -b \<subject\>            | mail subject           |
| -a \<attach_file\>        | attach file name       |
