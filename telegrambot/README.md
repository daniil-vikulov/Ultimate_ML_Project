## Telegram bot:
You can test the bot yourself, link: [detect bot](https://t.me/nuddetectbot)

You can see the main code in file `trybot.py`, add your token to the file `token_bot.py` for correct work

Telegram bot may be added to groups (give it admin rights to work well and make your chat history visible for new
members), or you can message the bot (private chat). 
Use `/help` command to find out about all functionalities.

File `minibot_server.py` was used to test connection with server (located in `backend/src/app/app.py`)

All tests are located in `tests` directory, files `test1.jpg`, `test1_censored.jpg`, `test2.jpg`, `test2_censored.jpg` are needed for tests to pass correctly

1) `test_censor.py` tests the work of `censor.py` + tests that `nudedetector.censor(file)` works well
2) `test_os.py` tests interactions with os
3) `test_trybot.py` contains all the main tests for `trybot.py`

### Links

I learned how to make telegram bot using this [video course](https://www.youtube.com/watch?v=axGHFAHlJP8&list=PLmSBSL0-aSglhQu_apL_4GM8VbUKuL2J)

How to write python [unittests](https://www.youtube.com/watch?v=6tNS--WetLI)

About unittest.mock: [link](https://www.youtube.com/watch?v=xT4SV7AH3G8), [link](https://www.youtube.com/watch?v=-F6wVOlsEAM)

