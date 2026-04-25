from aiogram.fsm.state import State, StatesGroup


class DialogStates(StatesGroup):
    testing = State()
    consultation = State()
    awaiting_room_photo = State()
    awaiting_visual_intensity = State()
