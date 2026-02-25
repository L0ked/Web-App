from datetime import datetime
import time

def function_logger(log_file):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            start_timestamp = time.time()

            result = func(*args, **kwargs)

            end_time = datetime.now()
            duration = time.time() - start_timestamp

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(func.__name__ + '\n')
                f.write(str(start_time) + '\n')
                if args:
                    f.write(str(args) + '\n')
                if kwargs:
                    f.write(str(kwargs) + '\n')
                if result is not None:
                    f.write(str(result) + '\n')
                else:
                    f.write('-\n')
                f.write(str(end_time) + '\n')
                f.write(f"{duration:.6f}\n")

            return result
        return wrapper
    return decorator
