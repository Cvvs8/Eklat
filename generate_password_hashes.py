import bcrypt
import json

def hash_password(password):
    """Generate a bcrypt hash for a password."""
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def main():
    # Dictionary of users with their plaintext passwords and roles
    users_with_roles = {
        'ADMIN': {'password': 'Gabri3L2024', 'role': 'director'},
        'D-Cientifica': {'password': 'Dv655Ni3V', 'role': 'auditor'},
        'VR-vendor': {'password': '8pkV143Qo', 'role': 'user'},
        'JP-vendor': {'password': 'MS9m1Qk6', 'role': 'user'},
        'NE-vendor': {'password': '7I95hdAf5', 'role': 'user'},
        'XX-vendor': {'password': 'letmein', 'role': 'user'}
    }

    # Generate hashes and build the final dictionary
    hashed_users = {}
    for username, data in users_with_roles.items():
        hashed_users[username] = {
            'password': hash_password(data['password']),
            'role': data['role']
        }

    # Write the correct structure to users.json
    with open('users.json', 'w') as file:
        json.dump(hashed_users, file, indent=4)

    print("Hashed passwords and roles have been saved to users.json")

if __name__ == "__main__":
    main()