'''
/*
/* functions for working with strings containing integers type
/*
'''


def check_int(str):
    return str[1:].isdigit() if str[0] in ('-', '+') else str.isdigit()


def convert_str_to_int(str):
    return int(str) if check_int(str) else None 


'''
/*
/* functions for working with strings containing float type
/*
'''

def check_float(str):
    try:
        float(str)
        return True
    except ValueError:
        return False


def convert_str_to_float(str):
    return float(str) if check_float(str) else None


'''
/*
/* functions for working with strings containing bool type
/*
'''

def check_bool(_str):
    if _str.strip().lower() in ('true', 'false'):
        return True
    
    return False


def convert_str_to_bool(_str):
    return bool(_str) if check_bool(_str) else None


'''
/*
/* functions for working with strings containing switch type
/*
'''

def check_switch(_str):
    if _str.strip().lower() in ('on', 'off'):
        return True
    
    return False


def convert_str_to_switch(_str):
    if check_switch(_str):
        return True if _str.strip().lower() == 'on' else False
    
    return None


def string_equal(str1: str, str2: str) -> bool:
    return str1 == str2