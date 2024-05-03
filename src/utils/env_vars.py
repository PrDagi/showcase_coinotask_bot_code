from dotenv import dotenv_values, set_key

env_vars = dotenv_values("config.env")


def get_env_var(var_name: str):
  return env_vars[var_name]


def set_env_var(key: str, value):
  is_set = set_key("config.env", key, value)
  if is_set:
    return True
