while True: eval(["exit()" if all(i in "QWERTYUIOPASDFGHJKLZXCVBNM" for i in user) and user.upper() == user and len(set(user)) == len(user) and sum([ord(i) for i in user]) >= 420 and sum([ord(i) for i in user]) <= 600 and len(user) >= 5 and len(user) <= 7 else "print ('Not Valid!')" for user in [input("> ")]][0])