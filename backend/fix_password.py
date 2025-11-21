#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script to fix password for SNB001000 user."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db.config import load_database_config
from db.engine import create_db_engine, get_session_factory, session_scope
from db.models import User
from db.utils.security import hash_password, verify_password
from sqlalchemy import select

def fix_user_password():
    config = load_database_config()
    engine = create_db_engine(config)
    session_factory = get_session_factory(engine)
    
    with session_scope(session_factory) as session:
        # Find user SNB001000
        user = session.execute(
            select(User).where(User.customer_number == "SNB001000")
        ).scalars().first()
        
        if not user:
            print("ERROR: User SNB001000 not found in database!")
            print("Please run: cd backend && python db/seed.py")
            return False
        
        print("Found user: {} ({} {})".format(
            user.customer_number, user.first_name, user.last_name
        ))
        
        # Expected password
        expected_password = "Sun@1000"
        print("Expected password: {}".format(expected_password))
        
        # Check current password
        if user.password_hash:
            current_valid = verify_password(expected_password, user.password_hash)
            print("Current password hash valid: {}".format(current_valid))
            
            if current_valid:
                print("[OK] Password is already correct!")
                return True
            else:
                print("[FIX] Password hash is incorrect, fixing...")
        else:
            print("[FIX] No password hash found, creating...")
        
        # Fix password
        user.password_hash = hash_password(expected_password)
        session.flush()
        
        # Verify it works
        new_valid = verify_password(expected_password, user.password_hash)
        if new_valid:
            print("[OK] Password fixed successfully!")
            print("  User ID: {}".format(user.customer_number))
            print("  Password: {}".format(expected_password))
            return True
        else:
            print("[ERROR] Password verification failed after fix!")
            return False

if __name__ == "__main__":
    success = fix_user_password()
    sys.exit(0 if success else 1)

