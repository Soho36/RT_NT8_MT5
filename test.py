
position_state_path = 'C:\\Users\\Liikurserv\\PycharmProjects\\RT_Ninja\\position_state.txt'


def get_position_state():
    with open(position_state_path, 'r', encoding='utf-8') as file:
        state = file.read()
    if state == 'opened':
        return True


contents = get_position_state()
print(contents)
