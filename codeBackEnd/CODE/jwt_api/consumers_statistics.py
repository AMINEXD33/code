from logs_util.log_core import LogCore
from .consumers_soft_records_system import SoftRecords
import json
from jwt_api.models import Session_user_tracking_record
log = LogCore("consumers_statistics.py", False)


def calculate_lines_of_code(code: str):
    """
    a function that calculates how mush words,lines are in a
    code, O(n) time complexity O(1) space complexity
    return (lines, words)
    """
    lines: int = 0
    if len(code) != 0:
        lines += 1
    words: int = 0
    space_break: bool = True
    for letter in code:
        if letter == "\n":
            lines += 1
        if (letter == " " or letter == "\n") and not space_break:
            space_break = True
        if (letter != " " and letter != "\n") and space_break:
            space_break = False
            words += 1
    return (lines, words)


def calculate_deltas(
    curr_lines: int,
    curr_words: int,
    curr_chars: int,
    prev_lines: int,
    prev_words: int,
    prev_chars: int,
):
    """
    a function that calculates the delta (diffrence)
    of lines, words
    return (lines_delta, words_delta)
    """
    lines_delta = prev_lines - curr_lines
    words_delta = prev_words - curr_words
    return (lines_delta, words_delta)


def code_statistics_routine(code: str, sfr: SoftRecords, username: str, session_id: str):
    try:
        # calculate some stats about the code
        curr_lines, curr_words = calculate_lines_of_code(code)

        # to calculate delta we need passed stats
        pass_lines = sfr.get_user_field(
            session_id=session_id, username=username, field_name="line_code"
        )
        pass_sum_lines = sfr.get_user_field(
            session_id=session_id, username=username, field_name="sum_line_code"
        )
        pass_words = sfr.get_user_field(
            session_id=session_id, username=username, field_name="words"
        )
        pass_sum_words = sfr.get_user_field(
            session_id=session_id, username=username, field_name="sum_words"
        )
        #update curr lines and words
        sfr.user_update_field(session_id=session_id, username=username, update_tuple=("line_code", curr_lines))
        sfr.user_update_field(session_id=session_id, username=username, update_tuple=("words", curr_words))
        
        # calculating deltas
        lines_delta = curr_lines - int(pass_lines)
        words_delta = curr_words - int(pass_words)
        # saving deltas
        sfr.user_update_field(
            session_id=session_id,
            username=username,
            update_tuple=("lines_delta", lines_delta),
        )
        sfr.user_update_field(
            session_id=session_id,
            username=username,
            update_tuple=("words_delta", words_delta),
        )

        # Note : to store the summurized data the sum_line_code and sum_words we're going to store every fifth
        # submition
        modification = sfr.get_user_field(
            session_id=session_id, username=username, field_name="modification"
        )
        print(f"""
            curr_lines = {curr_lines}
            curr_words = {curr_words}
            modification = {modification}
            lines_delta = {lines_delta}
            words_delta = {words_delta}
        """)
        if int(modification) >= 2:
            # we're adding this data to the summurized lists
            pass_sum_lines = json.loads(pass_sum_lines)
            pass_sum_words = json.loads(pass_sum_words)
            print(f"""
                pass_sum_lines = {pass_sum_lines} 
                pass_sum_words =  {pass_sum_words}
            """)
            # append the new data
            pass_sum_lines.append(curr_lines)
            pass_sum_words.append(curr_words)
            print(f"""
                pass_sum_lines = {pass_sum_lines} 
                pass_sum_words =  {pass_sum_words}
            """)

            # save
            sfr.user_update_field(
                session_id=session_id,
                username=username,
                update_tuple=("sum_line_code", tuple(pass_sum_lines)),
            )
            sfr.user_update_field(
                session_id=session_id,
                username=username,
                update_tuple=("sum_words", tuple(pass_sum_words)),
            )
            # reseting the modification counter
            sfr.user_update_field(
                session_id=session_id, username=username, update_tuple=("modification", 0)
            )
        else:
            # increment the modification counter
            sfr.user_update_field(
                session_id=session_id,
                username=username,
                update_tuple=("modification", int(modification)+1),
            )
        # updating the code
        sfr.user_update_field(
            session_id=session_id,
            username=username,
            update_tuple=("code", code),
        )
    except Exception as e:
        log.log_exception(str(e))

def get_new_user_stats(self, session_id:str, username:str, sfr: SoftRecords):
    data = {
        "errors":None,
        "submitions":None,
        "compilations":None,
        "line_code":None,
        "sum_line_code":None,
        "words":None,
        "sum_words":None,
        "sus":None,
        "code":None,
        "activityStartedAt":None,
        "activityEndedAt":None,
        "modification":None,
        "lines_delta":None,
        "words_delta":None,
    }
    for key in data:
        data[key] = sfr.get_user_field(session_id=session_id, username=username, field_name=key)
    # dumps
    data = json.dumps(data)
    return data

