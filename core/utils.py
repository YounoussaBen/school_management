def get_grade_letter(score):
    if 90 <= score <= 100:
        return 'A+'
    elif 85 <= score < 90:
        return 'A'
    elif 80 <= score < 85:
        return 'A-'
    elif 76 <= score < 80:
        return 'B+'
    elif 72 <= score < 76:
        return 'B'
    elif 68 <= score < 72:
        return 'B-'
    elif 64 <= score < 68:
        return 'C+'
    elif 60 <= score < 64:
        return 'C'
    elif 57 <= score < 60:
        return 'C-'
    elif 54 <= score < 57:
        return 'D+'
    elif 51 <= score < 54:
        return 'D'
    elif 49 <= score < 51:
        return 'D-'
    else:
        return 'F'


def get_gpa(score):
    if 90 <= score <= 100:
        return 4.0
    elif 85 <= score < 90:
        return 3.7
    elif 80 <= score < 85:
        return 3.3
    elif 75 <= score < 80:
        return 3.0
    elif 70 <= score < 75:
        return 2.7
    elif 65 <= score < 70:
        return 2.3
    elif 60 <= score < 65:
        return 2.0
    elif 55 <= score < 60:
        return 1.7
    elif 50 <= score < 55:
        return 1.3
    elif 45 <= score < 50:
        return 1.0
    else:
        return 0.0

