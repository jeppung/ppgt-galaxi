import pickle
from pathlib import Path

import streamlit_authenticator as stauth

# name = ["Peter Parker", "Rebecca Miller"]
# username = ["pparker", "rmiller"]
# password = ["XXX", "XXX"]

hashed_passwords = stauth.Hasher(['ppgtgalaxi2022$']).generate()
print(hashed_passwords)

# file_path = Path(__file__).parent/"hashed_pw.pkl"
# with file_path.open("wb") as file:
#     pickle.dump(hashed_passwords, file)
