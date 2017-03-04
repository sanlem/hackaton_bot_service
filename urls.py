from handlers import main


urlpatterns = [
    (r'/', main.MainHandler),
    (r'/telegram/', main.TelegramHandler)
]
