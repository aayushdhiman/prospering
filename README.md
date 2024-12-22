# prospering
My personal Discord utility bot. Current functionality is to accept and send reminders about tasks.

If you want to host it, clone the repo, enter your bot's token, and run `docker compose up -d`. 

Uses Python and discord.py (a Discord API wrapper). PostgreSQL for storing reminders, and spins up both the PostgreSQL database and the codebase in individual Docker containers. 

Runs indefinitely (for free!) on an Amazon EC2 instance. Used to run (also for free!) on an Oracle Cloud Infrastructure VM instance. I would recommend either if you are looking to host this or something similar. 