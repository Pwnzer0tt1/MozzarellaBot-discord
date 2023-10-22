# MozzarellaBot-discord
A Pwnzer0tt1 Bot with Mozzarella!

You find me in the pwnzer0tt1 server to manage user authentication and not only :D

If you want to use this bot, you need to create a `.env` file with the following variables, after that:

```bash
docker compose up -d --build
```

## ENV variables

| Variable           | Description                         | Required | Default            |
|--------------------|-------------------------------------|----------|--------------------|
| `MONGO_URL`        | Mongo DB URL to allow DB connection | Yes      | None               |
| `DB_NAME`          | Database name used on mongoDB       | No       | `mozzarellabot`    |
| `DISCORD_TOKEN`    | The discord token of the bot        | Yes      | None               |
| `EMAIL_FROM`       | Email From Field                    | No       | `info@pwnzer0tt1.it`    |
| `SMTP_SERVER`      | IP of SMTP server                   | No       | `127.0.0.1`        |
| `SMTP_SERVER_PORT` | PORT of SMTP server                 | No       | `587`              |
| `USER_SMTP`        | User for SMTP auth                  | No       | Same of EMAIL_FROM |
| `PSW_SMTP`         | Password for SMTP auth              | No       | ``                 |
| `GENERAL_TIMEOUT`  | Max duration of a Modal             | No       | 24\*60\*60 (1 day)   |

## Commands

| Command                  | Description                                                                                                       | Permissions |
|--------------------------|-------------------------------------------------------------------------------------------------------------------|-------------|
| `/admin`                 | Shows the admin panel (from here you can do different action)                                                     | Admin only  |
| `/clearchat`             | Delete all messages from the chat where this command is executed                                                  | Admin only  |
| `/generate_auth_channel` | Transform the current channel in the authentication channel (all messages will be deleted and permission changed) | Admin only  |
