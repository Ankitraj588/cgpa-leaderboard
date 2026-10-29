import smtplib
import getpass

user = input("Gmail address: ").strip()
pw = getpass.getpass("App password (hidden): ").replace(" ", "").replace("\xa0", "")

for port in (465, 587):
    print(f"--- port {port} ---")
    try:
        if port == 465:
            s = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15)
        else:
            s = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
            s.starttls()
        s.login(user, pw)
        print("LOGIN OK")
        s.quit()
    except Exception as e:
        print(type(e).__name__, "-", e)
