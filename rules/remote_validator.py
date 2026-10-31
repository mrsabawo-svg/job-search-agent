def validate_remote(workplace: str) -> list[str]:
    return [] if workplace.strip().lower() == 'remote' else ['not_remote']
