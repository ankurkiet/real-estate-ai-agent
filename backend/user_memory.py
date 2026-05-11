user_sessions = {}


def get_user_memory(user_id):

    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    return user_sessions[user_id]

def set_user_memory(user_id, memory):

    user_sessions[user_id] = memory
    

def update_user_memory(user_id, new_data):

    memory = get_user_memory(user_id)

    for key, value in new_data.items():

        if value is not None:
            memory[key] = value

    return memory



def clear_user_memory(user_id):

    if user_id in user_sessions:
        user_sessions[user_id] = {}