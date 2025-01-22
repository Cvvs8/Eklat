import bcrypt
import json

def hash_password(password):
    """Generate a bcrypt hash for a password."""
    password_bytes = password.encode('utf-8')  # Ensure the password is encoded to bytes
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())  # Generate the hash
    return hashed.decode('utf-8')  # Decode the hash to store in JSON as a string

def main():
    # Dictionary of users and their corresponding plaintext passwords
    users = {
        'ADMIN': 'Gabri3L2024',
        'VR-vendor': '8pkV143Qo',
        'JP-vendor': 'MS9m1Qk6',
        'NE-vendor': '7f5AI95hd',
        'XX-vendor': 'letmein',
        'D-Cientifica': 'Dv655Ni3V'
    }

    # Generate hashes for each user
    hashed_users = {username: hash_password(pw) for username, pw in users.items()}

    # Write the hashed passwords to users.json
    with open('users.json', 'w') as file:
        json.dump(hashed_users, file, indent=4)

    print("Hashed passwords have been saved to users.json")

if __name__ == "__main__":
    main()


