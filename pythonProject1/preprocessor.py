
import re
import pandas as pd
from datetime import datetime

def preprocess(data):
    # Fix the special narrow non-breaking space
    data = data.replace('\u202f', ' ')

    # Patterns
    pattern_12hr = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) (AM|PM|am|pm) - '
    pattern_24hr = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) - '

    if re.search(pattern_12hr, data):
        print("Detected 12-hour format chat")
        return preprocess_12hr(data, pattern_12hr)
    elif re.search(pattern_24hr, data):
        print("Detected 24-hour format chat")
        return preprocess_24hr(data, pattern_24hr)
    else:
        raise ValueError("Unknown chat format!")

def preprocess_12hr(data, pattern):
    messages = re.split(pattern, data)[1:]
    dates = []
    message_text = []

    for i in range(0, len(messages), 4):
        try:
            date = messages[i]
            time = messages[i + 1]
            ampm = messages[i + 2]
            msg = messages[i + 3]

            # Skip omitted media messages
            if re.search(r'\b\w*\s*omitted\b', msg, re.IGNORECASE):
                continue

            date_time_str = f"{date}, {time} {ampm.upper()}"
            try:
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y, %I:%M %p")
            except ValueError:
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%y, %I:%M %p")

            dates.append(date_time_obj)
            message_text.append(msg)
        except (IndexError, ValueError) as e:
            print(f"Skipping because of error: {e}")
            continue

    df = pd.DataFrame({'datetime': dates, 'message': message_text})
    return refine_dataframe(df, time_column='datetime')

def preprocess_24hr(data, pattern):
    messages = re.split(pattern, data)[1:]
    dates = []
    message_text = []

    for i in range(0, len(messages), 3):
        try:
            date = messages[i]
            time = messages[i + 1]
            msg = messages[i + 2]

            # Skip omitted media messages
            if re.search(r'\b\w*\s*omitted\b', msg, re.IGNORECASE):
                continue

            date_time_str = f"{date}, {time}"
            try:
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%Y, %H:%M")
            except ValueError:
                date_time_obj = datetime.strptime(date_time_str, "%d/%m/%y, %H:%M")

            dates.append(date_time_obj)
            message_text.append(msg)
        except (IndexError, ValueError) as e:
            print(f"Skipping because of error: {e}")
            continue

    df = pd.DataFrame({'datetime': dates, 'message': message_text})
    return refine_dataframe(df, time_column='datetime')

def refine_dataframe(df, time_column='datetime'):
    df = df.dropna(subset=[time_column])
    df[time_column] = pd.to_datetime(df[time_column])

    users = []
    messages = []

    for message in df['message']:
        if re.search(r'\b\w*\s*omitted\b', message, re.IGNORECASE):
            continue
        entry = extract_user_message(message)
        if entry:
            users.append(entry[0])
            messages.append(entry[1])
        else:
            users.append("group_notification")
            messages.append(message)

    df = df.iloc[:len(users)]
    df['user'] = users
    df['message'] = messages

    df['only_date'] = df[time_column].dt.date
    df['year'] = df[time_column].dt.year
    df['month_num'] = df[time_column].dt.month
    df['month'] = df[time_column].dt.month_name()
    df['day'] = df[time_column].dt.day
    df['day_name'] = df[time_column].dt.day_name()
    df['hour'] = df[time_column].dt.hour
    df['minute'] = df[time_column].dt.minute

    periods = []
    for hour in df['hour']:
        if hour == 23:
            periods.append(f"{hour}-0")
        else:
            periods.append(f"{hour}-{hour + 1}")
    df['period'] = periods

    return df

def extract_user_message(message):
    if message is None or message.strip() == "":
        return None
    if re.search(r'\b\w*\s*omitted\b', message, re.IGNORECASE):
        return None
    if ":" in message:
        parts = message.split(":", 1)
        if len(parts) == 2:
            return parts[0].strip(), parts[1].strip()
    return None





















