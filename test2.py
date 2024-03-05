from datetime import datetime

print(datetime.now() < datetime.strptime('22:00', '%H:%M'))