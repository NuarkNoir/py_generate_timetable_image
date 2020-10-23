import requests
import datetime
from image_utils import ImageText

font_extra_bold = "fonts/MontserratAlternates-ExtraBold.ttf"
font_light = "fonts/MontserratAlternates-Light.ttf"
font_light_italic = "fonts/MontserratAlternates-LightItalic.ttf"
font_medium = "fonts/MontserratAlternates-Medium.ttf"

weekdays = [
    "понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"
]

color = (50, 50, 50)
sib_color = (0xFF, 0x8A, 0x0F)
unk_color = (0x4B, 0x3C, 0xBA)
type_color = {
    "лекция": (0x38, 0x8E, 0x3C),
    "практика": (0xE6, 0x4A, 0x19),
    "лабораторная работа": (0xBA, 0x3C, 0xBA),
    "семинар": (0x00, 0x79, 0x6B)
}


def get_color_for_type(_type: str) -> tuple:
    return type_color.get(_type, unk_color)


def get_sub_for_day(week: int, day: int):
    return f"{weekdays[day-1]} {['', 'не'][week % 2]}чётной недели".capitalize()


def draw_element(image: ImageText, data: dict, shift_x: int):
    title = data["subject"]
    time = f"Время: {data['time']}"
    sub_message = f"{data['teacher'] or '???'} в {data['place'] or '???'}"
    t_color = get_color_for_type(data['type'])
    image.write_text_box((50, shift_x), title, box_width=900, font_filename=font_extra_bold, font_size=25, color=t_color)
    image.write_text_box((50, shift_x + 50), time, box_width=900, font_filename=font_medium, font_size=25, color=color)
    image.write_text_box((50, shift_x + 75), sub_message, box_width=900, font_filename=font_light, font_size=25, color=color)


def draw_timetable(target: str, week: int, day: int, is_today: bool=False) -> ImageText:
    data: list = requests.get(f"http://edu.sfu-kras.ru/api/timetable/get?target={target}&week={week}&day={day}").json().get("timetable", [])

    # height: top padding + title + subtitle + (height of all elements || 'empty' message)
    dimensions = 1000, 50 + 90 + 30 + (150 * len(data) if data else 75)
    img = ImageText(dimensions, background=(255, 255, 255, 200))  # 200 = alpha

    title = f"Расписание занятий для {target}"
    sub_title = get_sub_for_day(week, day)
    if is_today:
        sub_title += " " + datetime.datetime.now().strftime("%d.%m.%Y")
    img.write_text_box((50, 50), title, box_width=900, font_filename=font_extra_bold, font_size=40, color=color)
    img.write_text_box((50, 90), sub_title, box_width=900, font_filename=font_light_italic, font_size=30, color=color)

    after_title_pos = 50 + 90 + 30
    if data:
        for idx, element in enumerate(data):
            draw_element(img, element, after_title_pos + 150 * idx)
            img.draw.line(
                ((50, after_title_pos + 150 * idx - 25), (950, after_title_pos + 150 * idx - 25)),
                fill=color, width=2
            )
    else:
        msg_no_elements = "На сегодня занятий нет"
        img.write_text_box((50, after_title_pos), msg_no_elements, box_width=900, font_filename=font_medium, font_size=25, color=color)

    return img


def draw_today_timetable_for(group: str) -> ImageText:
    week, day = datetime.datetime.now().isocalendar()[1] % 2 + 1, datetime.datetime.now().weekday() + 1
    return draw_timetable(group, week, day, False)
