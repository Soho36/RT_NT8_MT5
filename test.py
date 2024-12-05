mt5_logging_file_path = f'E:\\YandexDisk\\Desktop_Zal\\44444.txt'


def leave_only_last_line():     # Clear file before starting the script
    with open(mt5_logging_file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        if lines:
            # Check if there's at least one line to keep
            lines_to_write_back = lines[-5:]
            with open(mt5_logging_file_path, 'w', encoding='utf-16') as file:
                file.write(''.join(lines_to_write_back))  # Write only the first line back to the file

        return lines_to_write_back


file_contents = leave_only_last_line()
print(file_contents)
