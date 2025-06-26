# main.py
from backend.db import init_oracle_client
from frontend.login import LoginPage

if __name__ == '__main__':
    init_oracle_client()
    login = LoginPage()
    login.mainloop()
