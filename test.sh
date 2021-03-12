docker-compose -f dc-bot.test.yml -f dc-bot.yml build && docker-compose -f dc-bot.yml -f dc-bot.test.yml up && docker-compose -f dc-bot.yml -f dc-bot.test.yml logs -f