# import re
# import pandas as pd
# from datetime import datetime
#
#
# def preprocess(data):
#     # Fix the special narrow non-breaking space
#     data = data.replace('\u202f', ' ')
#
#     # Pattern for 12-hour format
#     pattern = r'(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) (am|pm|AM|PM) - '
#
#     messages = re.split(pattern, data)[1:]
#     dates = []
#     message_text = []
#
#     for i in range(0, len(messages), 4):
#         try:
#             date = messages[i]
#             time = messages[i + 1]
#             ampm = messages[i + 2]
#             msg = messages[i + 3]
#
#             date_time_str = f"{date}, {time} {ampm.upper()}"
#             date_time_obj = datetime.strptime(date_time_str, "%d/%m/%y, %I:%M %p")  # Notice: %y for 2-digit year
#             dates.append(date_time_obj)
#             message_text.append(msg)
#         except (IndexError, ValueError) as e:
#             print(f"Skipping because of error: {e}")
#             continue
#
#     df = pd.DataFrame({'datetime': dates, 'message': message_text})
#
#     df = df.dropna(subset=['datetime'])
#     df['datetime'] = pd.to_datetime(df['datetime'])
#
#     users = []
#     messages = []
#
#     for message in df['message']:
#         entry = extract_user_message(message)
#         if entry:
#             users.append(entry[0])
#             messages.append(entry[1])
#         else:
#             users.append("group_notification")
#             messages.append(message)
#
#     df['user'] = users
#     df['message'] = messages
#
#     df['only_date'] = df['datetime'].dt.date
#     df['year'] = df['datetime'].dt.year
#     df['month_num'] = df['datetime'].dt.month
#     df['month'] = df['datetime'].dt.month_name()
#     df['day'] = df['datetime'].dt.day
#     df['day_name'] = df['datetime'].dt.day_name()
#     df['hour'] = df['datetime'].dt.hour
#     df['minute'] = df['datetime'].dt.minute
#
#     periods = []
#     for hour in df['hour']:
#         if hour == 23:
#             periods.append(f"{hour}-0")
#         else:
#             periods.append(f"{hour}-{hour + 1}")
#     df['period'] = periods
#
#     return df
#
#
# def extract_user_message(message):
#     if message is None or message.strip() == "":
#         return None
#     if ":" in message:
#         parts = message.split(":", 1)
#         if len(parts) == 2:
#             return parts[0].strip(), parts[1].strip()
#     return None
#
#











# import re
# import pandas as pd
#
# def preprocess(data):
#     pattern = '\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s'
#
#     messages = re.split(pattern, data)[1:]
#     dates = re.findall(pattern, data)
#
#     df = pd.DataFrame({'user_message': messages, 'message_date': dates})
#     # convert message_date type
#     df['message_date'] = pd.to_datetime(df['message_date'], format='%d/%m/%Y, %H:%M - ')
#
#     df.rename(columns={'message_date': 'date'}, inplace=True)
#
#     users = []
#     messages = []
#     for message in df['user_message']:
#         entry = re.split('([\w\W]+?):\s', message)
#         if entry[1:]:  # user name
#             users.append(entry[1])
#             messages.append(" ".join(entry[2:]))
#         else:
#             users.append('group_notification')
#             messages.append(entry[0])
#
#     df['user'] = users
#     df['message'] = messages
#     df.drop(columns=['user_message'], inplace=True)
#
#     df['only_date'] = df['date'].dt.date
#     df['year'] = df['date'].dt.year
#     df['month_num'] = df['date'].dt.month
#     df['month'] = df['date'].dt.month_name()
#     df['day'] = df['date'].dt.day
#     df['day_name'] = df['date'].dt.day_name()
#     df['hour'] = df['date'].dt.hour
#     df['minute'] = df['date'].dt.minute
#
#     period = []
#     for hour in df[['day_name', 'hour']]['hour']:
#         if hour == 23:
#             period.append(str(hour) + "-" + str('00'))
#         elif hour == 0:
#             period.append(str('00') + "-" + str(hour + 1))
#         else:
#             period.append(str(hour) + "-" + str(hour + 1))
#
#     df['period'] = period
#
#     return df
