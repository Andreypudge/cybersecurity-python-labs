import string

UPPERCASE_CHARS = set(string.ascii_uppercase)
SPECIAL_CHARS = set(string.punctuation)
DIGIT_CHARS = set(string.digits)

passwords = [
    "Digital@F0r3nsics",
    "plain",
    "Encrypt10n@Key",
    "member",
    "Security@Audit2023",
    "regular",
    "Hack3r@D3fense",
    "ordinary",
    "Threat@Intel",
    "usual",
]

criteria = {
    "min_length": 8,
    "require_digits": True,
    "require_upper": True,
    "require_special": True,
}

forbidden_passwords = {"plain", "member", "regular", "ordinary", "usual", "user"}


def check_passwd(password):
    if password in forbidden_passwords or len(password) < 8:
        return False

    big = 0
    spec = 0
    digit = 0

    for char in password:
        if char in UPPERCASE_CHARS:
            big += 1
        if char in SPECIAL_CHARS:
            spec += 1
        if char in DIGIT_CHARS:
            digit += 1

    return big > 0 and spec > 0 and digit > 0


for passwd in passwords:
    if check_passwd(passwd):
        print(f"{passwd} -> Valid")
    else:
        print(f"{passwd} -> Invalid")