def get_new_master_stats(self, session_id:str, username:str, sfr: SoftRecords):
    data = {
        "totallines":None,
        "totalwords":None,
        "blocked_students":None,
        "totalCodeCompexity":None,
        "totalStudentsdone":None,
        "activity":None,
        "ttl":None,
    }
    for key in data:
        data[key] = sfr.get_master_field(session_id=session_id, field_name=key)
    # dumps
    data = json.dumps(data)
    return data

def commit_user_stats(expected_data: dict):
    map_ = (
        ("line_code"),
        ("words"),
        ("code"),
        ("sum_line_code"),
        ("sum_words"),

    )

def calculate_stats(session_id:str, sfr: SoftRecords):
    """
    this function calculates the average words, lines, errors, and complexity of the whole users
    in a session.
    NOTE : this function calculates this bassed on data in redis , it could give some
    innacurate data in some side cases
    Parameters
    ----------
    session_id : str
        the id of the target session
    sfr : SoftRecords
        instance of a SoftRecords class
    
    Return
    ------
    if no users are in session : None

        return {
        "avg_words":post_calc_avg_words,
        "avg_lines":post_calc_avf_lines,
        "avg_errors":post_calc_avg_errors,
        "avg_complexity":post_calc_avg_code_complexity,
    }

    """
    users = sfr.get_master_field(session_id=session_id, field_name="users")
    if users:
        users = json.loads(users)
    else:
        return None
    if len(users) <= 0:
        return None
    avg_words = [0, 0]
    avg_lines = [0, 0]
    avg_errors = [0, 0]
    avg_code_complexity = [0, 0]
    avg_delta_words = [0, 0]
    avg_delta_lines = [0, 0]

    post_calc_avg_words = 0
    post_calc_avf_lines = 0
    post_calc_avg_errors = 0
    post_calc_avg_code_complexity = 0
    total_student_blocked = 0
    post_calc_avg_delta_line = 0
    post_calc_avg_delta_words = 0

    for user in users:
        try:
            username = user[1]
            # int
            user_words = int(sfr.get_user_field(session_id=session_id, username=username, field_name="words"))
            # print(f"user_words = {user_words}")
            if user_words:
                avg_words[0] += user_words
                avg_words[1] += 1
            # int
            user_lines = int(sfr.get_user_field(session_id=session_id, username=username, field_name="line_code"))
            # print(f"user_lines = {user_lines}")
            if user_lines:
                avg_lines[0] += user_lines
                avg_lines[1] += 1
            # int
            user_errors = json.loads((sfr.get_user_field(session_id=session_id, username=username, field_name="errors")))
            # print(f"user_errors = {user_errors}")
            if user_errors:
                avg_errors[0] += 0#len(user_errors)
                avg_errors[1] += 1
            # int
            user_complexity = sfr.get_user_field(session_id=session_id, username=username, field_name="code_complexity")
            # print(f"user_complexity = {user_complexity}")
            if user_complexity:
                avg_code_complexity[0] += int(user_complexity)
                avg_code_complexity[1] += 1
            user_blocked = sfr.get_user_field(session_id=session_id, username=username, field_name="blocked")
            if user_blocked == "True":
                total_student_blocked+=1
            delta_words = sfr.get_user_field(session_id=session_id, username=username, field_name="words_delta")
            if delta_words:
                avg_delta_words[0] += int(delta_words)
                avg_delta_words[1] += 1
            delta_lines = sfr.get_user_field(session_id=session_id, username=username, field_name="lines_delta")
            if delta_lines:
                avg_delta_lines[0] += int(delta_lines)
                avg_delta_lines[1] += 1
            
                
            
            if  avg_words[1] != 0:
                post_calc_avg_words = avg_words[0]/avg_words[1]
            if  avg_lines[1] != 0:
                post_calc_avf_lines =  avg_lines[0]/avg_lines[1]
            if  avg_errors[1] != 0:
                post_calc_avg_errors= avg_errors[0]/avg_errors[1]
            if  avg_code_complexity[1] != 0:
                post_calc_avg_code_complexity= avg_code_complexity[0]/avg_code_complexity[1]
            if avg_delta_lines[1] != 0:
                post_calc_avg_delta_line = avg_delta_lines[0]/avg_delta_lines[1]
            if avg_delta_words[1] != 0:
                post_calc_avg_delta_words = avg_delta_words[0]/avg_delta_words[1]
        except Exception as e:
            log.log_exception("calculate_all_avg_data_memo > "+str(e))
    return {
        "avg_words":post_calc_avg_words,
        "avg_lines":post_calc_avf_lines,
        "avg_errors":post_calc_avg_errors,
        "avg_complexity":post_calc_avg_code_complexity,
        "total_students_blocked":total_student_blocked,
        "avg_lines_delta":post_calc_avg_delta_line,
        "avg_words_delta":post_calc_avg_delta_words
    }




    
