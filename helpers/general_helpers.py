import traceback

try:
    print(4/0)
except ZeroDivisionError:
    print(traceback.format_exc())
