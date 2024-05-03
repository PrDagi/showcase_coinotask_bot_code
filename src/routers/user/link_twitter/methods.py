from src.models import DbSession,User


def is_username_exist(x_user_id):
    with DbSession() as session:
        result = session.query(User).where(User.x_user_id==x_user_id).all()
        return bool(result)


def save_username(tg_user_id, x_user_id):
    with DbSession() as session:
        try:
            # Attempt to retrieve an existing user by tg_user_id
            existing_user = session.query(User).filter_by(tg_user_id=tg_user_id).one()
            # Update the existing user's data
            existing_user.x_user_id = x_user_id
            # Commit the changes
            session.commit()
        except Exception:
            # If no user with the given tg_user_id is found, create a new user
            new_user = User(tg_user_id=tg_user_id, x_user_id=x_user_id)
            session.add(new_user)
            session.commit()